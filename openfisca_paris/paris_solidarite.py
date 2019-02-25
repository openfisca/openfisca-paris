# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris solidarité pour les personnes agées et les personnes handicapées

class paris_logement_psol(Variable):
    value_type = float
    label = u"Montant de l'aide Paris Solidarité"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        parisien = famille('parisien', period)

        personne_handicap_individu = famille.members('paris_personnes_handicap', period)
        personne_handicap = famille.sum(personne_handicap_individu)

        enfant_handicape = famille.members('paris_enfant_handicape', period)
        nb_enfant = famille.sum(enfant_handicape)
        montant_aide = famille('paris_logement_psol_montant', period)

        adulte_handicape = (personne_handicap - nb_enfant) >= 1

        psol_agregee = adulte_handicape * montant_aide
        psol_pa = famille('paris_solidarite_pa', period)

        result = parisien * max_(psol_agregee, psol_pa)

        return result


class paris_logement_psol_base_ressources(Variable):
    value_type = float
    label = u"Base ressources mensuelle pour PSOL"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        paris_base_ressources_commun = famille('paris_base_ressources_commun', period)
        aspa = famille('aspa', period)
        asi = famille.sum(famille.members('asi', period))
        aah = famille('paris_base_ressources_aah', period)
        caah = famille.sum(famille.members('caah', period))

        return paris_base_ressources_commun + asi + aspa + aah + caah


class paris_logement_psol_montant_max(Variable):
    value_type = float
    label = u"Montant de l'aide PSOL"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        montant_aide_seul_ph = legislation(period).paris.paris_solidarite.montant_ph
        montant_aide_couple = legislation(period).paris.paris_solidarite.montant_couple

        personnes_couple = famille('en_couple', period)

        personne_handicap_individu = famille.members('paris_personnes_handicap', period)
        nb_personne_handicap = famille.sum(personne_handicap_individu)
        ressources_conjoint = famille.conjoint('paris_base_ressources_commun_i', last_month)

        return select(
            [
                (personnes_couple) * ((nb_personne_handicap == 0) + (nb_personne_handicap == 1) * (ressources_conjoint == 0)),
                not_(personnes_couple) * (nb_personne_handicap == 1)
            ],
            [montant_aide_couple, montant_aide_seul_ph])


class paris_logement_psol_montant(Variable):
    value_type = float
    label = u"Montant de l'aide PSOL"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        plafond_couple_psol = legislation(period).paris.paris_solidarite.plafond_couple_psol
        plafond_seul_psol_personne_handicap = legislation(period).paris.paris_solidarite.plafond_seul_psol_personne_handicap
        montant_aide_seul_ph = legislation(period).paris.paris_solidarite.montant_ph
        montant_aide_couple = legislation(period).paris.paris_solidarite.montant_couple

        personnes_couple = famille('en_couple', period)

        personne_handicap_individu = famille.members('paris_personnes_handicap', period)
        nb_personne_handicap = famille.sum(personne_handicap_individu)
        ressources_conjoint = famille.conjoint('paris_base_ressources_commun_i', period)

        ressources_mensuelles = famille('paris_logement_psol_base_ressources', period)

        plafond_psol = select(
            [personnes_couple, nb_personne_handicap == 1],
            [plafond_couple_psol, plafond_seul_psol_personne_handicap]
        )

        montant_aide  = plafond_psol - ressources_mensuelles

        montant_max = famille('paris_logement_psol_montant_max', period)

        return max_(0, min_(montant_aide, montant_max))
