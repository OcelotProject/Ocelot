# -*- coding: utf-8 -*-
from ocelot.errors import UnresolvableActivityLink
from ocelot.transformations.activity_links import *
import pytest


def test_update_activity_link_parent_child():
    given = []
    expected = []
    assert update_activity_link_parent_child(given) == expected

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
            'byproduct classification': 'allocatable product',
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

@pytest.mark.skip(reason="`allocatable_production` doesn't check for production volumes anymore")
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
    error = [{
        'id': '1',
        'filepath': 'somewhere',
        'exchanges': [{
            # Not allocatable production exchange
            'type': 'from technosphere',
            'name': 'widget',
        }]
    }, {
        'id': '2',
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': '1',
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(error)

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

def test_check_activity_link_validity_missing_activity():
    missing = [{
        'id': '1',
        'filepath': 'foo',
        'exchanges': [{
            'type': 'from technosphere',
            'activity link': '2',
            'name': 'widget',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        check_activity_link_validity(missing)

def test_add_hard_linked_production_volumes_simple():
    given = [{
        'name': 'foo',
        'location': 'foo',
        'id': 'link to me',
        'exchanges': [{
            'name': 'François',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }]
    }, {
        'name': 'foo',
        'location': 'foo',
        'id': 'not useful',
        'exchanges': [{
            'activity link': 'link to me',
            'amount': 2,
            'byproduct classification': "don't worry about it",
            'name': 'François',
            'type': 'from technosphere',
        }, {
            'amount': 5,
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }]
    }]
    expected = [{
        'name': 'foo',
        'location': 'foo',
        'id': 'link to me',
        'exchanges': [{
            'name': 'François',
            'production volume': {
                'amount': 100,
                'subtracted activity link volume': 2 * 100 / 5
            },
            'type': 'reference product',
        }],
    }, {
        'name': 'foo',
        'location': 'foo',
        'id': 'not useful',
        'exchanges': [{
            'activity link': 'link to me',
            'amount': 2,
            'byproduct classification': "don't worry about it",
            'name': 'François',
            'type': 'from technosphere',
        }, {
            'amount': 5,
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }],
    }]
    assert add_hard_linked_production_volumes(given) == expected

def test_add_hard_linked_production_volumes_choose_scale_value():
    given = [{
        'name': 'foo',
        'location': 'foo',
        'id': 'link to me',
        'exchanges': [{
            'name': 'François',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }]
    }, {
        'name': 'foo',
        'location': 'foo',
        'id': 'not useful',
        'exchanges': [{
            'activity link': 'link to me',
            'amount': 2,
            'byproduct classification': "don't worry about it",
            'name': 'François',
            'type': 'from technosphere',
        }, {
            'amount': 5,
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 10},
            'type': 'reference product',
        }, {
            'amount': 5,
            'byproduct classification': 'allocatable product',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }]
    }]
    ds = add_hard_linked_production_volumes(given)[0]
    assert ds['exchanges'][0]['production volume']['subtracted activity link volume'] == 2 * 100 / 5

def test_add_hard_linked_production_volumes_multiple_targets():
    error = [{
        'name': 'foo',
        'location': 'foo',
        'id': 'link to me',
        'exchanges': [{
            'name': 'François',
            'production volume': {'amount': 100},
            'type': 'reference product',
        }, {
            'name': 'François',
            'production volume': {'amount': 100},
            'type': 'byproduct',
            'byproduct classification': 'allocatable product',
        }]
    }, {
        'name': 'foo',
        'location': 'foo',
        'id': 'not useful',
        'exchanges': [{
            'activity link': 'link to me',
            'amount': 2,
            'byproduct classification': "don't worry about it",
            'name': 'François',
            'type': 'from technosphere',
        }]
    }]
    with pytest.raises(AssertionError):
        add_hard_linked_production_volumes(error)

def test_fix_35_activity_links():
    given = [{
        'exchanges': [{'activity link': '25edb027-d7c0-4756-a051-cab82e4f6248',}]
    }]
    expected = [{'exchanges': [{}]}]
    assert fix_35_activity_links(given) == expected

def test_update_transforming_activity_production_volumes():
    given = [{
        'type': 'transforming activity',
        'exchanges': [{
            'production volume': {
                'amount': 100,
                'subtracted activity link volume': 25},
            'type': 'reference product',
        }]
    }]
    expected = [{
        'type': 'transforming activity',
        'exchanges': [{
            'production volume': {
                'amount': 75,
                'original amount': 100,
                'subtracted activity link volume': 25},
            'type': 'reference product',
        }]
    }]
    assert update_transforming_activity_production_volumes(given) == expected
