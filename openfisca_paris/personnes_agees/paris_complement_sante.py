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
		# base_ressources = famille('paris_base_ressources_commun', period) << probablement à utiliser

		last_month = period.last_month
		aspa = famille('aspa', last_month)
		asi = famille.sum(famille.members('asi', last_month))
		# TODO: Enlever l'ass, qui est déjà compté dans les ressources de base individuelles (paris_base_ressources_commun_i)
		ass = famille.sum(famille.members('ass', last_month))
		# TODO: Enlever les aides au logement (cf. dispositions générales)
		aide_logement = famille('aide_logement', last_month)
		aides_famille = aspa + asi + ass + aide_logement

		en_couple = famille('en_couple', period)
		ressources_demandeur = famille.demandeur('paris_complement_sante_i', last_month)
		ressources_conjoint = famille.conjoint('paris_complement_sante_i', last_month)

		ressources_pers_isol = ressources_demandeur + aides_famille
		ressources_couple = ressources_demandeur + ressources_conjoint + aides_famille

		return where(en_couple, ressources_couple, ressources_pers_isol)


class paris_complement_sante_pa_eligibilite(Variable):
	value_type = bool
	entity = Famille
	definition_period = MONTH
	label = u"Éligibilité au Complément Santé Paris pour les personnes âgées"
	reference = "article II.1.2.b.3 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		# TODO: Prendre en compte la parisianité quelque part pour toutes les aides Openfisca Paris
		# is_parisien = famille('parisien', period)
		
		personnes_agees_i = famille.members('paris_personnes_agees', period)
		personnes_agees = famille.any(personnes_agees_i)

		base_ressources = famille('paris_complement_sante_pa_base_ressources', period)
		param_plafond = parameters(period).paris.personnes_agees.paris_complement_sante.plafond
		en_couple = famille('en_couple', period)
		plafond = where(en_couple, param_plafond.en_couple, param_plafond.personne_isolee)

		return personnes_agees * (base_ressources <= plafond)


class paris_complement_sante_pa_montant(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Montant du Complément Santé Paris pour les personnes âgées"
	reference = "articles II.1.2.a.2 & II.1.2.b.6 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		montant = parameters(period).paris.personnes_agees.paris_complement_sante.montant
		acs = famille('acs', period)
		cmu_c = famille('cmu_c', period)

		return not_(cmu_c) * max_(montant - acs, 0)


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
