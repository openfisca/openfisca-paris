# -*- coding: utf-8 -*-
from __future__ import division
from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)
from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_navigo_amethyste_eligibilite_personnelle(Variable):
    value_type = bool
    label = u"Éligibité des personnes au Pass Navigo Améthyste de Paris"
    entity = Individu
    definition_period = MONTH
    reference = "Articles II.3.1.b et III.3.1.b du règlement municipal du CASVP"

    def formula(individu, period):
        return individu.famille('parisien', period) * (
            + individu('paris_personnes_agees', period)
            + individu('paris_personnes_handicap', period)
            )


class paris_navigo_amethyste_eligibilite_financiere(Variable):
    value_type = bool
    label = u"Éligibilité financière au Pass Navigo Améthyste de Paris"
    entity = FoyerFiscal
    definition_period = MONTH
    reference = "Articles II.3.1.b.1 et III.3.1.b.1 du règlement municipal du CASVP"

    def formula(foyer_fiscal, period, parameters):
        nam = parameters(period).paris.navigo_amethyste
        base_ressource = foyer_fiscal('ir_ss_qf', period.n_2)
        base_ressource_precedente = foyer_fiscal('ir_ss_qf', period.n_2.last_year)

        elig = base_ressource <= nam.imposition_maximale
        elig_renouvellement = (base_ressource <= nam.imposition_maximale_en_renouvellement) * (base_ressource_precedente <= nam.imposition_maximale)
        return elig + elig_renouvellement


class paris_navigo_amethyste(Variable):
    value_type = bool
    label = u"Éligibilité au Pass Navigo Améthyste de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):
        eligibilite_personnelle = individu('paris_navigo_amethyste_eligibilite_personnelle', period)
        eligibilite_financiere = individu.foyer_fiscal('paris_navigo_amethyste_eligibilite_financiere', period)
        return eligibilite_personnelle * eligibilite_financiere
