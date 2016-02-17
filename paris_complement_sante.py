# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_complement_sante(Variable):
    column = FloatCol
    label = u"L'aide Complémentaire Santé Paris"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        P = simulation.legislation_at(period.start)
        plafond_pers_isol_cs = P.paris.complement_sante.plafond_pers_isol_cs
        plafond_couple_cs = P.paris.complement_sante.plafond_couple_cs
        montant_aide_cs = P.paris.complement_sante.montant_aide_cs

        parisien = simulation.calculate('parisien', period)
        personnes_agees_i = simulation.compute('paris_personnes_agees', period)
        personnes_agees = self.any_by_roles(personnes_agees_i)
        personnes_handicape_i = simulation.compute('paris_personnes_handicap', period)
        personnes_handicap = self.any_by_roles(personnes_handicape_i)
        concub = simulation.calculate('concub', period)
        cmu_c = simulation.calculate('cmu_c', period)
        aspa = simulation.calculate('aspa', last_month)
        ass = simulation.calculate('ass', last_month)
        asi = simulation.calculate('asi', last_month)
        aide_logement = simulation.calculate('aide_logement', last_month)
        ressources_i = simulation.compute('paris_complement_sante_i', last_month)
        acs_montant = simulation.calculate('acs_montant', period)
        acs_plafond = simulation.calculate('acs_plafond', period)
        ressources = self.split_by_roles(ressources_i, roles = [CHEF, PART])

        ressources_pers_isol = ressources[CHEF] + aspa + ass + asi + aide_logement

        ressources_couple = ressources[CHEF] + ressources[PART]

        ressources_couple += aspa + ass + asi + aide_logement

        plafond = where(concub, plafond_couple_cs, plafond_pers_isol_cs)

        acs_isole = (ressources_pers_isol <= (acs_plafond / 12)) * acs_montant
        acs_couple = (ressources_couple <= (acs_plafond / 12)) * acs_montant

        montant_pers_handicap = where(parisien * personnes_handicap * (concub != 1) *
            (ressources_pers_isol <= plafond) * (montant_aide_cs >= acs_isole) * (cmu_c != 1),
            montant_aide_cs - acs_isole, 0)

        montant_couple = where(parisien * concub * (personnes_handicap + personnes_agees) *
         (ressources_couple <= plafond) * (montant_aide_cs >= acs_couple) *
         (acs_couple > 0) * (cmu_c != 1), montant_aide_cs - acs_couple, 0)

        montant_couple_ss_acs = where(parisien * concub * (personnes_handicap + personnes_agees) *
            (acs_couple == 0) * (cmu_c != 1) * (ressources_couple <= plafond), montant_aide_cs, 0)

        return period, montant_pers_handicap + montant_couple + montant_couple_ss_acs

class paris_complement_sante_i(Variable):
    column = FloatCol
    label = u"Ressources Individuelles"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        paris_base_ressources_commun_i = simulation.calculate('paris_base_ressources_commun_i', last_month)
        aah = simulation.calculate('aah', last_month)

        ressources_demandeur = paris_base_ressources_commun_i + aah

        return period, ressources_demandeur
