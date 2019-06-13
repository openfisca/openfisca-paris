# -*- coding: utf-8 -*-
from openfisca_france.model.base import *  # noqa analysis:ignore


# Pass Paris Access est le nouveau nom du Navigo Emeraude Améthyste pour les personnes en situation de handicap
class paris_pass_access(Variable):
    value_type = bool
    label = u"Éligibilité au Pass Paris Access'"
    entity = Individu
    definition_period = MONTH

    def formula(individu, period):

        personnes_handicap = individu('paris_personne_handicapee', period)
        eligibilite_pass = individu('paris_pass_eligibilite', period)
        
        return personnes_handicap * eligibilite_pass
