from ocelot.transformations.locations import correct_natural_gas_pipeline_location as cng


def test_cng():
    given = [{
        'type': 'transforming activity',
        'location': 'RER w/o DE+NL+NO',
        'name': 'transport, pipeline, long distance, natural gas'
    }, {
        'type': 'transforming activity',
        'location': 'RER',
        'name': 'transport, pipeline, long distance, natural gas'
    }, {
        'type': 'market activity',
        'location': 'RER w/o DE+NL+NO',
        'name': 'market for transport, pipeline, long distance, natural gas'

    }]
    expected = [{
        'type': 'transforming activity',
        'location': 'RER w/o DE+NL+NO+RU',
        'name': 'transport, pipeline, long distance, natural gas'
    }, {
        'type': 'transforming activity',
        'location': 'RER',
        'name': 'transport, pipeline, long distance, natural gas'
    }, {
        'type': 'market activity',
        'location': 'RER w/o DE+NL+NO',
        'name': 'market for transport, pipeline, long distance, natural gas'
    }]
    assert cng(given) == expected
