# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_forfait_famille_eligibilite(Variable):
    value_type = bool
    label = u"Eligibilité à l'aide Paris Forfait Famille"
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

class paris_forfait_famille(Variable):
    value_type = float
    label = u"Aide Paris Forfait Famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        premier_plafond = legislation(period).paris.familles.paris_forfait_famille.premier_plafond
        deuxieme_plafond = legislation(period).paris.familles.paris_forfait_famille.deuxieme_plafond
        aide_1er_plafond = legislation(period).paris.familles.paris_forfait_famille.aide_1er_plafond
        aide_2eme_plafond = legislation(period).paris.familles.paris_forfait_famille.aide_2eme_plafond

        nb_enfants = famille('paris_nb_enfants', period)
        elig = famille('paris_forfait_famille_eligibilite', period)
        ressources_mensuelles_famille = famille('paris_base_ressources_couple', last_month)
        montant_aide = select([(ressources_mensuelles_famille <= premier_plafond),
            (ressources_mensuelles_famille <= deuxieme_plafond)], [aide_1er_plafond, aide_2eme_plafond])
        result = (select([(nb_enfants >= 3), (nb_enfants < 3)], [montant_aide, 0])) * elig
        return result
