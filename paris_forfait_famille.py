# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris forfait familles
class paris_forfait_famille_elig(Variable):
    column = BoolCol
    label = u"Eligibilité à Paris Forfait Familles"
    entity_class = Familles

    def function(self, simulation, period):
        parisien = simulation.calculate('parisien', period)
        statut_occupation = simulation.calculate('statut_occupation_famille', period)
        charge_logement = (
            (statut_occupation == 1) +
            (statut_occupation == 2) +
            (statut_occupation == 3) +
            (statut_occupation == 4) +
            (statut_occupation == 5) +
            (statut_occupation == 7)
            )

        result = parisien * charge_logement

        return period, result

class paris_forfait_famille(Variable):
    column = FloatCol
    label = u"Famille qui est eligible à l'aide paris forfait famille "
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        premier_plafond = simulation.legislation_at(period.start).paris.paris_forfait_famille.premier_plafond
        deuxieme_plafond = simulation.legislation_at(period.start).paris.paris_forfait_famille.deuxieme_plafond
        aide_1er_plafond = simulation.legislation_at(period.start).paris.paris_forfait_famille.aide_1er_plafond
        aide_2eme_plafond = simulation.legislation_at(period.start).paris.paris_forfait_famille.aide_2eme_plafond

        nb_enfants = simulation.calculate('paris_nb_enfants', period)
        elig = simulation.calculate('paris_forfait_famille_elig', period)
        ressources_mensuelles_famille = simulation.calculate('paris_base_ressources_commun', last_month)
        montant_aide = select([(ressources_mensuelles_famille <= premier_plafond),
            (ressources_mensuelles_famille <= deuxieme_plafond)], [aide_1er_plafond, aide_2eme_plafond])
        result = (select([(nb_enfants >= 3), (nb_enfants < 3)], [montant_aide, 0])) * elig
        return period, result
