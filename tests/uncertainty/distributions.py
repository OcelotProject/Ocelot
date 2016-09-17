# -*- coding: utf-8 -*-
from copy import deepcopy
from ocelot.transformations.uncertainty.distributions import *
import numpy as np
import pytest


### NoUncertainty

def test_nouncertainty_repair():
    assert NoUncertainty.repair(1) is 1

def test_nouncertainty_rescale():
    assert NoUncertainty.rescale({"amount": 4}, 2) == {"amount": 8}

def test_nouncertainty_recalculate():
    assert NoUncertainty.recalculate(1) is 1

def test_nouncertainty_stats_arrays():
    expected = {
        'uncertainty type': 1,
        'amount': 4,
        'loc': 4
    }
    assert NoUncertainty.to_stats_arrays({"amount": 4}) == expected

def test_nouncertainty_sample():
    result = NoUncertainty.sample({"amount": 4}, 100)
    assert result.shape == (100,)
    assert np.allclose(result, np.ones((100,)) * 4)


### Undefined

def test_undefined_repair():
    assert Undefined.repair(1) is 1

def test_undefined_rescale():
    given = {
        "amount": 4,
        "uncertainty": {"minimum": 1, "maximum": 2}
    }
    expected = {
        "amount": 8,
        "uncertainty": {"minimum": 2, "maximum": 4}
    }
    assert Undefined.rescale(given, 2) == expected

def test_undefined_recalculate():
    assert Undefined.recalculate(1) is 1

def test_undefined_stats_arrays():
    expected = {
        'uncertainty type': 0,
        'amount': 4,
        'loc': 4
    }
    assert Undefined.to_stats_arrays({"amount": 4}) == expected

def test_undefined_sample():
    result = Undefined.sample({"amount": 4}, 100)
    assert result.shape == (100,)
    assert np.allclose(result, np.ones((100,)) * 4)


### Lognormal

def test_lognormal_repair_zero_amount():
    assert Lognormal.repair({"amount": 0, "uncertainty": {}}) == {"amount": 0}

def test_lognormal_repair_zero_variance():
    given = {
        'amount': 4,
        'uncertainty': {'variance with pedigree uncertainty': 0}
    }
    assert Lognormal.repair(given) == {"amount": 4}

def test_lognormal_repair():
    given = {
        'amount': 4,
        'uncertainty': {
            'variance with pedigree uncertainty': 7
        },
        'pedigree matrix': {}
    }
    expected = {
        'amount': 4,
        'pedigree matrix': {},
        'uncertainty': {
            'mean': 4,
            'mu': np.log(4),
            'negative': False,
            'variance': 7,
            'variance with pedigree uncertainty': 7
        },
    }
    assert Lognormal.repair(given, False) == expected

def test_lognormal_repair_negative():
    given = {
        'amount': -4,
        'uncertainty': {
            'variance with pedigree uncertainty': 7
        },
        'pedigree matrix': {}
    }
    expected = {
        'amount': -4,
        'pedigree matrix': {},
        'uncertainty': {
            'mean': 4,
            'mu': np.log(4),
            'negative': True,
            'variance': 7,
            'variance with pedigree uncertainty': 7
        },
    }
    assert Lognormal.repair(given, False) == expected

def test_lognormal_repair_fix_extremes_medium():
    given = {
        'amount': 4,
        'uncertainty': {
            'variance with pedigree uncertainty': 1.5
        },
        'pedigree matrix': {}
    }
    result = Lognormal.repair(given)
    assert np.allclose(
        result['uncertainty']['variance'],
        np.log(1.5)
    )

def test_lognormal_repair_fix_extremes_high():
    given = {
        'amount': 4,
        'uncertainty': {
            'variance with pedigree uncertainty': 5
        },
        'pedigree matrix': {}
    }
    result = Lognormal.repair(given)
    assert result['uncertainty']['variance'] == 0.25

def test_lognormal_rescale_zero():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    assert Lognormal.rescale(given, 0) == {'amount': 0}

