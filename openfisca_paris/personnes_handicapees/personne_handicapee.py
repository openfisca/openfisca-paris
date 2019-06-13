# -*- coding: utf-8 -*-
from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_personne_handicapee(Variable):
    value_type = bool
    label = u"Personne qui a le statut handicapé au sens de la Ville de Paris"
    entity = Individu
    definition_period = MONTH
    reference = "Article III.A.2 du Règlement municipal du CASVP"

    def formula(individu, period, legislation):

        handicap = individu('handicap', period)

        last_month = period.last_month
        aah = individu('aah', last_month)
        # manque : allocation compensatrice pour tierce personne
        pch = individu('pch', last_month)
        pensions_invalidite = individu('pensions_invalidite', last_month)
        # manque : pension de veuve ou de veuf invalide
        rente_accident_travail = individu('rente_accident_travail', last_month)
        # manque : pension anticipée attribuée aux fonctionnaires civils et aux militaires, s'ils ne sont pas admis à rester en service
        # manque : rente viagère d'invalidité servie par la Caisse des dépôts et consignations

        return handicap + aah + pch + pensions_invalidite + rente_accident_travail
