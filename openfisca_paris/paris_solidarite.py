# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris solidarité pour les personnes agées et les personnes handicapées

class paris_logement_psol(Variable):
    column = FloatCol
    label = u"Montant de l'aide Paris Solidarité"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        parisien = famille('parisien', period)

        personnes_agees = famille.members('paris_personnes_agees', period)
        personnes_agees_famille = famille.any(personnes_agees)

        personne_handicap_individu = famille.members('paris_personnes_handicap', period)
        personne_handicap = famille.sum(personne_handicap_individu)

        enfant_handicape = famille.members('paris_enfant_handicape', period)
        nb_enfant = famille.sum(enfant_handicape)
        montant_aide = famille('paris_logement_psol_montant', period)

        adulte_handicape = (personne_handicap - nb_enfant) >= 1

        result = parisien * (personnes_agees_famille + adulte_handicape) * montant_aide

        return result

class paris_logement_psol_montant(Variable):
    column = FloatCol
    label = u"Montant de l'aide PSOL"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        montant_seul_annuel = legislation(period).prestations.minima_sociaux.aspa.montant_annuel_seul
        montant_couple_annuel = legislation(period).prestations.minima_sociaux.aspa.montant_annuel_couple
        plafond_seul_psol = legislation(period).paris.paris_solidarite.plafond_seul_psol
        plafond_couple_psol = legislation(period).paris.paris_solidarite.plafond_couple_psol

        montant_seul = montant_seul_annuel / 12
        montant_couple = montant_couple_annuel / 12
        personnes_couple = famille('en_couple', period)
        paris_base_ressources_commun = famille('paris_base_ressources_commun', last_month)
        aspa = famille('aspa', last_month)
        asi = famille('asi', last_month)
        aah = famille('paris_base_ressources_aah', last_month)

        ressources_mensuelles = paris_base_ressources_commun + asi + aspa + aah

        plafond_psol = select([personnes_couple, (personnes_couple != 1)], [plafond_couple_psol, plafond_seul_psol])

        plancher_ressources = where(personnes_couple, montant_couple, montant_seul)
        ressources_mensuelles_min = where(ressources_mensuelles < plancher_ressources, plancher_ressources,
            ressources_mensuelles)

        result = select([((personnes_couple != 1) * (ressources_mensuelles_min <= plafond_psol)),
            personnes_couple * (ressources_mensuelles_min <= plafond_psol),
            ((personnes_couple != 1) + personnes_couple) * (ressources_mensuelles_min > plafond_psol)],
            [(plafond_seul_psol - ressources_mensuelles_min), (plafond_couple_psol - ressources_mensuelles_min), 0])

        return result
