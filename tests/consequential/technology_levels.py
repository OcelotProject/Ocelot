# -*- coding: utf-8 -*-
from ocelot.transformations.consequential.technology_levels import *


def test_log_conflicting_technology_levels():
    given = [{
        'reference product': 'something',
        'technology level': 'new',
        'location': 'here',
        'type': 'transforming activity'
    }, {
        'reference product': 'something',
        'technology level': 'new',
        'location': 'there',
        'type': 'transforming activity'
    }]
    log_conflicting_technology_levels(given)

def test_switch_undefined_to_current():
    given = [{
        'name': '',
        'reference product': 'something',
        'technology level': 'undefined',
        'location': 'here',
        'type': 'transforming activity'
    }, {
        'reference product': 'something',
        'technology level': 'new',
        'location': 'there',
        'type': 'transforming activity'
    }, {
        'reference product': 'something',
        'technology level': 'current',
        'location': 'far away',
        'type': 'transforming activity'
    }]
    expected = [{
        'name': '',
        'reference product': 'something',
        'technology level': 'current',
        'location': 'here',
        'type': 'transforming activity'
    }, {
        'reference product': 'something',
        'technology level': 'new',
        'location': 'there',
        'type': 'transforming activity'
    }, {
        'reference product': 'something',
        'technology level': 'current',
        'location': 'far away',
        'type': 'transforming activity'
    }]
    assert switch_undefined_to_current(given) == expected
