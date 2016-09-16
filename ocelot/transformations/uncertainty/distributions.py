# -*- coding: utf-8 -*-
from . import remove_exchange_uncertainty
from .pedigree import get_pedigree_variance
import logging
import math
import numpy as np


class NoUncertainty:
    @staticmethod
    def repair(obj):
        """Nothing to do for no uncertainty"""
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``"""
        obj['amount'] *= factor
        return obj

    @staticmethod
    def recalculate(obj):
        """Adjusting pedigree matrix values for no uncertainty has no effect"""
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 1,
            'amount': obj['amount'],
            'loc': obj['amount'],
        }


class Undefined(NoUncertainty):
    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``"""
        obj['amount'] *= factor
        obj['uncertainty']['minimum'] *= factor
        obj['uncertainty']['maximum'] *= factor
        # TODO: Adjust 95% factor?
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 0,
            'amount': obj['amount'],
            'loc': obj['amount'],
        }


class Lognormal:
    @staticmethod
    def repair(obj):
        """Fix some common failures in lognormal distributions.

        ``obj`` is an object with a lognormal uncertainty distribution.

        * If ``mean`` is negative, set to positive, and add ``negative = True``.
        * Make ``mean`` the same as ``amount``, and set ``mu`` to ``log(amount)``
        * Resolve any conflicts between ``variance`` and ``variance with pedigree matrix`` by preferring values in ``variance with pedigree uncertainty`` and ``pedigree matrix``.
        * Adjust clearly wrong uncertainties, using arbitrary rules I just made up:
            * If ``1 < = variance <= e``, then the variance is set to ``ln(variance)``.
            * If the ``variance`` is greater than ``e``, then the variance is set to ``0.25``.

        """
        if obj['amount'] == 0:
            return remove_exchange_uncertainty(obj)
        obj['uncertainty']['mean'] = abs(obj['amount'])
        obj['negative'] = obj['amount'] < 0
        obj['uncertainty']['mu'] = math.log(obj['uncertainty']['mean'])
        obj['uncertainty']['variance'] = (
            obj['uncertainty']['variance with pedigree uncertainty'] -
            get_pedigree_variance(obj['pedigree matrix'])
        )
        if 1 <= obj['uncertainty']['variance'] <= math.e:
            obj['uncertainty']['variance'] = math.log(obj['uncertainty']['variance'])
            obj['uncertainty']['variance with pedigree uncertainty'] = (
                obj['uncertainty']['variance'] +
                get_pedigree_variance(obj['pedigree matrix'])
            )
        elif obj['uncertainty']['variance'] > math.e:
            # TODO: Log large values
            obj['uncertainty']['variance'] = 0.25
            obj['uncertainty']['variance with pedigree uncertainty'] = (
                obj['uncertainty']['variance'] +
                get_pedigree_variance(obj['pedigree matrix'])
            )
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``"""
        if factor < 0:
            obj['amount'] = -1 * obj['amount']
            obj['uncertainty']['negative'] = not obj['uncertainty'].get('negative')
            return Lognormal.rescale(obj, abs(factor))
        elif factor == 0:
            obj['amount'] = 0
            return remove_exchange_uncertainty(obj)
        else:
            obj['amount'] *= factor
            obj['uncertainty']['mean'] = abs(obj['amount'])
            obj['uncertainty']['mu'] = math.log(obj['uncertainty']['mean'])
            return obj

    @staticmethod
    def recalculate(obj):
        """Recalculate uncertainty values based on new pedigree matrix"""
        obj['uncertainty']['variance with pedigree uncertainty'] = (
            obj['uncertainty']['variance'] +
            get_pedigree_variance(obj['pedigree matrix'])
        )
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 2,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mu'],
            'scale': math.sqrt(obj['uncertainty']['variance with pedigree uncertainty']),
            'negative': obj['amount'] < 1,
        }


class Normal:
    """Normal distribution.

    Adjustments to variance based on `The application of the pedigree
    approach to the distributions foreseen in ecoinvent v3 by Müller,
    et al <http://link.springer.com/article/10.1007/s11367-014-0759-5>`__."""
    @staticmethod
    def repair(obj):
        """Fix some common failures in normal distributions.

        ``obj`` is an object with a normal uncertainty distribution.

        * Make ``mean`` the same as ``amount``
        * Resolve any conflicts between ``variance`` and ``variance with pedigree matrix`` by preferring values in ``variance with pedigree uncertainty`` and ``pedigree matrix``

        """
        obj['uncertainty']['mean'] = obj['amount']
        obj['uncertainty']['variance'] = (
            obj['uncertainty']['variance with pedigree uncertainty'] -
            get_pedigree_variance(obj['pedigree matrix'])
        )
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``.

        Following Müller et al, rescaling should preserve the coefficient of determination, i.e. :math:`\sigma / \mu`. We are given the original variance, :math:`\sigma^{2}`. Therefore, we can find the new variance using:

        .. math::

            \\frac{\sigma_{old}}{\mu_{old}} = \\frac{\sigma_{new}}{\mu_{new}}

            \\frac{\sigma_{old}^{2}}{\mu_{old}^{2}} = \\frac{\sigma_{new}^{2}}{\mu_{new}^{2}}

            \sigma_{new}^{2} = \\frac{\mu_{new}^{2}}{\mu_{old}^{2}} \sigma_{old}^{2}

        """
        obj['uncertainty']['variance'] = (
            (obj['amount'] * factor) ** 2 / obj['amount'] ** 2
        ) * obj['uncertainty']['variance']
        obj['amount'] *= factor
        # Handle pedigree matrix
        return obj

    @staticmethod
    def recalculate(obj):
        """Adjusting the pedigree matrix for the normal distribution should lead to the same change in coefficient of determination as it would for the lognormal distribution.

        For the lognormal distribution, the coefficient of determination is defined by:

        .. math::

            CV = \sqrt{e^{\sigma^{2}} - 1}

        For the normal distribution, the coefficient of determination is simply :math:`\sigma / \mu`. Additionally, we note that:

        * Recalculating the pedigree matrix should not change the mean, i.e. :math:`\mu`.
        * The pedigree matrix factors operate directly on the variance of the lognormal, so no manipulation is needed on that score.

        So, our calculation algorithm is:

        #. Find the different in variance if the recalculation was applied to the lognormal distribution
        #. Find the relative change in coefficient of determination
        #. Calculate the new variance with pedigree matrix

        .. math::

            CV_{ratio} = \\frac{\sqrt{e^{\sigma_{pm}^{2}} - 1}}{\sqrt{e^{\sigma_{without-pm}^{2}} - 1}}

            \sigma_{without-pm} = 0

            CV_{ratio} = \sqrt{e^{\sigma_{pm}^{2}} - 1}

            \\frac{\sigma_{new}}{\mu_{new}} = \\frac{\sigma_{old}}{\mu_{old}} CV_{ratio}

            \mu_{new} = \mu_{old}

            \sigma_{new}^{2} = \sigma_{old}^{2} ( e^{\sigma_{pm}^{2}} - 1 )

        """
        # obj['uncertainty']['variance with pedigree uncertainty'] = (
        #     obj['uncertainty']['variance'] * \
        #     ( math.exp(get_pedigree_variance(obj['pedigree matrix'])) - 1)
        # )
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 3,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mean'],
            'scale': math.sqrt(obj['uncertainty']['variance with pedigree uncertainty'])
        }


class Triangular:
    """Dummy function"""
    @staticmethod
    def repair(obj):
        return obj

    @staticmethod
    def rescale(obj, factor):
        return obj

    @staticmethod
    def recalculate(obj):
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 5,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mode'],
            'minimum': obj['uncertainty']['minimum'],
            'maximum': obj['uncertainty']['maximum'],
        }


class Uniform:
    """Dummy function"""
    @staticmethod
    def repair(obj):
        return obj

    @staticmethod
    def rescale(obj, factor):
        return obj

    @staticmethod
    def recalculate(obj):
        return obj

    @staticmethod
    def to_stats_arrays(obj):
        return {
            'uncertainty type': 4,
            'amount': obj['amount'],
            'minimum': obj['uncertainty']['minimum'],
            'maximum': obj['uncertainty']['maximum'],
        }
