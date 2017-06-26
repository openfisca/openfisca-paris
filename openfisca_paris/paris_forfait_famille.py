# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris forfait familles
class paris_forfait_famille_elig(Variable):
    column = BoolCol
    label = u"Eligibilité à Paris Forfait Famille"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):
        parisien = famille('parisien', period)
        statut_occupation_logement = famille.demandeur.menage('statut_occupation_logement', period)
        charge_logement = (
            (statut_occupation_logement == 1) +
            (statut_occupation_logement == 2) +
            (statut_occupation_logement == 3) +
            (statut_occupation_logement == 4) +
            (statut_occupation_logement == 5) +
            (statut_occupation_logement == 7)
            )

        result = parisien * charge_logement

        return result

class paris_forfait_famille(Variable):
    column = FloatCol
    label = u"Famille qui est eligible à l'aide paris forfait famille "
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        premier_plafond = legislation(period).paris.paris_forfait_famille.premier_plafond
        deuxieme_plafond = legislation(period).paris.paris_forfait_famille.deuxieme_plafond
        aide_1er_plafond = legislation(period).paris.paris_forfait_famille.aide_1er_plafond
        aide_2eme_plafond = legislation(period).paris.paris_forfait_famille.aide_2eme_plafond

        nb_enfants = famille('paris_nb_enfants', period)
        elig = famille('paris_forfait_famille_elig', period)
        ressources_mensuelles_famille = famille('paris_base_ressources_commun', last_month)
        montant_aide = select([(ressources_mensuelles_famille <= premier_plafond),
            (ressources_mensuelles_famille <= deuxieme_plafond)], [aide_1er_plafond, aide_2eme_plafond])
        result = (select([(nb_enfants >= 3), (nb_enfants < 3)], [montant_aide, 0])) * elig
        return result
