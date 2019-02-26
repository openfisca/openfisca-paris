# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_complement_sante_pa_base_ressources(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Base ressources mensuelles pour le Complément Santé Paris pour les personnes âgées"
	reference = "article II.1.2.b.3 du règlement municipal du CASVP"

	def formula(famille, period, parameters):

		# TODO: Calculer cette base ressource proprement dans paris.py ou paris_complement_sante.py par exemple ?
		# "Toutes les ressources du demandeur, et, le cas échéant de son conjoint, de son partenaire civil de solidarité ou de la
		# personne avec laquelle il déclare être en situation de vie maritale, sont prises en compte à l’exclusion de celles mentionnées dans les
		# dispositions générales."
		# _base_ressources = famille('paris_base_ressources_commun', period) << probablement à utiliser
		return famille('paris_logement_psol_base_ressources', period)		


class paris_complement_sante_pa_eligibilite(Variable):
	value_type = bool
	entity = Famille
	definition_period = MONTH
	label = u"Éligibilité au Complément Santé Paris pour les personnes âgées"
	reference = "article II.1.2.b.3 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		base_ressources = famille('paris_complement_sante_pa_base_ressources', period)
		_plafond = parameters(period).paris.personnes_agees.paris_complement_sante.plafond
		en_couple = famille('en_couple', period)
		plafond = _plafond.en_couple if en_couple else _plafond.personne_isolee

		# TODO: Prendre en compte les dispositions particulières
		# article II.1.2.d
		return base_ressources <= plafond


class paris_complement_sante_pa_montant(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Montant du Complément Santé Paris pour les personnes âgées"
	reference = "articles II.1.2.a.2 & II.1.2.b.6 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		montant = parameters(period).paris.personnes_agees.paris_complement_sante.montant

		# TODO: Clarifier la signification de "cumul" avec la CMU-C
		# "Le Complément Santé Paris n’est cumulable avec la Couverture Maladie Universelle Complémentaire ou l’Aide à la
		# Complémentaire Santé que dans la limite du plafond fixé par le Conseil de Paris et précisé en annexe II 1.2. a.2"
		# cmu_c = famille('cmu_c', period)
		acs = famille('acs', period)

		return montant - acs


class paris_complement_sante_pa(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Complément Santé Paris pour les personnes âgées"
	reference = "article II.1.2 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		eligibilite = famille('paris_complement_sante_pa_eligibilite', period)
		montant = famille('paris_complement_sante_pa_montant', period)
		return eligibilite * montant
