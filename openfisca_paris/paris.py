# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (full_like as fl_, inf, divide as div_, maximum as max_, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class parisien(Variable):
    value_type = bool
    entity = Famille
    definition_period = MONTH
    label = u"Résident à Paris au moins 3 ans dans les 5 dernières années"

class paris_base_ressources_i(Variable):
    value_type = float
    label = u"Base de ressources pour un individu, pour l'ensemble des aides de Paris"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period, legislation):
        last_year = period.last_year

        ass = individu('ass', period)
        aah = individu('aah', period)
        asi = individu('asi', period)
        caah = individu('caah', period)

        salaire_net = individu('salaire_net', period)
        indemnites_stage = individu('indemnites_stage', period)
        smic = legislation(period).paris.smic_net_mensuel
        indemnites_stage_imposable = where((smic >= indemnites_stage), indemnites_stage, 0)
        revenus_stage_formation_pro = individu('revenus_stage_formation_pro', period)

        chomage_net = individu('chomage_net', period)
        allocation_securisation_professionnelle = individu('allocation_securisation_professionnelle', period)
        indemnites_journalieres = individu('indemnites_journalieres', period)
        indemnites_chomage_partiel = individu('indemnites_chomage_partiel', period)
        indemnites_volontariat = individu('indemnites_volontariat', period)

        prestation_compensatoire = individu('prestation_compensatoire', period)
        retraite_nette = individu('retraite_nette', period)
        pensions_invalidite = individu('pensions_invalidite', period)

        def revenus_tns():
            revenus_auto_entrepreneur = individu('rpns_auto_entrepreneur_benefice', period, options = [ADD])

            # Les revenus TNS hors AE sont estimés en se basant sur le revenu N-1
            tns_micro_entreprise_benefice = individu('rpns_micro_entreprise_benefice', last_year) / 12
            tns_benefice_exploitant_agricole = individu('rpns_benefice_exploitant_agricole', last_year) / 12
            tns_autres_revenus = individu('rpns_autres_revenus', last_year) / 12

            return revenus_auto_entrepreneur + tns_micro_entreprise_benefice + tns_benefice_exploitant_agricole + tns_autres_revenus

        result = (
            ass + aah + asi + caah
            + salaire_net + indemnites_stage_imposable + revenus_stage_formation_pro
            + chomage_net + allocation_securisation_professionnelle + indemnites_journalieres + indemnites_chomage_partiel + indemnites_volontariat
            + prestation_compensatoire + retraite_nette + pensions_invalidite
            + revenus_tns()
            )

        return result

class paris_base_ressources_famille(Variable):
    value_type = float
    label = u"Base de ressources liée à une famille (à ajouter aux ressources des individus), pour l'ensemble des aides de Paris"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        aeeh = famille('aeeh', period)
        aspa = famille('aspa', period)
        rsa = famille('rsa', period)
        return aeeh + aspa + rsa

class paris_base_ressources_couple(Variable):
    value_type = float
    label = u"Base de ressources pour un couple, pour l'ensemble des aides de Paris"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        en_couple = famille('en_couple', period)
        ressources_demandeur = famille.demandeur('paris_base_ressources_i', period)
        ressources_conjoint = famille.conjoint('paris_base_ressources_i', period)
        ressources_famille = famille('paris_base_ressources_famille', period)

        return where(en_couple,
            ressources_demandeur + ressources_conjoint + ressources_famille,
            ressources_demandeur + ressources_famille)

class paris_base_ressources_foyer(Variable):
    value_type = float
    label = u"Base de ressources pour un foyer, pour l'ensemble des aides de Paris"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        ressources = famille.members('paris_base_ressources_i', period)
        ressources_famille = famille('paris_base_ressources_famille', period)

        return famille.sum(ressources) + ressources_famille

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


class paris_nb_enfants(Variable):
    value_type = float
    label = u"Nombre d'enfant dans la famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        nb_enfants = famille.members('paris_enfant', period)
        paris_nb_enfants = famille.sum(nb_enfants)

        return paris_nb_enfants


class paris_nb_enfants_handicapes(Variable):
    value_type = float
    label = u"Nombre d'enfants handicapés dans la famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        nb_enfants = famille.members('paris_enfant_handicape', period)
        return famille.sum(nb_enfants)


class paris_taux_effort(Variable):
    value_type = float
    label = u"Taux d'effort pour le loyer"
    entity = Famille
    definition_period = MONTH
    reference = "Articles II.2.1.b.3 et III.2.1.b.3 et IV.2.3.b.3 et V.3.1.b.3 du Règlement Municipal"

    def formula(famille, period, legislation):

        loyer = famille.demandeur.menage('loyer', period)
        charges_forfaitaires_logement = famille('aide_logement_charges', period)
        aide_logement = famille('aide_logement', period)

        base_ressources = famille('paris_base_ressources_foyer', period.last_month)
        aspa_reference = famille('paris_aspa_reference', period)
        ressources = max_(aspa_reference, base_ressources)

        # Utiliser si les ressources sont à 0
        ressources_inf = fl_(ressources, inf)

        return div_(
            (loyer + charges_forfaitaires_logement - aide_logement),
            ressources,
            out=ressources_inf,
            where=ressources != 0
        )

class paris_condition_taux_effort(Variable):
    value_type = bool
    label = u"Condition vérifiant si le taux d'effort est suffisamment élevé"
    entity = Famille
    definition_period = MONTH
    reference = "Articles II.2.1.b.3 et III.2.1.b.3 et IV.2.3.b.3 et V.3.1.b.3 du Règlement Municipal"

    def formula(famille, period, legislation):

        taux_effort = famille('paris_taux_effort', period)
        taux_effort_min = legislation(period).paris.paris_logement.taux_effort_min

        return taux_effort >= taux_effort_min


class paris_locataire(Variable):
    value_type = bool
    label = u"Famille qui est locataire de son logement"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)

        return (
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer)
            )

class paris_logement_a_charge(Variable):
    value_type = bool
    label = u"Famille qui acquitte ses charges de logement"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        locataire = famille('paris_locataire', period)

        return (
            locataire +
            (statut_occupation_logement == TypesStatutOccupationLogement.primo_accedant) +
            (statut_occupation_logement == TypesStatutOccupationLogement.proprietaire)
            )
