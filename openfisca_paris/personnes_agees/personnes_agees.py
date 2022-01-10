# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_personne_agee(Variable):
    value_type = bool
    label = u"Personne âgée"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, legislation):

        param_age = legislation(period).paris.personnes_agees.personnes_agees

        age = individu('age', period)
        inapte = individu('inapte_travail', period)

        aspa_eligibilite = individu('aspa_eligibilite', period)

        return (age >= param_age.age_min) + (inapte * (age >= param_age.age_min_si_inaptitude)) + aspa_eligibilite


class paris_aspa_reference(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Minimum vieillesse à l'échelon national pour les personnes âgées"

    def formula(famille, period, parameters):

        personne_agee = famille.members('paris_personne_agee', period)
        personnes_agees_famille = famille.any(personne_agee)
        en_couple = famille('en_couple', period)
        aspa_montant_maximum_annuel = parameters(period).prestations_sociales.solidarite_insertion.minimum_vieillesse.aspa.montant_maximum_annuel

        
        return personnes_agees_famille * (en_couple * aspa_montant_maximum_annuel.couples + not_(en_couple) * aspa_montant_maximum_annuel.personnes_seules) / 12
