# -*- coding: utf-8 -*-
def find_allocation_method(data, logger):
    """Finds the allocation method, based on a few characteristics of outputs to technosphere"""
    
    #initializing some variables
    nb_reference_products = 0
    nb_allocatable_byproducts = 0
    has_conditional_exchange = False
    has_true_value = False
    
    #gathering the necessary information to find the allocation method
    for exc in data['exchanges']:
        if exc['amount'] != 0.:
            if exc['type'] == 'reference product':
                nb_reference_products += 1
                if exc['amount'] < 0.:
                    reference_product_amount_sign = -1
                else:
                    reference_product_amount_sign = 1
                reference_product_classification = exc['byproduct classification']
            elif exc['type'] == 'byproduct':
                nb_allocatable_byproducts += 1
                if 'activity link' in exc and data['type'] == 'market activity' and exc['amount'] < 0.:
                    has_conditional_exchange = True
            if 'properties' in exc and 'true value relation' in exc['properties']:
                has_true_value = True
    
    #settin the allocation method
    if data['type'] == 'market group':
        data['allocation method'] = 'no allocation'
    elif data['type'] == 'market activity':
        if has_conditional_exchange:
            data['allocation method'] = 'constrained market'
        else:
            data['allocation method'] = 'no allocation'
    else:
        if nb_reference_products + nb_allocatable_byproducts == 1:
            data['allocation method'] = 'no allocation'
        elif nb_reference_products > 1:
            if nb_allocatable_byproducts > 0:
                data['allocation method'] = 'combined production with byproducts'
            else:
                data['allocation method'] = 'combined production without byproducts'
        elif reference_product_amount_sign == 1:
            if has_true_value:
                data['allocation method'] = 'true value allocation'
            else:
                data['allocation method'] = 'economic allocation'
        else:
            if reference_product_classification == 'waste':
                data['allocation method'] = 'waste treatment'
            else:
                data['allocation method'] = 'recycling activity'
    
    #removing superfluous information from the dataset
    if not 'combined' in data['allocation method']:
        del data['parameters'] #parameters are only useful in the case of combined production
        for i in range(len(data['exchanges'])):
            #mathematical relation and variable names not necessary
            del data['exchanges'][i]['mathematical relation']
            del data['exchanges'][i]['variable']
            if 'properties' in data['exchanges'][i]:
                properties_to_keep = []
                if data['allocation method'] in ['recycling activity', 'economic allocation']:
                    properties_to_keep = ['price']
                elif data['allocation method'] in ['true value allocation']:
                    properties_to_keep = ['price', 'true value relation']
                #deleting unnecessary properties, mathematical relation and variable
                for property_name in data['exchanges'][i]['properties']:
                    if property_name not in properties_to_keep:
                        del data['exchanges'][i]['properties'][property_name]
                    else:
                        del data['exchanges'][i]['properties'][property_name]['mathematical relation']
                        del data['exchanges'][i]['properties'][property_name]['variable']
    
    return data
