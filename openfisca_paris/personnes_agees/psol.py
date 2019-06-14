# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_solidarite_pa_base_ressources(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Base ressources mensuelles pour Paris Solidarité pour les personnes âgées"
    reference = "article II.1.1.b.4 du règlement municipal du CASVP"

    def formula(famille, period, parameters):
        
        base_ressources = famille('paris_base_ressources_couple', period)
        aspa_reference = famille('paris_aspa_reference', period)

        return max_(aspa_reference, base_ressources)


class paris_solidarite_pa_montant(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Montant mensuel pour Paris Solidarité pour les personnes âgées"
    reference = "article II.1.1.b.3 du règlement municipal du CASVP"

    def formula(famille, period, parameters):

        base_ressources = famille('paris_solidarite_pa_base_ressources', period)
        plafond_psol = parameters(period).paris.personnes_agees.psol.plafond

        en_couple = famille('en_couple', period)
        plafond = (en_couple * plafond_psol.couple + not_(en_couple) * plafond_psol.personne_seule)

        return max_(0, plafond - base_ressources)


class paris_solidarite_pa_eligibilite(Variable):
    value_type = bool
    entity = Famille
    definition_period = MONTH
    label = u"Éligibilité à Paris Solidarité pour les personnes âgées"
    
    def formula(famille, period, parameters):

        personnes_agees_i = famille.members('paris_personne_agee', period)
        return famille.any(personnes_agees_i)


class paris_solidarite_pa(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Paris Solidarité pour les personnes âgées"
    
    def formula(famille, period, parameters):

        montant = famille('paris_solidarite_pa_montant', period)
        pa_eligibilite = famille('paris_solidarite_pa_eligibilite', period)
        
        return pa_eligibilite * montant
