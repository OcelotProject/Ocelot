# -*- coding: utf-8 -*-
from ocelot.errors import UnresolvableActivityLink
from ocelot.transformations.activity_links import check_activity_link_validity
import pytest


def test_check_activity_link_validity():
    # Check for correctness (ref prod and byproduct)
    # Check for link to technosphere exchange
    # Check for missing
    # Check for multiple (ref prod and byproduct)
    # Check for missing PV
    given = [{}]
