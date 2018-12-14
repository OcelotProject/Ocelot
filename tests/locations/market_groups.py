# -*- coding: utf-8 -*-
from ocelot.transformations.locations.market_groups import *
from ocelot.errors import MarketGroupError
import pytest


class FakeTopology:
    def tree(self, data):
        return {
            'G1': {
                'G2': {'M1': {}},
                'M2': {}
            }
        }

    def ordered_dependencies(self, datasets):
        locations = {x['location'] for x in datasets}
        return [x for x in ['G1', 'G2', 'M1', 'M2'] if x in locations]

    def contained(self, location, exclude_self=False, subtract=None,
            resolved_row=None):
        if location == 'G1':
            return {'G2', 'M1', 'M2'}
        elif location == 'G2':
            return {'M1'}
        else:
            return set()

    def __call__(self, x):
        return set()


def reformat_suppliers(result):
    result_as_dict = {ds['code']: sorted([exc['code'] for exc in ds.get('suppliers', [])])
                      for ds in result}
    return {k: v for k, v in result_as_dict.items() if v}


@pytest.fixture(scope="function")
def group_fixture(monkeypatch):
    monkeypatch.setattr(
        'ocelot.transformations.locations.market_groups.topology',
        FakeTopology()
    )
    data = [{
        'type': 'market activity',
        'location': 'M1',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market activity',
        'location': 'M2',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G1',
        'code': '3',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }, {
        'type': 'market group',
        'location': 'G2',
        'code': '4',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product',
            'name': 'foo',
        }]
    }]
    return data


def test_inconsistent_names():
    data = [{
        'type': 'market group',
        'name': 'market group for bar',
        'reference product': 'foo',
    }, {
        'type': 'market group',
        'name': 'market group for foo',
        'reference product': 'foo',
    }]
    with pytest.raises(MarketGroupError):
        link_market_group_suppliers(data)

def test_link_market_group_suppliers_format(group_fixture):
    expected = [{
        'type': 'market activity',
        'location': 'M1',
        'code': '1',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product', 'name': 'foo',
        }]
    }, {
        'type': 'market activity',
        'location': 'M2',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{
            'type': 'reference product', 'name': 'foo',
        }]
    }, {
        'code': '3',
        'exchanges': [
            {'name': 'foo', 'type': 'reference product'}
        ],
        'location': 'G1',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{
            'code': '2',
             'exchanges': [{
                'name': 'foo', 'type': 'reference product'
            }],
            'location': 'M2',
            'name': 'market for foo',
            'reference product': 'foo',
            'type': 'market activity'
        }, {
            'code': '4',
            'exchanges': [
                {'name': 'foo', 'type': 'reference product'}
            ],
            'location': 'G2',
            'name': 'market group for foo',
            'reference product': 'foo',
            'suppliers': [{
                'code': '1',
                'exchanges': [{
                    'name': 'foo', 'type': 'reference product'
                }],
                'location': 'M1',
                'name': 'market for foo',
                'reference product': 'foo',
                'type': 'market activity'
            }],
            'type': 'market group'
        }],
        'type': 'market group'
    }, {
        'code': '4',
        'exchanges': [{
            'name': 'foo', 'type': 'reference product'
        }],
        'location': 'G2',
        'name': 'market group for foo',
        'reference product': 'foo',
        'suppliers': [{
            'code': '1',
            'exchanges': [{
                'name': 'foo', 'type': 'reference product'
            }],
            'location': 'M1',
            'name': 'market for foo',
            'reference product': 'foo',
            'type': 'market activity'
        }],
        'type': 'market group'
    }]
    assert link_market_group_suppliers(group_fixture) == expected

def test_link_market_group_suppliers(group_fixture):
    expected = {
        "3": ["2", "4"],
        "4": ["1"],
     }
    assert reformat_suppliers(link_market_group_suppliers(group_fixture)) == expected