def test_lognormal_rescale_negative():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    expected = {
        'amount': -8,
        'uncertainty': {
            'negative': True,
            'mean': 8,
            'mu': np.log(8)
        }
    }
    assert Lognormal.rescale(given, -2) == expected

def test_lognormal_rescale():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    expected = {
        'amount': 8,
        'uncertainty': {
            'mean': 8,
            'mu': np.log(8)
        }
    }
    assert Lognormal.rescale(given, 2) == expected

def test_lognormal_recalculate():
    given = {
        'uncertainty': {'variance': 1},
        'pedigree matrix': {'reliability': 5}
    }
    expected = {
        'uncertainty': {
            'variance': 1,
            'variance with pedigree uncertainty': 1.04,
        },
        'pedigree matrix': {'reliability': 5}
    }
    assert Lognormal.recalculate(given) == expected

def test_lognormal_stats_arrays():
    given = {
        'amount': 4,
        'uncertainty': {
            'variance': 1,
            'variance with pedigree uncertainty': 4,
            'mu': 3
        }
    }
    expected = {
        'uncertainty type': 2,
        'amount': 4,
        'loc': 3,
        'scale': 2,
        'negative': False
    }
    assert Lognormal.to_stats_arrays(given) == expected

def test_lognormal_sample():
    given = {
        'amount': 0.5,
        'uncertainty': {
            'variance with pedigree uncertainty': 0.05,
            'mu': np.log(0.5)
        }
    }
    result = Lognormal.sample(given, 1000)
    assert result.shape == (1000,)
    assert not (result <= 0).sum()
    assert 0.4 < np.average(result) < 0.6


### Normal

def test_normal_repair():
    given = {
        'amount': 4,
        'uncertainty': {
            'variance with pedigree uncertainty': 7
        }
    }
    expected = {
        'amount': 4,
        'uncertainty': {
            'mean': 4,
            'variance with pedigree uncertainty': 7
        }
    }
    assert Normal.repair(given) == expected

def test_normal_repair_zero_variance():
    given = {
        'amount': 4,
        'uncertainty': {'variance with pedigree uncertainty': 0}
    }
    assert Normal.repair(given) == {"amount": 4}

def test_normal_rescale_zero():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    assert Normal.rescale(given, 0) == {'amount': 0}

def test_normal_rescale():
    given = {
        'amount': 1,
        'uncertainty': {'variance': 0.5}
    }
    expected = {
        'amount': 2,
        'uncertainty': {'variance': 4 / 1 * 0.5}
    }
    assert Normal.rescale(given, 2) == expected

def test_normal_recalculate():
    assert Normal.recalculate('foo') == 'foo'

def test_normal_stats_arrays():
    given = {
        'amount': 4,
        'uncertainty': {
            'mean': 3,
            'variance with pedigree uncertainty': 4,
        }
    }
    expected = {
        'uncertainty type': 3,
        'amount': 4,
        'loc': 3,
        'scale': 2,
    }
    assert Normal.to_stats_arrays(given) == expected

def test_normal_sample():
    given = {
        'amount': 1,
        'uncertainty': {
            'variance with pedigree uncertainty': 0.2,
            'mean': 1
        }
    }
    result = Normal.sample(given, 1000)
    assert result.shape == (1000,)
    assert 0.8 < np.average(result) < 1.2


### Triangular

def test_triangular_repair_all_same():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 4,
            'maximum': 4
        }
    }
    assert Triangular.repair(given) == {'amount': 4}

def test_triangular_repair():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 3,
            'maximum': 7
        }
    }
    expected = {
        'amount': 4,
        'uncertainty': {
            'minimum': 3,
            'maximum': 7,
            'mode': 4
        }
    }
    assert Triangular.repair(given) == expected

def test_triangular_repair_switch():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 6,
            'maximum': 2
        }
    }
    expected = {
        'amount': 4,
        'uncertainty': {
            'minimum': 2,
            'maximum': 6,
            'mode': 4
        }
    }
    assert Triangular.repair(given) == expected

def test_triangular_repair_outside_bounds():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 3
        }
    }
    with pytest.raises(ValueError):
        Triangular.repair(given)

