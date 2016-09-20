# -*- coding: utf-8 -*-
from . import remove_exchange_uncertainty
from .pedigree import get_pedigree_variance
import math
import numpy as np
import stats_arrays as sa


"""Uncertainty distributions used in ecospold2.

Provides a common API to useful functions for all distributions.

Still TODO:

* Recalculate doesn't work for normal, uniform, triangular
* Need consistent story on whether we want to deal with pedigree matrix for uniform and triangular
* Doesn't support all distributions in ecoinvent
* Need decision on what 95% thing means in undefined uncertainty
* Need common log format for changes

"""

class NoUncertainty:
    distribution = sa.NoUncertainty

    @staticmethod
    def repair(obj):
        """No-op for no uncertainty"""
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

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'loc': obj['amount'],
        }

    @classmethod
    def sample(cls, obj, size=1):
        """Draw ``size`` samples from this uncertainty distribution"""
        return cls.distribution.bounded_random_variables(
            cls.distribution.from_dicts(cls.to_stats_arrays(obj)),
            size=size
        ).ravel()


class Undefined(NoUncertainty):
    """Undefined uncertainty distribution.

    This distribution has an uncertainty dictionary, include ``minimum`` and ``maximum`` values. However, as there is no given way to understand these values, they are not checked or used in Ocelot."""
    distribution = sa.UndefinedUncertainty

    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``"""
        obj['amount'] *= factor
        obj['uncertainty']['minimum'] *= factor
        obj['uncertainty']['maximum'] *= factor
        # TODO: Adjust 95% factor?
        return obj

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'loc': obj['amount'],
        }


class Lognormal(NoUncertainty):
    """`Lognormal distribution <https://en.wikipedia.org/wiki/Log-normal_distribution>`__, defined by the mean (:math:`\mu`, called ``mu``) and variance (:math:`\sigma^{2}`, called ``variance``) of the distribution's natural logarithm."""
    distribution = sa.LognormalUncertainty

    @staticmethod
    def repair(obj, fix_extremes=True):
        """Fix some common failures in lognormal distributions.

        ``obj`` is an object with a lognormal uncertainty distribution.

        If ``fix_extremes``, will adjust variance values which are almost physically impossible.

        * If ``mean`` is negative, set to positive, and add ``negative = True``.
        * Make ``mean`` the same as ``amount``, and set ``mu`` to ``log(amount)``
        * Resolve any conflicts between ``variance`` and ``variance with pedigree matrix`` by preferring values in ``variance with pedigree uncertainty`` and ``pedigree matrix``.
        * If ``fix_extremes``, adjust clearly wrong uncertainties, using arbitrary rules I just made up:
            * If ``1 < = variance <= e``, then the variance is set to ``ln(variance)``.
            * If the ``variance`` is greater than ``e``, then the variance is set to ``0.25``.

        """
        if obj['amount'] == 0:
            return remove_exchange_uncertainty(obj)
        elif obj['uncertainty']['variance with pedigree uncertainty'] == 0:
            return remove_exchange_uncertainty(obj)
        obj['uncertainty']['mean'] = abs(obj['amount'])
        obj['uncertainty']['negative'] = obj['amount'] < 0
        obj['uncertainty']['mu'] = math.log(obj['uncertainty']['mean'])
        obj['uncertainty']['variance'] = (
            obj['uncertainty']['variance with pedigree uncertainty'] -
            get_pedigree_variance(obj.get('pedigree matrix', {}))
        )
        if fix_extremes and 1 <= obj['uncertainty']['variance'] <= math.e:
            # TODO: Log this
            obj['uncertainty']['variance'] = math.log(obj['uncertainty']['variance'])
            obj['uncertainty']['variance with pedigree uncertainty'] = (
                obj['uncertainty']['variance'] +
                get_pedigree_variance(obj.get('pedigree matrix', {}))
            )
        elif fix_extremes and obj['uncertainty']['variance'] > math.e:
            # TODO: Log this
            obj['uncertainty']['variance'] = 0.25
            obj['uncertainty']['variance with pedigree uncertainty'] = (
                obj['uncertainty']['variance'] +
                get_pedigree_variance(obj.get('pedigree matrix', {}))
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
            # TODO: Log this
            return remove_exchange_uncertainty(obj)
        else:
            obj['amount'] *= factor
            obj['uncertainty']['mean'] = abs(obj['amount'])
            obj['uncertainty']['mu'] = math.log(obj['uncertainty']['mean'])
            return obj

    @staticmethod
    def recalculate(obj):
        """Recalculate uncertainty values based on new pedigree matrix values"""
        obj['uncertainty']['variance with pedigree uncertainty'] = (
            obj['uncertainty']['variance'] +
            get_pedigree_variance(obj.get('pedigree matrix', {}))
        )
        return obj

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary.

        As negative lognormal distributions are not defined using the normal distribution functions, this method sets a ``negative`` flag. ``stats_arrays`` will adjust any results to have the correct sign.

        Uses the standard deviation instead of the variance for compatibility with `scipy <http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html#scipy.stats.lognorm>`__ and `numpy <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.lognormal.html#numpy.random.lognormal>`__."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mu'],
            'scale': math.sqrt(obj['uncertainty']['variance with pedigree uncertainty']),
            'negative': obj['amount'] < 0,
        }


