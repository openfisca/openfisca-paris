# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Allocation de soutien aux parents d’enfants handicapés

class paris_logement_aspeh(Variable):
    column = FloatCol
    label = u"Le montant de l'Allocation de soutien aux parents d’enfants handicapés"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        plafond_aspeh = simulation.legislation_at(period.start).paris.aspeh.plafond_aspeh
        aide_aspeh = simulation.legislation_at(period.start).paris.aspeh.aide_aspeh

        parisien = simulation.calculate('parisien', period)
        enfant_handicape = simulation.calculate('paris_enfant_handicape', period)
        nb_enfant = self.sum_by_entity(enfant_handicape)
        paris_base_ressources_commun = simulation.calculate('paris_base_ressources_commun', last_month)
        clca = simulation.calculate('paje_clca', last_month)

        ressources_mensuelles_famille = paris_base_ressources_commun + clca

        result = select([ressources_mensuelles_famille <= plafond_aspeh],
            [aide_aspeh]) * parisien
        return period, result * nb_enfant