def test_triangular_rescale_zero():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    assert Triangular.rescale(given, 0) == {'amount': 0}

def test_triangular_rescale():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
            'mode': 4,
        }
    }
    expected = {
        'amount': 8,
        'uncertainty': {
            'minimum': 2,
            'maximum': 10,
            'mode': 8
        }
    }
    assert Triangular.rescale(given, 2) == expected

def test_triangular_rescale_negative():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
            'mode': 4,
        }
    }
    expected = {
        'amount': -8,
        'uncertainty': {
            'minimum': -10,
            'maximum': -2,
            'mode': -8
        }
    }
    assert Triangular.rescale(given, -2) == expected

def test_triangular_rescale_zero():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
            'mode': 4,
        }
    }
    assert Triangular.rescale(given, 0) == {'amount': 0}

def test_triangular_recalculate():
    assert Triangular.recalculate('foo') == 'foo'

def test_triangular_stats_arrays():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
            'mode': 3,
        }
    }
    expected = {
        'uncertainty type': 5,
        'amount': 4,
        'loc': 3,
        'minimum': 1,
        'maximum': 5
    }
    assert Triangular.to_stats_arrays(given) == expected

def test_triangular_sample():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
            'mode': 3,
        }
    }
    result = Triangular.sample(given, 1000)
    assert result.shape == (1000,)
    assert 2.8 < np.average(result) < 3.2
    assert result.min() >= 1
    assert result.max() <= 5


### Uniform

def test_uniform_repair_all_same():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 4,
            'maximum': 4
        }
    }
    assert Uniform.repair(given) == {'amount': 4}

def test_uniform_repair():
    given = {
        'amount': 5,
        'uncertainty': {
            'minimum': 3,
            'maximum': 7
        }
    }
    expected = deepcopy(given)
    assert Uniform.repair(given) == expected

def test_uniform_repair_to_triangular():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 3,
            'maximum': 7
        }
    }
    expected = {
        'amount': 4,
        'uncertainty': {
            'minimum': 3,
            'maximum': 7,
            'mode': 4,
            'type': 'triangular',
        }
    }
    assert Uniform.repair(given) == expected

def test_uniform_repair_switch():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 6,
            'maximum': 2
        }
    }
    expected = {
        'amount': 4,
        'uncertainty': {
            'minimum': 2,
            'maximum': 6,
        }
    }
    assert Uniform.repair(given) == expected

def test_uniform_repair_outside_bounds():
    given = {
        'amount': 4,
        'uncertainty': {
            'minimum': 1,
            'maximum': 3
        }
    }
    with pytest.raises(ValueError):
        Uniform.repair(given)

def test_uniform_rescale_zero():
    given = {
        'amount': 4,
        'uncertainty': {}
    }
    assert Uniform.rescale(given, 0) == {'amount': 0}

def test_uniform_rescale():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
        }
    }
    expected = {
        'amount': 6,
        'uncertainty': {
            'minimum': 2,
            'maximum': 10,
        }
    }
    assert Uniform.rescale(given, 2) == expected

def test_uniform_rescale_negative():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
        }
    }
    expected = {
        'amount': -6,
        'uncertainty': {
            'minimum': -10,
            'maximum': -2,
        }
    }
    assert Uniform.rescale(given, -2) == expected

def test_uniform_rescale_zero():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
        }
    }
    assert Uniform.rescale(given, 0) == {'amount': 0}

def test_uniform_recalculate():
    assert Uniform.recalculate('foo') == 'foo'

def test_uniform_stats_arrays():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
        }
    }
    expected = {
        'uncertainty type': 4,
        'amount': 3,
        'minimum': 1,
        'maximum': 5
    }
    assert Uniform.to_stats_arrays(given) == expected

def test_uniform_sample():
    given = {
        'amount': 3,
        'uncertainty': {
            'minimum': 1,
            'maximum': 5,
        }
    }
    result = Uniform.sample(given, 1000)
    assert result.shape == (1000,)
    assert 2.8 < np.average(result) < 3.2
    assert result.min() >= 1
    assert result.max() <= 5
