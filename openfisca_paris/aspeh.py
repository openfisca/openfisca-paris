# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Allocation de soutien aux parents d’enfants handicapés

class paris_logement_aspeh(Variable):
    value_type = float
    label = u"Le montant de l'Allocation de soutien aux parents d’enfants handicapés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        plafond_aspeh = legislation(period).paris.aspeh.plafond_aspeh
        aide_aspeh = legislation(period).paris.aspeh.aide_aspeh

        parisien = famille('parisien', period)

        enfant_handicape = famille.members('paris_enfant_handicape', period)
        nb_enfant = famille.sum(enfant_handicape)

        paris_base_ressources_commun = famille('paris_base_ressources_commun', last_month)
        clca = famille('paje_clca', last_month)

        ressources_mensuelles_famille = paris_base_ressources_commun + clca

        result = select([ressources_mensuelles_famille <= plafond_aspeh],
            [aide_aspeh]) * parisien
        return result * nb_enfant