class Normal(NoUncertainty):
    """`Normal distribution <https://en.wikipedia.org/wiki/Normal_distribution>`__, defined by mean and variance."""
    distribution = sa.NormalUncertainty

    @staticmethod
    def repair(obj):
        """Fix some common failures in normal distributions.

        ``obj`` is an object with a normal uncertainty distribution.

        * Make ``mean`` the same as ``amount``
        * Resolve any conflicts between ``variance`` and ``variance with pedigree matrix`` by preferring values in ``variance with pedigree uncertainty`` and ``pedigree matrix``

        """
        if obj['uncertainty']['variance with pedigree uncertainty'] == 0:
            return remove_exchange_uncertainty(obj)
        obj['uncertainty']['mean'] = obj['amount']
        # TODO: Need pedigree matrix math to fix variance
        # The following applies to sum of normal distributions
        # but we have product of normal and lognormal...
        # obj['uncertainty']['variance'] = (
        #     obj['uncertainty']['variance with pedigree uncertainty'] -
        #     get_pedigree_variance(obj.get('pedigree matrix', {}))
        # )
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale uncertainty distribution by a numeric ``factor``.

        Following `Müller et al <http://link.springer.com/article/10.1007/s11367-014-0759-5>`__, rescaling should preserve the coefficient of determination, i.e. :math:`\sigma / \mu`. We are given the original variance, :math:`\sigma^{2}`. Therefore, we can find the new variance using:

        .. math::

            \\frac{\sigma_{old}}{\mu_{old}} = \\frac{\sigma_{new}}{\mu_{new}}

            \\frac{\sigma_{old}^{2}}{\mu_{old}^{2}} = \\frac{\sigma_{new}^{2}}{\mu_{new}^{2}}

            \sigma_{new}^{2} = \\frac{\mu_{new}^{2}}{\mu_{old}^{2}} \sigma_{old}^{2}

        """
        if factor == 0:
            obj['amount'] = 0
            # TODO: Log this
            return remove_exchange_uncertainty(obj)
        obj['uncertainty']['variance'] = (
            (obj['amount'] * factor) / obj['amount']
        ) ** 2 * obj['uncertainty']['variance']
        obj['amount'] *= factor
        # TODO: Adjust variance with pedigree uncertainty
        return Normal.recalculate(obj)

    @staticmethod
    def recalculate(obj):
        """TODO: This is currently not functioning correctly.

        Use new pedigree matrix values to adjust the variance based on `The application of the pedigree
        approach to the distributions foreseen in ecoinvent v3 by Müller,
        et al <http://link.springer.com/article/10.1007/s11367-014-0759-5>`__.

        Adjusting the pedigree matrix for the normal distribution should lead to the same change in coefficient of determination as it would for the lognormal distribution.

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

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary.

        Uses standard deviation instead of variance for compatibility with `scipy <http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html>`__ and `numpy <http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.normal.html>`__."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mean'],
            'scale': math.sqrt(obj['uncertainty']['variance with pedigree uncertainty'])
        }


