# -*- coding: utf-8 -*-
from ._topology import Topology

topology = Topology()

from .rest_of_world import relabel_global_to_row
from .validation import (
    # check_markets_dont_overlap,
    check_single_global_dataset,
)

