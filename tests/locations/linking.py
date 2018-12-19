from ocelot.errors import (
    UnresolvableActivityLink,
    MissingSupplier,
)
from ocelot.transformations.locations.linking import (add_reference_product_codes,
    actualize_activity_links,
    link_consumers_to_recycled_content_activities,
    link_consumers_to_markets,
    log_and_delete_unlinked_exchanges,
)
import pytest
from copy import deepcopy


def test_add_reference_product_codes():
    given = [{
        'code': 'foo',
        'exchanges': [{
            'type': 'reference product',
        }, {
            'type': 'not reference product'
        }]
    }]
    expected = [{
        'code': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'code': 'foo'
        }, {
            'type': 'not reference product'
        }]
    }]
    assert add_reference_product_codes(given) == expected

def test_add_reference_product_codes_error():
    given = [{'name': ''}]
    with pytest.raises(AssertionError):
        add_reference_product_codes(given)

def test_actualize_activity_links():
    given = [{
        'code': 'find me',
        'id': 'the right one',
        'name': '',
        'location': '',
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
        'name': '',
        'location': '',
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
            'amount': 1,
        }]
    }]
    # with pytest.raises(UnresolvableActivityLink):
    #     actualize_activity_links(too_many)
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
            'amount': 1,
        }]
    }]
    # with pytest.raises(UnresolvableActivityLink):
    #     actualize_activity_links(too_few)
    actualize_activity_links(too_few)

def test_link_consumers_to_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'reference product': 'sandwiches',
        'name': '',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 2,
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    expected = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'Made in the EU',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'olympics',
        'exchanges': [],
    }, {
        'type': 'market group',
        'reference product': 'sandwiches',
        'name': '',
        'location': 'BR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
        }]
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 2,
            'code': 'Made in the EU',
        }, {
            'type': 'from technosphere',
            'name': 'cheese',
            'code': 'already here',
        }, {
            'type': 'something else',
            'name': 'cheese',
        }]
    }]
    assert link_consumers_to_markets(given) == expected

def test_link_consumers_to_markets_no_market():
    missing = [{
        'type': 'market activity',
        'reference product': 'granola',
        'name': '',
        'location': 'UCTE without Germany',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'FR',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    with pytest.raises(MissingSupplier):
        link_consumers_to_markets(missing)

def test_link_consumers_to_markets_global_activity():
    given = [{
        'type': 'transforming activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'GLO',
        'code': 'g',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'enzymes',
            'amount': 2,
            'unit': 'foo',
        }],
    }, {
        'type': 'market activity',
        'reference product': 'enzymes',
        'name': '',
        'location': 'CH',
        'code': 'ch',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': 'special swiss enzymes'
        }]
    }, {
        'type': 'market activity',
        'reference product': 'enzymes',
        'name': '',
        'location': 'US',
        'code': 'us',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 2},
            'name': 'special USA enzymes'
        }]
    }, {
        'type': 'market activity',
        'reference product': 'enzymes',
        'name': '',
        'location': 'RoW',
        'code': 'row',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 3},
            'name': 'boring enzymes'
        }]
    }, {
        'type': 'market activity',
        'reference product': 'enzymes',
        'name': '',
        'location': 'CN',
        'code': 'cn',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 4},
            'name': 'special mandarin enzymes'
        }]
    }]
    expected = [{
        'amount': 0.6,
        'code': 'row',
        'name': 'enzymes',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': 'foo',
    },{
        'amount': 0.4,
        'code': 'us',
        'name': 'enzymes',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': 'foo',
    },{
        'amount': 0.8,
        'code': 'cn',
        'name': 'enzymes',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': 'foo'
    },{
        'amount': 0.2,
        'code': 'ch',
        'name': 'enzymes',
        'tag': 'intermediateExchange',
        'type': 'from technosphere',
        'unit': 'foo'
    }]
    assert (
        link_consumers_to_markets(deepcopy(given))[1:] ==
        given[1:]
    )
    assert (
        link_consumers_to_markets(deepcopy(given))[0]['exchanges'] ==
        expected
    )