class Triangular(NoUncertainty):
    """`Triangular distribution <https://en.wikipedia.org/wiki/Triangular_distribution>`__, defined by minimum, mode, and maximum."""
    distribution = sa.TriangularUncertainty

    @staticmethod
    def repair(obj):
        """Make sure the provided values are a valid triangular distribution.

        * Set ``mode`` to ``amount``.
        * Erases uncertainty if minimum == maximum == mode.
        * Flips minimum and maximum if necessary.
        * Raises ``ValueError`` if mode is outside (minimum, maximum)

        """
        ud = obj['uncertainty']
        ud['mode'] = obj['amount']
        if ud['minimum'] == ud['maximum'] == ud['mode']:
            return remove_exchange_uncertainty(obj)
        if ud['minimum'] > ud['maximum']:
            ud['minimum'], ud['maximum'] = ud['maximum'], ud['minimum']
        if ud['mode'] < ud['minimum'] or ud['mode'] > ud['maximum']:
            raise ValueError("Mode is outside (minimum, maximum) bound.")
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale the exchange by a constant numeric ``factor``."""
        obj['uncertainty']['minimum'] *= factor
        obj['uncertainty']['mode'] *= factor
        obj['amount'] *= factor
        obj['uncertainty']['maximum'] *= factor
        # Repair will switch min/max if negative factor, and catch factor == 0
        return Triangular.repair(obj)

    @staticmethod
    def recalculate(obj):
        """This is currently a no-op, as pedigree matrices are not used for this distribution. However, it would be nice to have it in the future for completeness."""
        return obj

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'loc': obj['uncertainty']['mode'],
            'minimum': obj['uncertainty']['minimum'],
            'maximum': obj['uncertainty']['maximum'],
        }


class Uniform(NoUncertainty):
    """`Uniform distribution <https://en.wikipedia.org/wiki/Uniform_distribution_(continuous)>`__, defined by minimum and maximum."""
    distribution = sa.UniformUncertainty

    @staticmethod
    def repair(obj):
        """Make sure the provided values are a valid uniform distribution.

        * Erases uncertainty if minimum == maximum == amount.
        * Flips minimum and maximum if necessary.
        * Raises ``ValueError`` if mode is outside (minimum, maximum)
        * If ``amount`` if not `close to <http://docs.scipy.org/doc/numpy/reference/generated/numpy.allclose.html>`__ halfway between minimum and maximum, change to triangular distribution.

        """
        ud = obj['uncertainty']
        if ud['minimum'] == ud['maximum'] == obj['amount']:
            return remove_exchange_uncertainty(obj)
        if ud['minimum'] > ud['maximum']:
            ud['minimum'], ud['maximum'] = ud['maximum'], ud['minimum']
        if obj['amount'] < ud['minimum'] or obj['amount'] > ud['maximum']:
            raise ValueError("Amount is outside (minimum, maximum) bound.")
        expected = (ud['minimum'] + ud['maximum']) / 2
        if not np.allclose(obj['amount'], expected):
            # TODO: Log this
            ud['type'] = 'triangular'
            return Triangular.repair(obj)
        return obj

    @staticmethod
    def rescale(obj, factor):
        """Rescale the exchange by a constant numeric ``factor``."""
        obj['uncertainty']['minimum'] *= factor
        obj['amount'] *= factor
        obj['uncertainty']['maximum'] *= factor
        # Repair will switch min/max if negative factor, and catch factor == 0
        return Uniform.repair(obj)

    @staticmethod
    def recalculate(obj):
        """This is currently a no-op, as pedigree matrices are not used for this distribution. However, it would be nice to have it in the future for completeness."""
        return obj

    @classmethod
    def to_stats_arrays(cls, obj):
        """Returns a ``stats_arrays`` compatible dictionary."""
        return {
            'uncertainty type': cls.distribution.id,
            'amount': obj['amount'],
            'minimum': obj['uncertainty']['minimum'],
            'maximum': obj['uncertainty']['maximum'],
        }