def test_real_locations_including_glo_and_row():
    # Markets: RoW, CA, FR, NO
    # Market groups: GLO, RER, WEU (Western Europe)
    expected = {
        "GLO": ['CA', 'RER', 'RoW'],
        "RER": ['NO', 'WEU'],
        "WEU": ['FR'],

    }
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': 'RoW',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'CA',
        'code': 'CA',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': 'FR',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'NO',
        'code': 'NO',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': 'RER',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'WEU',
        'code': 'WEU',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_glo_includes_missing_activities():
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': 'CA',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'FR',
        'code': 'FR',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'RER',
        'code': 'RER',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "GLO": ['CA', 'RER'],
        "RER": ['FR'],

    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_same_location_market_group_market():
    given = [{
        'type': 'market activity',
        'location': 'CA',
        'code': '2',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'CA',
        'code': '1',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "1": ['2'],
    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_row_only_supply_no_market_group():
    given = [{
        'type': 'market activity',
        'location': 'RoW',
        'code': 'RoW',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market activity',
        'location': 'RER',
        'code': 'RER',
        'name': 'market for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }, {
        'type': 'market group',
        'location': 'GLO',
        'code': 'GLO',
        'name': 'market group for foo',
        'reference product': 'foo',
        'exchanges': [{'type': 'reference product', 'name': 'foo'}]
    }]
    expected = {
        "GLO": ['RER', 'RoW'],
    }
    assert reformat_suppliers(link_market_group_suppliers(given)) == expected

def test_check_markets_only_supply_one_market_group():
    given = [{
        'name': 'market group for foo',
        'location': 'there',
        'code': '1',
        'type': 'market group',
        'exchanges': [{
            'code': '1',
            'type': 'production exchange',
            'amount': 1
        }, {
            'code': '2',
            'type': 'from technosphere',
            'amount': 1
        }]
    }, {
        'name': 'market for foo',
        'location': 'here',
        'type': 'market activity',
        'code': '2',
        'exchanges': []
    }]
    assert check_markets_only_supply_one_market_group(given)

def test_check_markets_only_supply_one_market_group_error():
    given = [{
        'name': 'market group for foo',
        'location': 'RER',
        'code': '1',
        'type': 'market group',
        'exchanges': [{
            'code': '1',
            'type': 'production exchange',
            'amount': 1
        }, {
            'code': '2',
            'type': 'from technosphere',
            'amount': 1
        }]
    }, {
        'name': 'market group for foo',
        'location': 'WEU',
        'code': '3',
        'type': 'market group',
        'exchanges': [{
            'code': '3',
            'type': 'production exchange',
            'amount': 1
        }, {
            'code': '2',
            'type': 'from technosphere',
            'amount': 1
        }]
    }, {
        'name': 'market for foo',
        'location': 'FR',
        'type': 'market activity',
        'code': '2',
        'exchanges': []
    }]
    with pytest.raises(MarketGroupError):
        check_markets_only_supply_one_market_group(given)

def test_check_markets_only_supply_one_market_group_overlapping_allowed():
    # Neither ENTSO-E nor Europe with Switzerland completely cover each other
    given = [{
        'name': 'market group for foo',
        'location': 'ENTSO-E',
        'code': '1',
        'type': 'market group',
        'exchanges': [{
            'code': '1',
            'type': 'production exchange',
            'amount': 1
        }, {
            'code': '2',
            'type': 'from technosphere',
            'amount': 1
        }]
    }, {
        'name': 'market group for foo',
        'location': 'Europe without Switzerland',
        'code': '3',
        'type': 'market group',
        'exchanges': [{
            'code': '3',
            'type': 'production exchange',
            'amount': 1
        }, {
            'code': '2',
            'type': 'from technosphere',
            'amount': 1
        }]
    }, {
        'name': 'market for foo',
        'location': 'EE',
        'type': 'market activity',
        'code': '2',
        'exchanges': []
    }]
    assert check_markets_only_supply_one_market_group(given)

def test_row_market_groups():
    data = [{
        'type': 'market group',
        'location': 'RoW',
    }]
    with pytest.raises(MarketGroupError):
        check_no_row_market_groups(data)

def test_get_next_biggest_candidate():
    assert get_next_biggest_candidate(
        "RER",
        [
            {'location': 'CH'},
            {'location': 'Europe without Switzerland'},
            {'location': 'WEU'},
            {'location': 'IS'},
            {'location': 'CA'},
            {'location': 'GLO'},
        ],
    ) == {'location': 'Europe without Switzerland'}

def test_get_next_biggest_candidate_subtract():
    assert get_next_biggest_candidate(
        "RER",
        [
            {'location': 'CH'},
            {'location': 'Europe without Switzerland'},
            {'location': 'WEU'},
            {'location': 'IS'},
            {'location': 'CA'},
            {'location': 'GLO'},
        ],
        ['Europe without Switzerland'],
    ) == {'location': 'CH'}


def test_get_next_biggest_candidate_none():
    assert get_next_biggest_candidate(
        "CN",
        [
            {'location': 'CH'},
            {'location': 'Europe without Switzerland'},
            {'location': 'WEU'},
            {'location': 'IS'},
            {'location': 'CA'},
            {'location': 'GLO'},
        ],
    ) is None

def test_get_next_biggest_candidate_no_candidates():
    assert get_next_biggest_candidate("CN", []) is None

def test_substitute_market_group_consumers():
    # Need to test the following:
    # - Already market group
    given = [
        {
            'type': 'market group',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }],
            'location': 'CH',
            'reference product': 'foo',
            'code': '1',
            'name': '1',
        }, {
            'type': 'market group',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 90}
            }],
            'location': 'Europe without Switzerland',
            'code': '2',
            'name': '2',
            'reference product': 'foo',
        }, {
            'type': 'market activity',
            'exchanges': [],
            'location': 'WEU',
            'code': '3',
            'reference product': 'foo',
        }, {
            'type': 'market activity',
            'exchanges': [],
            'location': 'GLO',
            'code': 'other',
            'reference product': 'foo',
        }, {
            'type': "transforming activity",
            'reference product': 'ice cream cone',
            'code': '4',
            'exchanges': [{
                'name': 'ice cream cone',
                'type': 'reference product',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'activity link': 'some other provider',
                'code': 'other',
                'amount': 1,
            }, {
                'name': 'waffle cone',
                'type': 'from technosphere',
                'code': '5',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '3',
                'amount': 100,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'amount': 50,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '3',
                'amount': 0,
            }],
            'location': 'RER',
            'name': '',
        }, {
            'type': "transforming activity",
            'reference product': 'waffle cone',
            'code': '5',
            'exchanges': [],
            'location': 'US',
            'name': '',
        }, {
            'type': "market activity",
            'reference product': 'ice cream cone',
            'code': '6',
            'exchanges': [{
                'name': 'ice cream cone',
                'type': 'reference product',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '3',
                'amount': 100,
            }],
            'location': 'WEU',
            'name': '',
        }
    ]
    expected = [
        {
            'type': 'market group',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 10}
            }],
            'location': 'CH',
            'reference product': 'foo',
            'code': '1',
            'name': '1',
        }, {
            'type': 'market group',
            'exchanges': [{
                'type': 'reference product',
                'production volume': {'amount': 90}
            }],
            'location': 'Europe without Switzerland',
            'code': '2',
            'name': '2',
            'reference product': 'foo',
        }, {
            'type': 'market activity',
            'exchanges': [],
            'location': 'WEU',
            'code': '3',
            'reference product': 'foo',
        }, {
            'type': 'market activity',
            'exchanges': [],
            'location': 'GLO',
            'code': 'other',
            'reference product': 'foo',
        }, {
            'type': "transforming activity",
            'reference product': 'ice cream cone',
            'code': '4',
            'exchanges': [{
                'name': 'ice cream cone',
                'type': 'reference product',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'activity link': 'some other provider',
                'code': 'other',
                'amount': 1,
            }, {
                'name': 'waffle cone',
                'type': 'from technosphere',
                'code': '5',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'amount': 50,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '3',
                'amount': 0,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '2',
                'activity': '2',
                'location': 'Europe without Switzerland',
                'amount': 90,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '1',
                'activity': '1',
                'amount': 10,
                'location': 'CH',
            }],
            'location': 'RER',
            'name': '',
        }, {
            'type': "transforming activity",
            'reference product': 'waffle cone',
            'code': '5',
            'exchanges': [],
            'location': 'US',
            'name': '',
        }, {
            'type': "market activity",
            'reference product': 'ice cream cone',
            'code': '6',
            'exchanges': [{
                'name': 'ice cream cone',
                'type': 'reference product',
                'amount': 1,
            }, {
                'name': 'foo',
                'type': 'from technosphere',
                'code': '1',
                'activity': '1',
                'location': 'CH',
                'amount': 100,
            }],
            'location': 'WEU',
            'name': '',
        }
    ]
    assert substitute_market_group_consumers(given) == expected

def test_allocate_replacements():
    given = [
        {'amount': 4, 'production volume': 5},
        {'amount': 4, 'production volume': 15},
    ]
    expected = [
        {'amount': 1},
        {'amount': 3},
    ]
    assert allocate_replacements(given) == expected

def test_allocate_replacements_missing_pv():
    given = [
        {'amount': 4, 'production volume': 0},
        {'amount': 4, 'production volume': 0},
    ]
    expected = [
        {'amount': 2},
        {'amount': 2},
    ]
    assert allocate_replacements(given) == expected

def test_allocate_replacements_some_missing_pv():
    given = [
        {'amount': 4, 'production volume': 0},
        {'amount': 4, 'production volume': 15},
    ]
    expected = [
        {'amount': 0},
        {'amount': 4},
    ]
    assert allocate_replacements(given) == expected

def test_no_row_market_groups():
    given = [{
        'location': 'RoW',
        'type': 'market group',
    }]
    with pytest.raises(MarketGroupError):
        no_row_market_groups(given)
