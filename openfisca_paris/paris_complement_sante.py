# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_, logical_not as not_, absolute as abs_, minimum as min_, select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_complement_sante(Variable):
    value_type = float
    label = u"Paris Complément Santé pour les personnes âgées et les personnes handicapées"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):

        parisien = famille('parisien', period)

        pcs_pa = famille('paris_complement_sante_pa', period)
        pcs_ph = famille('paris_complement_sante_ph', period)

        return parisien * max_(pcs_pa, pcs_ph)
