# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class parisien(Variable):
    column = BoolCol
    entity_class = Familles
    label = u"Résidant à Paris au moins 3 ans dans les 5 dernières années"

class paris_base_ressources_commun_i(Variable):
        column = FloatCol
        label = u"Base de ressources individuelle"
        entity_class = Individus

        def function(self, simulation, period):
            period = period.this_month
            last_year = period.last_year

            salaire_net = simulation.calculate('salaire_net', period)
            indemnites_stage = simulation.calculate('indemnites_stage', period)
            smic = simulation.legislation_at(period.start).paris.smic_net_mensuel
            indemnites_stage_imposable = where((smic >= indemnites_stage), indemnites_stage, 0)
            revenus_stage_formation_pro = simulation.calculate('revenus_stage_formation_pro', period)

            chomage_net = simulation.calculate('chomage_net', period)
            allocation_securisation_professionnelle = simulation.calculate(
                'allocation_securisation_professionnelle', period)

            indemnites_journalieres = simulation.calculate('indemnites_journalieres', period)
            indemnites_chomage_partiel = simulation.calculate('indemnites_chomage_partiel', period)
            indemnites_volontariat = simulation.calculate('indemnites_volontariat', period)

            pensions_alimentaires_percues = simulation.calculate('pensions_alimentaires_percues', period)
            pensions_alimentaires_versees_individu = simulation.calculate(
                'pensions_alimentaires_versees_individu', period)
            prestation_compensatoire = simulation.calculate('prestation_compensatoire', period)
            retraite_nette = simulation.calculate('retraite_nette', period)
            pensions_invalidite = simulation.calculate('pensions_invalidite', period)

            def revenus_tns():
                revenus_auto_entrepreneur = simulation.calculate_add('tns_auto_entrepreneur_benefice', period)

                # Les revenus TNS hors AE sont estimés en se basant sur le revenu N-1
                tns_micro_entreprise_benefice = simulation.calculate('tns_micro_entreprise_benefice', last_year) / 12
                tns_benefice_exploitant_agricole = simulation.calculate('tns_benefice_exploitant_agricole', last_year) / 12
                tns_autres_revenus = simulation.calculate('tns_autres_revenus', last_year) / 12

                return revenus_auto_entrepreneur + tns_micro_entreprise_benefice + tns_benefice_exploitant_agricole + tns_autres_revenus

            result = (
                salaire_net + indemnites_chomage_partiel + chomage_net + retraite_nette +
                pensions_alimentaires_percues - abs_(pensions_alimentaires_versees_individu) +
                allocation_securisation_professionnelle + prestation_compensatoire +
                pensions_invalidite + revenus_tns() + revenus_stage_formation_pro +
                indemnites_stage_imposable + indemnites_journalieres + indemnites_volontariat
                )

            return period, result

class paris_base_ressources_commun(Variable):
    column = FloatCol
    label = u"Base de ressource"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month

        ass = simulation.calculate('ass', period)
        paris_base_ressources_i_holder = simulation.compute('paris_base_ressources_commun_i', period)
        paris_base_ressources = self.sum_by_entity(paris_base_ressources_i_holder)

        result = paris_base_ressources + ass

        return period, result

class paris_indemnite_enfant_i(Variable):
    column = FloatCol
    label = u"Indemnités de maternité, paternité, adoption"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        indemnites_maternite = simulation.calculate('indemnites_journalieres_maternite', period)
        indemnites_paternite = simulation.calculate('indemnites_journalieres_paternite', period)
        indemnites_adoption = simulation.calculate('indemnites_journalieres_adoption', period)

        result = indemnites_maternite + indemnites_paternite + indemnites_adoption

        return period, result

class paris_indemnite_enfant(Variable):
    column = FloatCol
    label = u"Base de ressources pour Indemnités de maternité, paternité, adoption"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month

        paris_indemnite_enfant_i = simulation.compute('paris_indemnite_enfant_i', period)
        paris_indemnite_enfant = self.sum_by_entity(paris_indemnite_enfant_i)

        return period, paris_indemnite_enfant

