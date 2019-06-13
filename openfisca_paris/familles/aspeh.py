# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Allocation de soutien aux parents d’enfants handicapés

class paris_logement_aspeh_base_ressources(Variable):
    value_type = float
    label = u"Base ressources pour l'Allocation de soutien aux parents d’enfants handicapés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        base_ressources = famille('paris_base_ressources_couple', period.last_month)
        clca = famille('paje_clca', period.last_month)
        return base_ressources + clca


class paris_logement_aspeh(Variable):
    value_type = float
    label = u"Le montant de l'Allocation de soutien aux parents d’enfants handicapés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        plafond_aspeh = legislation(period).paris.familles.aspeh.plafond_aspeh
        montant = legislation(period).paris.familles.aspeh.aide_aspeh

        parisien = famille('parisien', period)
        nb_enfant_handicape = famille('paris_nb_enfants_handicapes', period)
        ressources = famille('paris_logement_aspeh_base_ressources', period)

        return parisien * (ressources <= plafond_aspeh) * nb_enfant_handicape * montant
