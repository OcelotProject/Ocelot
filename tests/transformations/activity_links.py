# -*- coding: utf-8 -*-
from ocelot.errors import UnresolvableActivityLink
from ocelot.transformations.activity_links import check_activity_link_validity
import pytest


def test_check_activity_link_validity_ref_product():
    ref_prod = [{
        'id': 1,
        'exchanges': [{
            'type': 'reference product',
            'name': 'widget',
            'production volume': {'amount': 42}
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    assert check_activity_link_validity(ref_prod)

def test_check_activity_link_validity_byproduct():
    byproduct = [{
        'id': 1,
        'exchanges': [{
            'type': 'byproduct',
            'classification': 'allocatable product',
            'name': 'widget',
            'production volume': {'amount': 42}
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    assert check_activity_link_validity(byproduct)

def test_check_activity_link_validity_no_pv():
    missing = [{
        'id': 1,
        'filepath': 'somewhere',
        'exchanges': [{
            'type': 'reference product',
            'name': 'widget',
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(missing)

def test_check_activity_link_validity_technosphere_exchange():
    missing = [{
        'id': 1,
        'filepath': 'somewhere',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'widget',
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(missing)

def test_check_activity_link_validity_multiple():
    missing = [{
        'id': 1,
        'filepath': 'somewhere',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 42},
            'name': 'widget',
        }, {
            'type': 'reference product',
            'production volume': {'amount': 24},
            'name': 'widget',
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(missing)

def test_check_activity_link_validity_missing():
    missing = [{
        'id': 1,
        'filepath': 'somewhere',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 42},
            'name': 'bubblegum',
        }]
    }, {
        'id': 2,
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': 1,
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(missing)
