# -*- coding: utf-8 -*-
from __future__ import division

from numpy import absolute as abs_, minimum as min_, maximum as max_, where

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_logement_familles_elig(Variable):
    value_type = bool
    label = u"Eligibilité à Paris-Logement-Famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        charge_logement = (
            (statut_occupation_logement == TypesStatutOccupationLogement.primo_accedant) +
            (statut_occupation_logement == TypesStatutOccupationLogement.proprietaire) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer)
            )

        result = parisien * charge_logement

        return result


class plf_handicap(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = u"Allocation Paris-Logement-Famille en cas d'enfant handicapé"

    def formula(famille, period, legislation):
        last_month = period.last_month

        br = famille('paris_base_ressources_commun', last_month)
        P = legislation(period).paris.paris_logement_familles
        plafond_plfm = legislation(period).paris.plfm.deuxieme_plafond_plfm
        personnes_couple = famille('en_couple', period)

        parent_mono_plfm = (personnes_couple != 1) * (br > plafond_plfm)

        nb_enfant = famille('paris_nb_enfants', period)

        paris_enfant_handicape = famille.members('paris_enfant_handicape', period)
        nb_enf_handicape = famille.sum(paris_enfant_handicape)

        paris_enfant_handicape_garde_alternee = famille.members('paris_enfant_handicape_garde_alternee', period)
        nb_enf_handicape_garde_alternee = famille.sum(paris_enfant_handicape_garde_alternee)

        plafond = legislation(period).paris.paris_logement_familles.plafond_haut_3enf
        montant = legislation(period).paris.paris_logement_familles.montant_haut_3enf

        plf_handicap = ((nb_enf_handicape > 0) * (br <= plafond) * montant) * (personnes_couple + parent_mono_plfm)

        # Si tous les enfants handicapés sont en garde alternée
        garde_alternee = (nb_enf_handicape - nb_enf_handicape_garde_alternee) == 0
        deduction_garde_alternee = garde_alternee * 0.5 * plf_handicap

        # S'il a plus de 3 enfants
        supa3_enfant = where(nb_enfant > 3, nb_enfant - 3, 0)
        suppl_enfant = where(supa3_enfant > 0, P.montant_haut_enf_sup * supa3_enfant, 0)

        plf_handicap = plf_handicap + suppl_enfant

        plf_handicap = plf_handicap - deduction_garde_alternee
        return plf_handicap

class paris_logement_familles(Variable):
    value_type = float
    label = u"Allocation Paris Logement Famille"
    entity = Famille
    definition_period = MONTH
    reference = "http://www.paris.fr/pratique/toutes-les-aides-et-allocations/aides-sociales/paris-logement-familles-prestation-ville-de-paris/rub_9737_stand_88805_port_24193"  # noqa

    def formula(famille, period, legislation):
        last_month = period.last_month

        elig = famille('paris_logement_familles_elig', period)
        br = famille('paris_base_ressources_commun', last_month)
        personnes_couple = famille('en_couple', period)
        paris_enfant = famille.members('paris_enfant', period)
        nbenf = famille.sum(paris_enfant)
        paris_enfant_garde_alternee = famille.members('paris_enfant_garde_alternee', period)
        nbenf_garde_alternee = famille.sum(paris_enfant_garde_alternee)
        plf_handicap = famille('plf_handicap', period)
        menage = famille.demandeur.menage
        loyer = menage('loyer', period) + menage('charges_locatives', period)
        loyer_net = famille('paris_loyer_net', period)
        P = legislation(period).paris.paris_logement_familles
        plafond_plfm = legislation(period).paris.plfm.deuxieme_plafond_plfm

        parent_mono_plfm = (personnes_couple != 1) * ((nbenf >= 4) + ((nbenf >= 2) * (br > plafond_plfm)))

        ressources_sous_plaf_bas = (br <= P.plafond_bas_3enf)
        ressources_sous_plaf_haut = (br <= P.plafond_haut_3enf) * (br > P.plafond_bas_3enf)

        montant_base_3enfs = (nbenf >= 3) * (
            ressources_sous_plaf_bas * P.montant_haut_3enf +
            ressources_sous_plaf_haut * P.montant_bas_3enf
            )
        montant_enf_sup = (
            ressources_sous_plaf_bas * P.montant_haut_enf_sup +
            ressources_sous_plaf_haut * P.montant_bas_enf_sup
            )
        montant_3enfs = (montant_base_3enfs + montant_enf_sup * max_(nbenf - 3, 0)) * (personnes_couple + parent_mono_plfm)
        montant_2enfs = ((nbenf == 2) * (br <= P.plafond_2enf) * P.montant_2enf) * (personnes_couple + parent_mono_plfm)
        plf = montant_2enfs + montant_3enfs
        deduction_garde_alternee = (nbenf_garde_alternee > 0) * (
            (nbenf - nbenf_garde_alternee < 3) * 0.5 * plf +
            (nbenf - nbenf_garde_alternee >= 3) * nbenf_garde_alternee * 0.5 * montant_enf_sup
            )

        plf = plf - deduction_garde_alternee
        plf = max_(plf, plf_handicap)
        plf = elig * plf
        plf = min_(plf, loyer)

        result_montant = where((plf > loyer_net), (plf - (plf - loyer_net)), plf)

        result = where(result_montant > 0, result_montant, 0)

        return result
