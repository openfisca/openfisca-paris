# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_complement_sante(Variable):
    value_type = float
    label = u"L'aide Complémentaire Santé Paris"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        P = legislation(period)
        plafond_pers_isol_cs = P.paris.complement_sante.plafond_pers_isol_cs
        plafond_couple_cs = P.paris.complement_sante.plafond_couple_cs
        montant_aide_cs = P.paris.complement_sante.montant_aide_cs

        parisien = famille('parisien', period)
        personnes_agees_i = famille.members('paris_personnes_agees', period)
        personnes_agees = famille.any(personnes_agees_i)
        personnes_handicape_i = famille.members('paris_personnes_handicap', period)
        personnes_handicap = famille.any(personnes_handicape_i)
        en_couple = famille('en_couple', period)
        cmu_c = famille('cmu_c', period)
        aspa = famille('aspa', last_month)
        ass = famille('ass', last_month)
        asi = famille.sum(famille.members('asi', last_month))
        aide_logement = famille('aide_logement', last_month)
        acs_montant = famille('acs_montant', period)
        acs_plafond = famille('acs_plafond', period)

        ressources_demandeur = famille.demandeur('paris_complement_sante_i', last_month)
        ressources_conjoint = famille.conjoint('paris_complement_sante_i', last_month)

        ressources_pers_isol = ressources_demandeur + aspa + ass + asi + aide_logement

        ressources_couple = ressources_demandeur + ressources_conjoint

        ressources_couple += aspa + ass + asi + aide_logement

        plafond = where(en_couple, plafond_couple_cs, plafond_pers_isol_cs)

        acs_isole = (ressources_pers_isol <= (acs_plafond / 12)) * acs_montant
        acs_couple = (ressources_couple <= (acs_plafond / 12)) * acs_montant

        montant_pers_handicap = where(parisien * personnes_handicap * (en_couple != 1) *
            (ressources_pers_isol <= plafond) * (montant_aide_cs >= acs_isole) * (cmu_c != 1),
            montant_aide_cs - acs_isole, 0)

        montant_couple = where(parisien * en_couple * (personnes_handicap + personnes_agees) *
         (ressources_couple <= plafond) * (montant_aide_cs >= acs_couple) *
         (acs_couple > 0) * (cmu_c != 1), montant_aide_cs - acs_couple, 0)

        montant_couple_ss_acs = where(parisien * en_couple * (personnes_handicap + personnes_agees) *
            (acs_couple == 0) * (cmu_c != 1) * (ressources_couple <= plafond), montant_aide_cs, 0)

        return montant_pers_handicap + montant_couple + montant_couple_ss_acs

class paris_complement_sante_i(Variable):
    value_type = float
    label = u"Ressources Individuelles"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):
        last_month = period.last_month

        paris_base_ressources_commun_i = individu('paris_base_ressources_commun_i', last_month)
        aah = individu('aah', last_month)

        ressources_demandeur = paris_base_ressources_commun_i + aah

        return ressources_demandeur
