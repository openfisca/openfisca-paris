# -*- coding: utf-8 -*-
from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_pass_eligibilite_financiere(Variable):
    value_type = bool
    label = u"Éligibilité financière au Pass Paris Senior ou Pass Paris Access'"
    entity = FoyerFiscal
    definition_period = MONTH
    reference = "Articles II.3.1.b.1 et III.3.1.b.1 du règlement municipal du CASVP"

    def formula(foyer_fiscal, period, parameters):

        paris_pass = parameters(period).paris.paris_pass
        base_ressources = foyer_fiscal('ir_ss_qf', period.n_2)
        base_ressources_precedente = foyer_fiscal('ir_ss_qf', period.n_2.last_year)

        elig = base_ressources <= paris_pass.imposition_maximale
        elig_renouvellement = (base_ressources <= paris_pass.imposition_maximale_en_renouvellement) * (base_ressources_precedente <= paris_pass.imposition_maximale)

        return elig + elig_renouvellement


class paris_pass_eligibilite(Variable):
    value_type = bool
    label = u"Éligibilité au Pass Paris Senior ou Pass Paris Access'"
    entity = Individu
    definition_period = MONTH
    reference = "Articles II.3.1.b.1 et III.3.1.b.1 du règlement municipal du CASVP"

    def formula(individu, period):

        parisien = individu.famille('parisien', period)
        eligibilite_logement = individu.menage('statut_occupation_logement', period) != TypesStatutOccupationLogement.sans_domicile
        eligibilite_financiere = individu.foyer_fiscal('paris_pass_eligibilite_financiere', period)

        return parisien * eligibilite_logement * eligibilite_financiere

