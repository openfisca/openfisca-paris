# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_forfait_familles_eligibilite(Variable):
    value_type = bool
    label = u"Eligibilité à l'aide Paris Forfait Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        parisien = famille('parisien', period)
        logement_a_charge = famille('paris_logement_a_charge', period)
        nb_enfants = famille('paris_nb_enfants', period)

        return parisien * logement_a_charge * (nb_enfants >= 3)


class paris_forfait_familles_montant(Variable):
    value_type = float
    label = u"Montant de l'aide Paris Forfait Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        
        param = legislation(period).paris.familles.paris_forfait_familles
        base_ressources = famille('paris_base_ressources_couple', period.last_month)

        return select(
            [base_ressources <= param.plafond.premier, base_ressources <= param.plafond.deuxieme, base_ressources > param.plafond.deuxieme],
            [param.montant.premier_plafond, param.montant.deuxieme_plafond, 0]
            )


class paris_forfait_familles(Variable):
    value_type = float
    label = u"Aide Paris Forfait Familles"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        eligibilite = famille('paris_forfait_familles_eligibilite', period)
        montant = famille('paris_forfait_familles_montant', period)

        return eligibilite * montant
