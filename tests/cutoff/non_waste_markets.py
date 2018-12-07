from ocelot.transformations.cutoff import adjust_market_signs_for_allocatable_products as adj

def test_adjust_market_signs_for_allocatable_products_one():
    given = [{
        'name': 'a name',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': -1,
            'type': 'reference product',
            'byproduct classification': 'allocatable product',
        }, {
            'name': 'exchange 2',
            'amount': -.5,
            'type': 'something else',
        }]
    }, {
        'name': 'a name 2',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': -1,
            'type': 'reference product',
            'byproduct classification': 'waste',
        }, {
            'name': 'exchange 2',
            'amount': -.5,
            'type': 'something else',
        }]
    }, {
        'name': 'a name 3',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': -1,
            'type': 'reference product',
            'byproduct classification': 'allocatable product',
        }, {
            'name': 'exchange 2',
            'amount': .5,
            'type': 'something else',
        }]
    }]
    expected = [{
        'name': 'a name',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': 1,
            'type': 'reference product',
            'byproduct classification': 'allocatable product',
        }, {
            'name': 'exchange 2',
            'amount': .5,
            'type': 'something else',
        }]
    }, {
        'name': 'a name 2',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': -1,
            'type': 'reference product',
            'byproduct classification': 'waste',
        }, {
            'name': 'exchange 2',
            'amount': -.5,
            'type': 'something else',
        }]
    }, {
        'name': 'a name 3',
        'location': 'somewhere',
        'type': 'market activity',
        'exchanges': [{
            'name': 'exchange 1',
            'amount': -1,
            'type': 'reference product',
            'byproduct classification': 'allocatable product',
        }, {
            'name': 'exchange 2',
            'amount': .5,
            'type': 'something else',
        }]
    }]
    assert adj(given) == expected