def test_link_consumers_to_markets_prefer_m_to_mg():
    given = [{
        'type': 'market group',
        'reference product': 'cheese',
        'name': '',
        'location': 'US',
        'code': 'a',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'US',
        'code': 'b',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'CA',
        'code': 'c',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'NAFTA',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
            'unit': ''
        }]
    }]
    result = link_consumers_to_markets(given)
    assert set(x['code'] for x in result[-1]['exchanges']) == set('bc')

def test_link_consumers_to_markets_same_product_name():
    given = [{
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': 'something different',
        'location': 'GLO',
        'code': 'a',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'WECC',
        'code': 'b',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'CA',
        'code': 'c',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': 'something',
        'location': 'NAFTA',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
            'unit': ''
        }]
    }]
    result = link_consumers_to_markets(given)
    assert [x['code'] for x in result[-1]['exchanges']] == ['c']

def test_link_consumers_to_markets_include_mg():
    given = [{
        'type': 'market group',
        'reference product': 'cheese',
        'name': '',
        'location': 'US',
        'code': 'a',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'WECC',
        'code': 'b',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'CA',
        'code': 'c',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'NAFTA',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
            'unit': ''
        }]
    }]
    result = link_consumers_to_markets(given)
    assert set(x['code'] for x in result[-1]['exchanges']) == set('ac')

def test_link_consumers_to_markets_include_global_mg():
    given = [{
        'type': 'market group',
        'reference product': 'cheese',
        'name': '',
        'location': 'GLO',
        'code': 'a',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'WECC',
        'code': 'b',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'CA',
        'code': 'c',
        'exchanges': [{
            'type': 'reference product',
            'production volume': {'amount': 1},
            'name': ''
        }],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'GLO',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
            'unit': ''
        }]
    }]
    result = link_consumers_to_markets(given)
    assert set(x['code'] for x in result[-1]['exchanges']) == set('a')

def test_link_consumers_to_markets_global_no_link():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'BR',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert 'code' not in result[2]['exchanges'][0]

def test_link_consumers_to_markets_global():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'GLO',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    result = link_consumers_to_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert result[2]['exchanges'][0]['code'] == 'yes!'

def test_link_consumers_to_markets_global_use_row():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'market activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RoW',
        'code': 'yes!',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'US',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    result = link_consumers_to_markets(given)
    assert result[2]['reference product'] == 'crackers'
    assert result[2]['exchanges'][0]['code'] == 'yes!'

def test_log_and_delete_unlinked_exchanges_logged():
    error = [{
        'type': 'market activity',
        'reference product': 'nope',
        'name': '',
        'location': 'RER',
        'code': '',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    # TODO: Check if message written to log
    log_and_delete_unlinked_exchanges(error)

def test_log_and_delete_unlinked_exchanges_deletion():
    error = [{
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese',
            'amount': 1,
        }]
    }]
    expected = [{
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': []
    }]
    assert log_and_delete_unlinked_exchanges(error) == expected

def test_link_consumers_to_recycled_content_activities():
    given = [{
        'type': 'transforming activity',
        'reference product': 'cheese, Recycled Content cut-off',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese, Recycled Content cut-off'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert result[1]['exchanges'][0]['code'] == 'found it'

def test_link_consumers_to_recycled_content_activities_not_markets():
    given = [{
        'type': 'market activity',
        'reference product': 'cheese, Recycled Content cut-off',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese, Recycled Content cut-off'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert 'code' not in result[1]['exchanges'][0]

def test_link_consumers_to_recycled_content_activities_wrong_name():
    given = [{
        'type': 'transforming activity',
        'reference product': 'cheese',
        'name': '',
        'location': 'RER',
        'code': 'found it',
        'exchanges': [],
    }, {
        'type': 'transforming activity',
        'reference product': 'crackers',
        'name': '',
        'location': 'DE',
        'exchanges': [{
            'type': 'from technosphere',
            'name': 'cheese'
        }]
    }]
    result = link_consumers_to_recycled_content_activities(given)
    assert result[1]['reference product'] == 'crackers'
    assert 'code' not in result[1]['exchanges'][0]
