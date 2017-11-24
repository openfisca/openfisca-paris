# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class parisien(Variable):
    value_type = bool
    entity = Famille
    definition_period = MONTH
    label = u"Résidant à Paris au moins 3 ans dans les 5 dernières années"

class paris_base_ressources_commun_i(Variable):
    value_type = float
    label = u"Base de ressources individuelle"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, legislation):
        last_year = period.last_year

        salaire_net = individu('salaire_net', period)
        indemnites_stage = individu('indemnites_stage', period)
        smic = legislation(period).paris.smic_net_mensuel
        indemnites_stage_imposable = where((smic >= indemnites_stage), indemnites_stage, 0)
        revenus_stage_formation_pro = individu('revenus_stage_formation_pro', period)

        chomage_net = individu('chomage_net', period)
        allocation_securisation_professionnelle = individu(
            'allocation_securisation_professionnelle', period)

        indemnites_journalieres = individu('indemnites_journalieres', period)
        indemnites_chomage_partiel = individu('indemnites_chomage_partiel', period)
        indemnites_volontariat = individu('indemnites_volontariat', period)

        pensions_alimentaires_percues = individu('pensions_alimentaires_percues', period)
        pensions_alimentaires_versees_individu = individu(
            'pensions_alimentaires_versees_individu', period)
        prestation_compensatoire = individu('prestation_compensatoire', period)
        retraite_nette = individu('retraite_nette', period)
        pensions_invalidite = individu('pensions_invalidite', period)

        def revenus_tns():
            revenus_auto_entrepreneur = individu('tns_auto_entrepreneur_benefice', period, options = [ADD])

            # Les revenus TNS hors AE sont estimés en se basant sur le revenu N-1
            tns_micro_entreprise_benefice = individu('tns_micro_entreprise_benefice', last_year) / 12
            tns_benefice_exploitant_agricole = individu('tns_benefice_exploitant_agricole', last_year) / 12
            tns_autres_revenus = individu('tns_autres_revenus', last_year) / 12

            return revenus_auto_entrepreneur + tns_micro_entreprise_benefice + tns_benefice_exploitant_agricole + tns_autres_revenus

        result = (
            salaire_net + indemnites_chomage_partiel + chomage_net + retraite_nette +
            pensions_alimentaires_percues - abs_(pensions_alimentaires_versees_individu) +
            allocation_securisation_professionnelle + prestation_compensatoire +
            pensions_invalidite + revenus_tns() + revenus_stage_formation_pro +
            indemnites_stage_imposable + indemnites_journalieres + indemnites_volontariat
            )

        return result

class paris_base_ressources_commun(Variable):
    value_type = float
    label = u"Base de ressource"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        ass = famille('ass', period)
        paris_base_ressources_i = famille.members('paris_base_ressources_commun_i', period)
        paris_base_ressources = famille.sum(paris_base_ressources_i)

        result = paris_base_ressources + ass

        return result

class paris_indemnite_enfant_i(Variable):
    value_type = float
    label = u"Indemnités de maternité, paternité, adoption"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        indemnites_maternite = individu('indemnites_journalieres_maternite', period)
        indemnites_paternite = individu('indemnites_journalieres_paternite', period)
        indemnites_adoption = individu('indemnites_journalieres_adoption', period)

        result = indemnites_maternite + indemnites_paternite + indemnites_adoption

        return result

class paris_indemnite_enfant(Variable):
    value_type = float
    label = u"Base de ressources pour Indemnités de maternité, paternité, adoption"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        paris_indemnite_enfant_i = famille.members('paris_indemnite_enfant_i', period)
        paris_indemnite_enfant = famille.sum(paris_indemnite_enfant_i)

        return paris_indemnite_enfant

class paris_base_ressources_aah(Variable):
    value_type = float
    label = u"Le montant de l'AAH s'il y a plusieurs personnes handicapés dans la famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        aah = famille.members('aah', period)
        aah_famille = famille.sum(aah)

        return aah_famille

class paris_enfant_handicape(Variable):
    value_type = bool
    label = u"Enfant handicapé au sens de la mairie de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        handicap = individu('handicap', period)
        paris_enfant = individu('paris_enfant', period)

        return paris_enfant * handicap

class paris_enfant(Variable):
    value_type = bool
    label = u"Enfant pris en compte par la mairie de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        est_enfant_dans_famille = individu('est_enfant_dans_famille', period)
        enfant_place = individu('enfant_place', period)
        a_charge_fiscale = individu('enfant_a_charge', period.this_year)

        return est_enfant_dans_famille * (1 - enfant_place) * a_charge_fiscale

class paris_enfant_garde_alternee(Variable):
    value_type = bool
    label = u"Enfant en garde alternée pris en compte par la mairie de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        garde_alternee = individu('garde_alternee', period)
        paris_enfant = individu('paris_enfant', period)

        return garde_alternee * paris_enfant

class paris_enfant_handicape_garde_alternee(Variable):
    value_type = bool
    label = u"Enfant handicapé en garde alternée pris en compte par la mairie de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        garde_alternee = individu('garde_alternee', period)
        paris_enfant_handicape = individu('paris_enfant_handicape', period)

        return garde_alternee * paris_enfant_handicape

class paris_personnes_agees(Variable):
    value_type = bool
    label = u"Personne âgée"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, legislation):

        age_min = legislation(period).paris.age_pers_agee
        age = individu('age', period)
        aspa_eligibilite = individu('aspa_eligibilite', period)
        personne_agee = (age >= age_min) + (aspa_eligibilite)
        return personne_agee

class paris_personnes_handicap(Variable):
    value_type = bool
    label = u"Personne qui a le statut Handicapé"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, legislation):

        age_min = legislation(period).paris.age_pers_inapte
        handicap = individu('handicap', period)
        inapte_travail = individu('inapte_travail', period)
        age = individu('age', period)
        handicap = handicap + ((age < age_min) * inapte_travail)
        return handicap

class paris_nb_enfants(Variable):
    value_type = float
    label = u"Nombre d'enfant dans la famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        nb_enfants = famille.members('paris_enfant', period)
        paris_nb_enfants = famille.sum(nb_enfants)

        return paris_nb_enfants

class paris_condition_taux_effort(Variable):
    value_type = bool
    label = u"condition du taux d'effort"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        taux_effort = legislation(period).paris.paris_logement.taux_effort
        loyer = famille.demandeur.menage('loyer', period)
        aide_logement = famille('aide_logement', period)

        ressources_mensuelles = famille('paris_base_ressources_commun', period)
        charges_forfaitaire_logement = famille('aide_logement_charges', period)
        calcul_taux_effort = (loyer + charges_forfaitaire_logement - aide_logement) / ressources_mensuelles
        condition_loyer = calcul_taux_effort >= taux_effort
        return condition_loyer

class paris_loyer_net(Variable):
    value_type = float
    label = u"Charge nette de logement"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        last_month = period.last_month

        aide_logement = famille('aide_logement', period)
        aide_logement_dernier = famille('aide_logement', last_month)
        loyer = famille.demandeur.menage('loyer', period)
        charges_locatives = famille.demandeur.menage('charges_locatives', period)

        montant_aide_logement = where(aide_logement_dernier > 0, aide_logement_dernier, aide_logement)

        result = loyer + charges_locatives - montant_aide_logement

        return result
