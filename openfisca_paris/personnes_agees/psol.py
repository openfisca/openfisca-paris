# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_solidarite_pa_base_ressources_initiale(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Base ressources mensuelles pour Paris Solidarité pour les personnes âgées"
    reference = "article II.1.1.b.4 du règlement municipal du CASVP"


class paris_solidarite_pa_base_ressources(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Base ressources mensuelles pour Paris Solidarité pour les personnes âgées"
    reference = "article II.1.1.b.4 du règlement municipal du CASVP"

    def formula(famille, period, parameters):

        base_ressource = famille('paris_solidarite_pa_base_ressources_initiale', period)
        aspa  = parameters(period).prestations.minima_sociaux.aspa

        en_couple = famille('en_couple', period)
        minimum_vieillesse = (en_couple * aspa.montant_annuel_couple + not_(en_couple) * aspa.montant_annuel_seul) / 12

        return max_(minimum_vieillesse, base_ressource)


class paris_solidarite_pa_montant(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Montant mensuel pour Paris Solidarité pour les personnes âgées"
    reference = "article II.1.1.b.3 du règlement municipal du CASVP"

    def formula(famille, period, parameters):

        base_ressource = famille('paris_solidarite_pa_base_ressources', period)
        plafond_psol = parameters(period).paris.personnes_agees.psol.plafond


        en_couple = famille('en_couple', period)
        plafond = (en_couple * plafond_psol.couple + not_(en_couple) * plafond_psol.personne_seule)

        return max_(0, plafond - base_ressource)
