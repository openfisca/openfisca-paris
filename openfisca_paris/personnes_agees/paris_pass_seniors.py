# -*- coding: utf-8 -*-
from openfisca_france.model.base import *  # noqa analysis:ignore


# Pass Paris Seniors est le nouveau nom du Navigo Emeraude Améthyste pour les personnes âgées
class paris_pass_seniors(Variable):
    value_type = bool
    label = u"Éligibilité au Pass Paris Seniors"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        personnes_agees = individu('paris_personne_agee', period)
        eligibilite_pass = individu('paris_pass_eligibilite', period)
        
        return personnes_agees * eligibilite_pass
