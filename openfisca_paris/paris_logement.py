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

        base_ressources = famille('paris_base_ressources_foyer', last_month)
        loyer_net = famille('paris_logement_charge_nette_mensuelle', period)

        personnes_couple = famille('en_couple', period)
        nb_enfants = famille('paris_nb_enfants', period)
        paris_logement_ph_eligibilite = famille('paris_logement_ph_eligibilite', period)

        plafond = select([(nb_enfants >= 1), (nb_enfants < 1)], [plafond_pl_avec_enf, plafond_pl])
        condition_ressource = base_ressources <= plafond
        montant_aide = select([personnes_couple * (nb_enfants > 0), personnes_couple,
            ((personnes_couple != 1) * (nb_enfants == 0)), ((personnes_couple != 1) * (nb_enfants >= 1))],
            [aide_couple_avec_enf, aide_couple_ss_enf, aide_pers_isol, 0])

        result_montant = where((montant_aide > loyer_net), (montant_aide - (montant_aide - loyer_net)), montant_aide)

        result = where(result_montant > 0, result_montant, 0)

        paris_logement_pa = famille('paris_logement_pa', period)
        return max_(result * condition_ressource * paris_logement_ph_eligibilite, paris_logement_pa)


class paris_logement_pa_ph_eligibilite(Variable):
    value_type = bool
    label = u"Eligibilité à l'aide Paris Logement pour les personnes agées et les personne handicapées"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        locataire = famille('paris_locataire', period)
        condition_taux_effort = famille('paris_condition_taux_effort', period)
        nb_enfants = famille('paris_nb_enfants', period)

        return parisien * locataire * condition_taux_effort * (nb_enfants <= 1)


class paris_logement_ph_eligibilite(Variable):
    value_type = bool
    label = u"Personne qui est eligible pour l'aide PL pour les personne handicapées"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        locataire = famille('paris_locataire', period)
        condition_taux_effort = famille('paris_condition_taux_effort', period)

        personne_handicap_individu = famille.members('paris_personne_handicapee', period)
        personne_handicap = famille.sum(personne_handicap_individu)
        nb_enfants_handicapes = famille('paris_nb_enfants_handicapes', period)
        adulte_handicape = (personne_handicap - nb_enfants_handicapes) >= 1

        return parisien * locataire * condition_taux_effort * adulte_handicape

class paris_logement_fam(Variable):
    value_type = float
    label = u"Paris Logement pour les couples avec enfant(s)"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        plafond_pl_fam = legislation(period).paris.paris_logement.plafond_pl_fam
        aide_pl_fam = legislation(period).paris.paris_logement.aide_pl_fam

        base_ressources = famille('paris_base_ressources_foyer', last_month)
        loyer_net = famille('paris_logement_charge_nette_mensuelle', period)

        personnes_couple = famille('en_couple', period)
        nb_enfants = famille('paris_nb_enfants', period)
        paris_logement_elig_fam = famille('paris_logement_elig_fam', period)

        condition_ressource = base_ressources <= plafond_pl_fam

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

        personnes_agees = famille.members('paris_personne_agee', period)
        personnes_agees_famille = famille.any(personnes_agees)

        personne_handicap = famille.members('paris_personne_handicapee', period)
        personne_handicap_famille = famille.any(personne_handicap)

        locataire = famille('paris_locataire', period)
        condition_taux_effort = famille('paris_condition_taux_effort', period)

        return parisien * locataire * (personnes_agees_famille != 1) * (personne_handicap_famille != 1) * condition_taux_effort

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

        base_ressources = famille('paris_base_ressources_foyer', last_month)

        indemnite = famille('paris_indemnite_enfant', last_month)
        loyer_net = famille('paris_logement_charge_nette_mensuelle', period)

        personnes_couple = famille('en_couple', period)
        paris_logement_elig_apd = famille('paris_logement_elig_apd', period)

        condition_ressources = (base_ressources - indemnite) <= plafond

        montant_aide = where(personnes_couple, aide_pl_apd_couple, aide_pl_apd_pers_isol)

        result = where((montant_aide > loyer_net), (montant_aide - (montant_aide - loyer_net)), montant_aide)

        return result * condition_ressources * paris_logement_elig_apd


class paris_logement_elig_apd(Variable):
    value_type = bool
    label = u"Personne qui est eligible pour l'aide Paris Logement aide aux parisiens en difficultés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        
        locataire = famille('paris_locataire', period)

        personnes_agees = famille.members('paris_personne_agee', period)
        personnes_agees_famille = famille.any(personnes_agees)

        personne_handicap = famille.members('paris_personne_handicapee', period)
        personne_handicap_famille = famille.any(personne_handicap)

        condition_taux_effort = famille('paris_condition_taux_effort', period)

        etudiant_ok = famille('paris_logement_elig_apd_etudiant', period)
        
        loyer = famille.demandeur.menage('loyer', period)

        nb_enfants = famille('paris_nb_enfants', period)

        return parisien * locataire * etudiant_ok * (personnes_agees_famille != 1) * (personne_handicap_famille != 1) * condition_taux_effort * (loyer > 0) * (nb_enfants == 0)


class paris_logement_elig_apd_etudiant(Variable):
    value_type = bool
    label = u"Évaluation de l'éligibilité des étudiants à Paris Logement aide aux parisiens en difficultés"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        etudiant_i = famille.members('etudiant', period)
        etudiant = famille.any(etudiant_i)

        boursier_i = famille.members('boursier', period)
        boursier = famille.any(boursier_i)

        return not_(etudiant) + (etudiant * boursier)


class paris_logement_charge_nette_mensuelle(Variable):
    value_type = float
    label = u"Charge nette de logement pour les locataires"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        loyer = famille.demandeur.menage('loyer', period)
        charges_locatives = famille.demandeur.menage('charges_locatives', period)
        aide_logement = famille('aide_logement', period)

        return max_(0, loyer + charges_locatives - aide_logement)
