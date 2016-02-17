# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_energie_famille_elig(Variable):
    column = BoolCol
    label = u"Eligibilité à Paris Energie Famille"
    entity_class = Familles

    def function(self, simulation, period):
        parisien = simulation.calculate('parisien', period)
        statut_occupation = simulation.calculate('statut_occupation_famille', period)
        charge_logement = (
            (statut_occupation == 1) +
            (statut_occupation == 2) +
            (statut_occupation == 3) +
            (statut_occupation == 4) +
            (statut_occupation == 5) +
            (statut_occupation == 7)
            )

        result = parisien * charge_logement

        return period, result

class paris_energie_famille(Variable):
    column = FloatCol
    label = u"L'aide Paris Energie Famille"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        premier_plafond_pef = simulation.legislation_at(period.start).paris.pef.premier_plafond_pef
        deuxieme_plafond_pef = simulation.legislation_at(period.start).paris.pef.deuxieme_plafond_pef
        troisieme_plafond_pef = simulation.legislation_at(period.start).paris.pef.troisieme_plafond_pef
        aide_1er_plafond_pef = simulation.legislation_at(period.start).paris.pef.aide_1er_plafond_pef
        aide_2eme_plafond_pef = simulation.legislation_at(period.start).paris.pef.aide_2eme_plafond_pef
        aide_3eme_plafond_pef = simulation.legislation_at(period.start).paris.pef.aide_3eme_plafond_pef

        elig = simulation.calculate('paris_energie_famille_elig', period)
        nb_enfant = simulation.calculate('paris_nb_enfants', period)
        enfant_handicape = simulation.calculate('paris_enfant_handicape', period)
        nb_enfant_handicape = self.sum_by_entity(enfant_handicape)
        ressources_familliales = simulation.calculate('paris_base_ressources_commun', last_month)

        result = select([(nb_enfant == 1) * (ressources_familliales <= premier_plafond_pef),
            (nb_enfant == 2) * (ressources_familliales <= deuxieme_plafond_pef),
            ((nb_enfant >= 3) + (nb_enfant_handicape >= 1)) * (ressources_familliales <= troisieme_plafond_pef)],
            [aide_1er_plafond_pef, aide_2eme_plafond_pef, aide_3eme_plafond_pef]) * elig

        return period, result
