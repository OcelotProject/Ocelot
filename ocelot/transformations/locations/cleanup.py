def correct_natural_gas_pipeline_location(data):
    """Correct specific location in ecoinvent 3.3"""
    for ds in data:
        if (ds['type'] == 'transforming activity' and
            ds['name'] == 'transport, pipeline, long distance, natural gas' and
            ds['location'] == 'RER w/o DE+NL+NO'):
            ds['location'] = 'RER w/o DE+NL+NO+RU'
    return data