class paris_base_ressources_aah(Variable):
    column = FloatCol
    label = u"Le montant de l'AAH s'il y a plusieurs personnes handicapés dans la famille"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month

        aah = simulation.compute('aah', period)
        aah_famille = self.sum_by_entity(aah)

        return period, aah_famille

class paris_enfant_handicape(Variable):
    column = BoolCol
    label = u"Enfant handicapé au sens de la mairie de Paris"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        handicap = simulation.calculate('handicap', period)
        paris_enfant = simulation.calculate('paris_enfant', period)

        return period, paris_enfant * handicap

class paris_enfant(Variable):
    column = BoolCol
    label = u"Enfant pris en compte par la mairie de Paris"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        est_enfant_dans_famille = simulation.calculate('est_enfant_dans_famille', period)
        enfant_place = simulation.calculate('enfant_place', period)
        a_charge_fiscale = simulation.calculate('enfant_a_charge', period)

        return period, est_enfant_dans_famille * (1 - enfant_place) * a_charge_fiscale

class paris_enfant_garde_alternee(Variable):
    column = BoolCol
    label = u"Enfant en garde alternée pris en compte par la mairie de Paris"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        garde_alternee = simulation.calculate('garde_alternee', period)
        paris_enfant = simulation.calculate('paris_enfant', period)

        return period, garde_alternee * paris_enfant

class paris_enfant_handicape_garde_alternee(Variable):
    column = BoolCol
    label = u"Enfant handicapé en garde alternée pris en compte par la mairie de Paris"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        garde_alternee = simulation.calculate('garde_alternee', period)
        paris_enfant_handicape = simulation.calculate('paris_enfant_handicape', period)

        return period, garde_alternee * paris_enfant_handicape

class paris_personnes_agees(Variable):
    column = BoolCol
    label = u"Personne âgée"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        age_min = simulation.legislation_at(period.start).paris.age_pers_agee
        age = simulation.calculate('age', period)
        aspa_eligibilite = simulation.calculate('aspa_eligibilite', period)
        personne_agee = (age >= age_min) + (aspa_eligibilite)
        return period, personne_agee

class paris_personnes_handicap(Variable):
    column = BoolCol
    label = u"Personne qui a le statut Handicapé"
    entity_class = Individus

    def function(self, simulation, period):
        period = period.this_month

        age_min = simulation.legislation_at(period.start).paris.age_pers_inapte
        handicap = simulation.calculate('handicap', period)
        inapte_travail = simulation.calculate('inapte_travail', period)
        age = simulation.calculate('age', period)
        handicap = handicap + ((age < age_min) * inapte_travail)
        return period, handicap

class paris_nb_enfants(Variable):
    column = FloatCol
    label = u"Nombre d'enfant dans la famille"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month

        nb_enfants = simulation.compute('paris_enfant', period)
        paris_nb_enfants = self.sum_by_entity(nb_enfants)

        return period, paris_nb_enfants

class paris_condition_taux_effort(Variable):
    column = BoolCol
    label = u"condition du taux d'effort"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month

        taux_effort = simulation.legislation_at(period.start).paris.paris_logement.taux_effort
        loyer = simulation.calculate('loyer', period)
        apl = simulation.calculate('apl', period)

        ressources_mensuelles = simulation.calculate('paris_base_ressources_commun', period)
        charges_forfaitaire_logement = simulation.calculate('aide_logement_charges', period)
        calcul_taux_effort = (loyer + charges_forfaitaire_logement - apl) / ressources_mensuelles
        condition_loyer = calcul_taux_effort >= taux_effort
        return period, condition_loyer

class paris_loyer_net(Variable):
    column = FloatCol
    label = u"Charge nette de logement"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        loyer = simulation.calculate('loyer', period)
        aide_logement = simulation.calculate('aide_logement', period)
        aide_logement_dernier = simulation.calculate('aide_logement', last_month)
        charges_locatives = simulation.calculate('charges_locatives', period)

        montant_aide_logement = where(aide_logement_dernier > 0, aide_logement_dernier, aide_logement)

        result = loyer + charges_locatives - montant_aide_logement

        return period, result
