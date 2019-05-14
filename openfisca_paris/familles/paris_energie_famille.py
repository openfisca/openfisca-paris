# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

class paris_energie_famille_elig(Variable):
    value_type = bool
    label = u"Eligibilité à Paris Energie Famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        participation_frais = famille.demandeur.menage('participation_frais', period)
        charge_logement = (
            (statut_occupation_logement == TypesStatutOccupationLogement.primo_accedant) +
            (statut_occupation_logement == TypesStatutOccupationLogement.proprietaire) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_hlm) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_vide) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_meuble) +
            (statut_occupation_logement == TypesStatutOccupationLogement.locataire_foyer) +
            ((statut_occupation_logement == TypesStatutOccupationLogement.loge_gratuitement) 
              * participation_frais  )
            )

        result = parisien * charge_logement

        return result

class paris_energie_famille(Variable):
    value_type = float
    label = u"L'aide Paris Energie Famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        premier_plafond_pef = legislation(period).paris.pef.premier_plafond_pef
        deuxieme_plafond_pef = legislation(period).paris.pef.deuxieme_plafond_pef
        troisieme_plafond_pef = legislation(period).paris.pef.troisieme_plafond_pef
        aide_1er_plafond_pef = legislation(period).paris.pef.aide_1er_plafond_pef
        aide_2eme_plafond_pef = legislation(period).paris.pef.aide_2eme_plafond_pef
        aide_3eme_plafond_pef = legislation(period).paris.pef.aide_3eme_plafond_pef

        elig = famille('paris_energie_famille_elig', period)
        nb_enfant = famille('paris_nb_enfants', period)
        nb_enfants_handicapes = famille('paris_nb_enfants_handicapes', period)
        ressources_familliales = famille('paris_base_ressources_couple', last_month)

        result = select([((nb_enfant == 1) * (nb_enfants_handicapes == 0)) * (ressources_familliales <= premier_plafond_pef),
            ((nb_enfant == 2) * (nb_enfants_handicapes == 0)) * (ressources_familliales <= deuxieme_plafond_pef),
            ((nb_enfant >= 3) + (nb_enfants_handicapes >= 1)) * (ressources_familliales <= troisieme_plafond_pef)],
            [aide_1er_plafond_pef, aide_2eme_plafond_pef, aide_3eme_plafond_pef]) * elig

        return result
