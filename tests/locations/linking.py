from ocelot.errors import UnresolvableActivityLink
from ocelot.transformations.locations.linking import actualize_activity_links
import pytest


def test_actualize_activity_links():
    given = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
        }]
    }]
    expected = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'code': 'find me',
            'name': 'foo',
        }]
    }]
    assert actualize_activity_links(given) == expected

@pytest.mark.skip(reason="Bug in combined production means skip for now")
def test_actualize_activity_links_errors():
    too_many = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'code': 'oops',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'foo',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        actualize_activity_links(too_many)

    too_few = [{
        'code': 'find me',
        'id': 'the right one',
        'exchanges': [],
        'reference product': 'bar',
    }, {
        'id': '',
        'exchanges': [{
            'activity link': 'the right one',
            'name': 'foo',
        }]
    }]
    with pytest.raises(UnresolvableActivityLink):
        actualize_activity_links(too_few)
