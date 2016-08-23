# -*- coding: utf-8 -*-
import arrow
import math

PEDIGREE_MATRIX_VALUES = {
    # From the data quality guidelines
    # e.g. http://www.ecoinvent.org/files/dataqualityguideline_ecoinvent_3_20130506.pdf
    'original': {
        "reliability": (0, 0.0006, 0.002, 0.008, 0.04),
        "completeness": (0, 0.0001, 0.0006, 0.002, 0.008),
        "temporal correlation": (0, 0.0002, 0.002, 0.008, 0.04),
        "geographical correlation": (0, 0.000025, 0.0001, 0.0006, 0.002),
        "further technological correlation": (0, 0.0006, 0.008, 0.04, 0.12),
        "sample size": (0, 9.8e-05, 0.0006, 0.0023, 0.0083)
    },
    # From "Empirically based uncertainty factors for the pedigree matrix in ecoinvent"
    # http://link.springer.com/article/10.1007/s11367-013-0670-5
    "Ciroth et al": {
        "reliability": (0.0, 0.047, 0.057, 0.069, 0.069),
        "completeness": (0.0, 0.00022, 0.00038, 0.0015, 0.0015),
        "temporal correlation": (0, 0.00022, 0.0023, 0.0076, 0.016),
        "geographical correlation": (0, 0.00022, 0.0023, 0.0076, 0.016),
        "further technological correlation": (0, 0.00022, 0.0023, 0.0076, 0.016),
        "sample size": (0,0,0,0,0)
    }
}



def get_pedigree_variance(pm, version="original"):
    """Get additional variance added by ``pm``"""
    assert all(isinstance(obj, int) for obj in pm.values())
    return sum(PEDIGREE_MATRIX_VALUES[version][k][v - 1] for k, v in pm.items())


def adjust_pedigree_matrix_time(ds, exc, year):
    if 'pedigree matrix' not in exc:
        return exc

    new_year = year if isinstance(year, int) else arrow.get(year).year
    difference = new_year - arrow.get(ds['end date'])
    current_value = exc['pedigree matrix']['temporal correlation']

    if difference > 0:
        if current_value == 3 and difference <= 5:
            new_value = 4
        elif current_value == 2 and difference < 5:
            new_value = 3
        elif current_value == 2 and difference == 5:
            new_value = 4
        elif current_value == 1 and difference <= 3:
            new_value = 2
        elif current_value == 1 and difference <= 7:
            new_value = 3
        elif current_value == 1 and difference <= 12:
            new_value = 4
        else:
            new_value = 5
        exc['pedigree matrix']['temporal correlation'] = new_value
    return exc
