# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)
from math import ceil

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_logement_pa_plafond(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Plafond de ressources pour l'éligibilité à l'aide Paris Logement pour les personnes âgées"
	reference = "article II.2.1.b/2 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		salaire_minimum = parameters(period).marche_travail.salaire_minimum.smic
		smic_brut_mensuel = salaire_minimum.smic_b_horaire * salaire_minimum.nb_heures_travail_mensuel

		# Utilisation des valeurs indicatives de service-public.fr pour passer du SMIC brut au SMIC net
		# https://www.service-public.fr/particuliers/vosdroits/F2300
		# Dans l'attente de la formule effectivement utilisée par la ville de Paris
		smic_net_mensuel = 7.94 / 10.03 * smic_brut_mensuel
		smic_arrondi = ceil(smic_net_mensuel / 10) * 10	# arrondi à la dizaine supérieure

		nb_enfants = famille('paris_nb_enfants', period)

		plafond_avec_enfant = parameters(period).paris.personnes_agees.paris_logement.plafond.avec_enfant

		return where(nb_enfants < 1, smic_arrondi, plafond_avec_enfant)


class paris_logement_pa_eligibilite(Variable):
	value_type = bool
	entity = Famille
	definition_period = MONTH
	label = u"Éligibilité à l'aide Paris Logement pour les personnes âgées"
	reference = "article II.2.1.b du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		pa_ph_eligibilite = famille('paris_logement_pa_ph_eligibilite', period)

		personnes_agees_i = famille.members('paris_personne_agee', period)
		personnes_agees = famille.any(personnes_agees_i)

		base_ressources = famille('paris_base_ressources_foyer', period.last_month)
		plafond = famille('paris_logement_pa_plafond', period)

		return pa_ph_eligibilite * personnes_agees * (base_ressources <= plafond)


class paris_logement_pa_montant(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Montant de l'aide Paris Logement pour les personnes âgées"
	reference = "article II.2.1.a du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		en_couple = famille('en_couple', period)
		nb_enfants = famille('paris_nb_enfants', period)
		param_montant = parameters(period).paris.personnes_agees.paris_logement.montant

		montant = select(
				[not_(en_couple), nb_enfants < 1, nb_enfants >=1],
				[param_montant.personne_isolee, param_montant.couple_sans_enfant, param_montant.couple_avec_enfant]
			)
		charge_logement = famille('paris_logement_charge_nette_mensuelle', period)

		return min_(montant, charge_logement)


class paris_logement_pa(Variable):
	value_type = float
	entity = Famille
	definition_period = MONTH
	label = u"Paris Logement pour les personnes âgées"
	reference = "article II.2.1 du règlement municipal du CASVP"

	def formula(famille, period, parameters):
		eligibilite = famille('paris_logement_pa_eligibilite', period)
		montant = famille('paris_logement_pa_montant', period)
		return eligibilite * montant
