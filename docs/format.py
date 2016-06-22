Dataset:
{	'id': str, 
    'name': str, #field 100: activityName
    'filepath': str, 
    'location': str, #field 410: shortname
    'technology level': str, #field 500: technologyLevel.  either undefined, new, modern, current, old or outdated
    'economic scenario': str, #field 700: macroEconomicScenarioId
    'exchanges': [{
        'amount': float, #field 1020: amount
        'id': str, #uuid as hex-encoded string, #field 1005: id
		'mathematical relation': str, #optional, field 1060: mathematicalRelation
		'variable': str, #optional, field 1040: variableName
        'name': str, # field 1000: name
		'compartment': str, 
		'subcompartment': str, 
        # The following only applies to exchanges whose "type" is "reference product" and "byproduct"
        'production volume': {
            'amount': float, #field 1530: productionVolumeAmount
            # Optional name of this numeric value as a variable
            'variable': str, #field 1532: productionVolumeVariableName
            # Optional mathematical relation defining this numeric value
            'mathematical relation': str, #field 1534: productionVolumeMathematicalRelation
            'uncertainty': { #field 1539: productionVolumeUncertainty
                # filled with distribution-specific numeric fields,
                # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                'pedigree matrix': tuple, #5 integers between 1 and 5, 
				#fields 2271 to 2275: reliability, completeness, temporalCorrelation, geographicalCorrelation, furtherTechnologyCorrelation
                'type': str, #either: 'normal', 'lognormal', 'triangular', 'uniform', or 'undefined'
            }
        },
		'activity link': str #optional, uuid of the the activity link.  Field 1520: activityLinkId
		'byproduct classification': str, #optional, field 310: classificationValue, if classificationSystem is 'By-product classification'.  either 'allocatable', 'waste' or 'recyclable'
        'tag': str, #either 'intermediateExchange' or 'elementaryExchange', from the XML tag name of the exchange
        'type': str, #either 'from technosphere', 'from environment', 'reference product', 'byproduct', 'to environment'
        'unit': str, #field 1035: unitName
		'uncertainty': { #field 1300: uncertainty
                # filled with distribution-specific numeric fields,
                # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                'pedigree matrix': tuple, #5 integers between 1 and 5, 
				#fields 2271 to 2275: reliability, completeness, temporalCorrelation, geographicalCorrelation, furtherTechnologyCorrelation
                'type': str, #either: 'normal', 'lognormal', 'triangular', 'uniform', or 'undefined'
            }
		'properties': {'property name': {#optional, field 1400: property
			'amount': float, #field 2330: amount
			'unit': str, #field 2324: unitName
			'id': str, #uuid as hex-encoded string, #field 2300: propertyId
			'variable': str, #field 2350: variableName
			'mathematical relation': str, #optional, field 2340: mathematicalRelation
			'uncertainty': { #field 2360: uncertainty
                # filled with distribution-specific numeric fields,
                # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                'pedigree matrix': tuple, #5 integers between 1 and 5, 
				#fields 2271 to 2275: reliability, completeness, temporalCorrelation, geographicalCorrelation, furtherTechnologyCorrelation
                'type': str, #either: 'normal', 'lognormal', 'triangular', 'uniform', or 'undefined'
				}
			}}
    }],
    'start date': str,
	'end date': str, # Starting and ending dates for dataset validity, in format '2015-12-31'
    'type': str, #field 115: specialActivityType.  Either 'transforming activity', 'market activity', 'market group'
	'parameters': [{
        'amount': float, #field 1710: amount
        'name': str, #field 1700: name
        'variable': str, #field 1715: variableName
        'mathematical relation': str, #field 1720: mathematicalRelation
        'uncertainty': { #field 1730: uncertainty
                # filled with distribution-specific numeric fields,
                # e.g. 'mean', 'maximum', 'minimum', as well as the following:
                'pedigree matrix': tuple, #5 integers between 1 and 5, 
				#fields 2271 to 2275: reliability, completeness, temporalCorrelation, geographicalCorrelation, furtherTechnologyCorrelation
                'type': str, #either: 'normal', 'lognormal', 'triangular', 'uniform', or 'undefined'
				}
    }],
	'access restricted': str, #field 3550: accessRestrictedTo.  Either: 'public', 'licensees', 'results only', 'restricted'
	'allocation method': str, #either 'no allocation', 'combined production without byproduct', 'combined production with byproduct', 'constrained market', 'economic allocation', 'true value allocation', 'recycling activity', 'waste treatment'
	'main reference product': str, #name of the reference product.  
	'last operation': str, #name of the function that last acted on this dataset
}
Master data:
{
	'intermediate exchange': {'id': {
		'name': str, 
		'unit': str, 
		'byproduct classification': str, #either 'allocatable', 'waste' or 'recyclable'
		}}
	'elementary exchange': {'id': {
		'name': str, 
		'compartment': str, 
		'subcompartment': str, 
		'unit': str, 
		}}
	'parameter': {'id': {
		'name': str, 
		'unit': str
		}}
	'property': {'id': {
		'name': str, 
		'unit': str
		}}
}