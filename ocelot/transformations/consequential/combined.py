# -*- coding: utf-8 -*-
from ..cutoff.combined import combined_production
from ...wrapper import TransformationWrapper


multi_rp = lambda ds: len(e for e in ds['exchanges']
                          if e['type'] == 'reference product') > 1

split_combined_production = TransformationWrapper(combined_production, multi_rp)
