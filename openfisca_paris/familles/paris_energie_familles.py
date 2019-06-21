# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_energie_familles_eligibilite_simple(Variable):
    value_type = bool
    label = u"Eligibilité à l'aide Paris Energie Familles, sans prendre en compte les conditions financières"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        participation_frais = famille.demandeur.menage('participation_frais', period)
        logement_a_charge = (
            famille('paris_logement_a_charge', period) +
            ((statut_occupation_logement == TypesStatutOccupationLogement.loge_gratuitement) * participation_frais)
            )

        return parisien * logement_a_charge


class paris_energie_familles_eligibilite_financiere(Variable):
    value_type = bool
    label = u"Eligibilité financière à l'aide Paris Energie Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        plafond = legislation(period).paris.familles.paris_energie_familles.plafond
        base_ressources = famille('paris_base_ressources_couple', period.last_month)

        nb_enfants = famille('paris_nb_enfants', period)
        nb_enfants_handicapes = famille('paris_nb_enfants_handicapes', period)

        return select(
            [(nb_enfants >= 3) + (nb_enfants_handicapes >= 1), nb_enfants == 2, nb_enfants == 1],
            [base_ressources <= plafond.trois_enfants, base_ressources <= plafond.deux_enfants, base_ressources <= plafond.un_enfant]
            )


class paris_energie_familles_montant(Variable):
    value_type = float
    label = u"Montant de l'aide Paris Energie Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        montant = legislation(period).paris.familles.paris_energie_familles.montant

        nb_enfants = famille('paris_nb_enfants', period)
        nb_enfants_handicapes = famille('paris_nb_enfants_handicapes', period)

        return select(
            [(nb_enfants >= 3) + (nb_enfants_handicapes >=1), (nb_enfants == 1) + (nb_enfants == 2)],
            [montant.trois_enfants, montant.un_ou_deux_enfants]
            )


class paris_energie_familles(Variable):
    value_type = float
    label = u"L'aide Paris Energie Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        eligibilite_simple = famille('paris_energie_familles_eligibilite_simple', period)
        eligibilite_financiere = famille('paris_energie_familles_eligibilite_financiere', period)
        montant = famille('paris_energie_familles_montant', period)

        return eligibilite_simple * eligibilite_financiere * montant
