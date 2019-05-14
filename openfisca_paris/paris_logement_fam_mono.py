# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_,  logical_not as not_,  absolute as abs_,  minimum as min_,  select, where)

from openfisca_france.model.base import *  # noqa analysis:ignore


class paris_logement_est_monoparentale(Variable):
    value_type = bool
    label = u"Famille monoparentale au sens de Paris logement familles monoparentales"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        parent_solo = not_(famille('en_couple', period))
        nb_enfants = famille('paris_nb_enfants', period)
        parisien = famille('parisien', period)

        logement_a_charge = famille('paris_logement_a_charge', period)

        return  parent_solo * (nb_enfants >= 1) * (nb_enfants < 4) * parisien * logement_a_charge


class paris_logement_plfm_montant(Variable):
    value_type = float
    label = u"Famille monoparentale qui est eligible à Paris logement familles monoparentales"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        premier_plafond_plfm = legislation(period).paris.plfm.premier_plafond_plfm
        deuxieme_plafond_plfm = legislation(period).paris.plfm.deuxieme_plafond_plfm
        aide_1er_plafond_plfm = legislation(period).paris.plfm.aide_1er_plafond_plfm
        aide_2eme_plafond_plfm = legislation(period).paris.plfm.aide_2eme_plafond_plfm

        base_ressources = famille('paris_base_ressources_foyer', last_month)

        return select([(base_ressources <= premier_plafond_plfm),
            (base_ressources <= deuxieme_plafond_plfm)], [aide_1er_plafond_plfm, aide_2eme_plafond_plfm])


class paris_logement_plfm(Variable):
    value_type = float
    label = u"Famille monoparentale qui est eligible à Paris logement familles monoparentales"
    entity = Famille
    definition_period = MONTH

    def formula(famille, period, legislation):
        last_month = period.last_month

        loyer_net = famille('paris_logement_charge_nette_mensuelle', period)
        est_monoparentale = famille('paris_logement_est_monoparentale', period)

        montant_aide_max = famille('paris_logement_plfm_montant', period)

        return est_monoparentale * min_(montant_aide_max, loyer_net)
