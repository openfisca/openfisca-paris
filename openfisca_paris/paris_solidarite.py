# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore

# Paris solidarité pour les personnes agées et les personnes handicapées

class paris_logement_psol(Variable):
    value_type = float
    label = u"Montant de l'aide Paris Solidarité"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period):

        parisien = famille('parisien', period)

        psol_pa = famille('paris_solidarite_pa', period)
        psol_ph = famille('paris_solidarite_ph', period)

        result = parisien * max_(psol_pa, psol_ph)

        return result
