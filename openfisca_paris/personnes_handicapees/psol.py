# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_solidarite_ph_base_ressources(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Base ressources mensuelles pour Paris Solidarité pour les personnes handicapées"
    reference = "article III.1.1.b.4 du règlement municipal du CASVP"

    def formula(famille, period, parameters):

        base_ressource = famille('paris_base_ressources_couple', period)
        
        aspa_montant_maximum_annuel = parameters(period).prestations_sociales.solidarite_insertion.minimum_vieillesse.aspa.montant_maximum_annuel
        aah = parameters(period).prestations_sociales.prestations_etat_de_sante.invalidite.aah
        en_couple = famille('en_couple', period)
        # ASPA est utilisé comme seuil de ressources pour
        # les couples avec personne en situation de handicap
        # faute d'AAH pour couple
        montant_psol_handicap = ((en_couple * aspa_montant_maximum_annuel.couples) / 12 + not_(en_couple) * aah.montant)

        return max_(montant_psol_handicap, base_ressource)


class paris_solidarite_ph_eligibilite(Variable):
    value_type = bool
    entity = Famille
    definition_period = MONTH
    label = u"Éligibilité à Paris Solidarité pour les personnes handicapées"
    
    def formula(famille, period, parameters):

        personnes_handicapees = famille.members('paris_personne_handicapee', period)
        return famille.any(personnes_handicapees, role = Famille.PARENT)


class paris_solidarite_ph_montant(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Montant mensuel pour Paris Solidarité pour les personnes handicapées"
    reference = "article III.1.1.b.3 du règlement municipal du CASVP"

    def formula(famille, period, parameters):

        base_ressource = famille('paris_solidarite_ph_base_ressources', period)
        plafond_psol = parameters(period).paris.personnes_handicapees.psol.plafond

        en_couple = famille('en_couple', period)
        plafond = (en_couple * plafond_psol.couple + not_(en_couple) * plafond_psol.personne_seule)

        return max_(0, plafond - base_ressource)


class paris_solidarite_ph(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Paris Solidarité pour les personnes handicapées"
    
    def formula(famille, period, parameters):

        montant = famille('paris_solidarite_ph_montant', period)
        ph_eligibilite = famille('paris_solidarite_ph_eligibilite', period)
        
        return ph_eligibilite * montant
