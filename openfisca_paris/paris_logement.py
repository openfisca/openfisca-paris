# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris Logement pour les personnes agées et les personnes handicapées

class paris_logement(Variable):
    value_type = float
    label = u"L'aide Paris Logement"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        paris_logement_pa_ph = famille('paris_logement_pa_ph', period)
        paris_logement_fam = famille('paris_logement_fam', period)
        paris_logement_apd = famille('paris_logement_apd', period)

        return paris_logement_pa_ph + paris_logement_fam + paris_logement_apd

class paris_logement_pa_ph(Variable):
    value_type = float
    label = u"Paris Logement pour les personnes handicapées et les personnes agées"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        plafond_pl = legislation(period).paris.paris_logement.plafond_pl
        plafond_pl_avec_enf = legislation(period).paris.paris_logement.plafond_pl_avec_enf
        aide_pers_isol = legislation(period).paris.paris_logement.aide_pers_isol
        aide_couple_ss_enf = legislation(period).paris.paris_logement.aide_couple_ss_enf
        aide_couple_avec_enf = legislation(period).paris.paris_logement.aide_couple_avec_enf

        paris_base_ressources_commun = famille('paris_base_ressources_commun', last_month)
        aspa = famille('aspa', last_month)
        asi = famille.sum(famille.members('asi', last_month))
        aah = famille('paris_base_ressources_aah', last_month)
        aide_logement = famille('aide_logement', last_month)
        loyer_net = famille('paris_loyer_net', period)
        ressources_familiale = paris_base_ressources_commun + aspa + asi + aah + aide_logement

        personnes_couple = famille('en_couple', period)
        nb_enfants = famille('paris_nb_enfants', period)
        paris_logement_elig_pa_ph = famille('paris_logement_elig_pa_ph', period)

        plafond = select([(nb_enfants >= 1), (nb_enfants < 1)], [plafond_pl_avec_enf, plafond_pl])
        condition_ressource = ressources_familiale <= plafond
        montant_aide = select([personnes_couple * (nb_enfants > 0), personnes_couple,
            ((personnes_couple != 1) * (nb_enfants == 0)), ((personnes_couple != 1) * (nb_enfants >= 1))],
            [aide_couple_avec_enf, aide_couple_ss_enf, aide_pers_isol, 0])

        result_montant = where((montant_aide > loyer_net), (montant_aide - (montant_aide - loyer_net)), montant_aide)

        result = where(result_montant > 0, result_montant, 0)

        return result * condition_ressource * paris_logement_elig_pa_ph

class paris_logement_elig_pa_ph(Variable):
    value_type = bool
    label = u"Personne qui est eligible pour l'aide PL pour les personnes agées et les personne handicapées"
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

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        statut_occupation_elig = (
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer)
        )
        charges_logement = famille('paris_condition_taux_effort', period)

        adulte_handicape = (personne_handicap - nb_enfant) >= 1

        result = parisien * statut_occupation_elig * (personnes_agees_famille + adulte_handicape) * charges_logement
        return result

class paris_logement_fam(Variable):
    value_type = float
    label = u"Paris Logement pour les couples avec enfant(s)"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        plafond_pl_fam = legislation(period).paris.paris_logement.plafond_pl_fam
        aide_pl_fam = legislation(period).paris.paris_logement.aide_pl_fam

        paris_base_ressources_commun = famille('paris_base_ressources_commun', last_month)
        rsa = famille('rsa', last_month)
        aah = famille('paris_base_ressources_aah', last_month)
        aide_logement = famille('aide_logement', last_month)
        loyer_net = famille('paris_loyer_net', period)
        ressources_familiale = paris_base_ressources_commun + rsa + aah + aide_logement

        personnes_couple = famille('en_couple', period)
        nb_enfants = famille('paris_nb_enfants', period)
        paris_logement_elig_fam = famille('paris_logement_elig_fam', period)

        condition_ressource = ressources_familiale <= plafond_pl_fam

        montant_aide = where(personnes_couple * (nb_enfants > 0), aide_pl_fam, 0)

        result = where((montant_aide > loyer_net), (montant_aide - (montant_aide - loyer_net)), montant_aide)

        return result * condition_ressource * paris_logement_elig_fam

class paris_logement_elig_fam(Variable):
    value_type = bool
    label = u"Personne qui est eligible pour l'aide Paris Logement quand c'est un couple avec enfant(s)"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)

        personnes_agees = famille.members('paris_personnes_agees', period)
        personnes_agees_famille = famille.any(personnes_agees)

        personne_handicap = famille.members('paris_personnes_handicap', period)
        personne_handicap_famille = famille.any(personne_handicap)

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        statut_occupation_elig = (
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer)
        )
        charges_logement = famille('paris_condition_taux_effort', period)
        result = parisien * statut_occupation_elig * (personnes_agees_famille != 1) * (personne_handicap_famille != 1) * charges_logement
        return result

class paris_logement_apd(Variable):
    value_type = float
    label = u"Paris Logement pour les personnes isolées et couples sans enfant"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        plafond = legislation(period).paris.paris_logement.plafond_pl_apd
        aide_pl_apd_pers_isol = legislation(period).paris.paris_logement.aide_pl_apd_pers_isol
        aide_pl_apd_couple = legislation(period).paris.paris_logement.aide_pl_apd_couple

        paris_base_ressources_commun = famille('paris_base_ressources_commun', last_month)

        rsa = famille('rsa', last_month)
        indemnite = famille('paris_indemnite_enfant', last_month)
        aah = famille('paris_base_ressources_aah', last_month)
        aide_logement = famille('aide_logement', last_month)
        loyer_net = famille('paris_loyer_net', period)
        ressources_familiale = paris_base_ressources_commun + aah + aide_logement + rsa - indemnite

        personnes_couple = famille('en_couple', period)
        paris_logement_elig_apd = famille('paris_logement_elig_apd', period)

        condition_ressource = ressources_familiale <= plafond

        montant_aide = where(personnes_couple, aide_pl_apd_couple, aide_pl_apd_pers_isol)

        result = where((montant_aide > loyer_net), (montant_aide - (montant_aide - loyer_net)), montant_aide)

        return result * condition_ressource * paris_logement_elig_apd

class paris_logement_elig_apd(Variable):
    value_type = bool
    label = u"Personne qui est eligible pour l'aide Paris Logement aide aux parisiens en difficultés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)

        personnes_agees = famille.members('paris_personnes_agees', period)
        personnes_agees_famille = famille.any(personnes_agees)

        personne_handicap = famille.members('paris_personnes_handicap', period)
        personne_handicap_famille = famille.any(personne_handicap)

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        loyer = famille.demandeur.menage('loyer', period)
        nb_enfants = famille('paris_nb_enfants', period)

        statut_occupation_elig = (
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer)
        )
        charges_logement = famille('paris_condition_taux_effort', period)

        result = parisien * statut_occupation_elig * (personnes_agees_famille != 1) * (personne_handicap_famille != 1) * charges_logement * (loyer > 0) * (nb_enfants == 0)

        return result
