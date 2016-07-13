# -*- coding: utf-8 -*-
import pandas as pd
from copy import copy, deepcopy
import numpy as np
from .. import utils
import time
def dummy():
    return ''
		
def allocate_datasets_cutoff(datasets, data_format, logger):
    '''a new list of datasets is created, all made single output by the right allocation method'''
    allocated_datasets = []
    counter = 0
    for dataset in datasets:
        assert set(dataset['history'].keys()) == set([
            'find_allocation_method_cutoff', 'fix_known_issues_ecoinvent_32', 
            'extract_ecospold2', 'calculate_available_PV'])
        counter += 1
        print(dataset['name'], dataset['location'])
        print(counter, 'of', len(datasets))
        dataset['history']['allocate_cutoff'] = time.ctime()
        
        #flip non allocatable byproducts, if necessary
        dataset = flip_non_allocatable_byproducts(dataset)
        
        #allocate according to the previously determined method
        if dataset['allocation method'] == 'no allocation':
            new_datasets = [dataset]
        elif 'combined' in dataset['allocation method']:
            new_datasets = combined_production(dataset)
            if dataset['allocation method'] == 'combined production with byproducts':
                new_datasets = allocate_after_subdivision(dataset, new_datasets)
        elif dataset['allocation method'] in ['economic allocation', 'true value allocation']:
            dataset = info_for_allocation_factor(dataset)
            dataset = find_allocation_factors(dataset)
            new_datasets = allocate_with_factors(dataset)
        elif dataset['allocation method'] == 'waste treatment':
            new_datasets = waste_treatment_allocation(dataset)
        elif dataset['allocation method'] == 'recycling activity':
            new_datasets = recycling_activity_allocation(dataset)
        elif dataset['allocation method'] == 'constrained market':
            new_datasets = constrained_market_allocation(dataset)
        else:
            raise NotImplementedError('"%s" is not a recognized allocationMethod')
        
        #each dataset has to be scaled, then put back to the internal format
        for new_dataset in new_datasets:
            new_dataset = utils.scale_exchanges(new_dataset)
            allocated_datasets.append(new_dataset)
    
    return allocated_datasets

	
def flip_non_allocatable_byproducts(dataset):
    '''makes the non-allocatable byproducts an input from technosphere.  Sign has to be changed.'''
    
    for exc in dataset['exchanges']:
        if exc['type'] == 'byproduct' and exc['byproduct classification'] != 'allocatable':
            exc['type'] = 'from technosphere'
            exc['amount'] = -exc['amount']
            if 'mathematical relation' in exc:
                exc['mathematical relation'] = '-(%s)' % exc['mathematical relation']
            del exc['production volume']
    
    return dataset


def info_for_allocation_factor(dataset):
    if dataset['allocation method'] in ['economic allocation', 
            'recycling activity', 'combined production with byproducts']:
        properties = ['price']
    elif dataset['allocation method'] == 'true value allocation':
        properties = ['price', 'true value relation']
    df = {}
    for exc in dataset['exchanges']:
        if exc['type'] in ['reference product', 'byproduct']:
            to_add = {'name': exc['name'], 
                      'amount': exc['amount']}
            for p in exc['properties']:
                if p['name'] in properties:
                    to_add[p['name']] = p['amount']
            df[len(df)] = copy(to_add)
    df = pd.DataFrame(df).transpose()
    df['revenu'] = df['amount'] * df['price']
    
    dataset['allocation factors'] = df.copy()
    
    return dataset
	
def find_allocation_factors(dataset):
    df = dataset['allocation factors'].copy()
    df = df.rename(columns = {'true value relation': 'TVR'})
    
    #calculate revenu
    dataset['allocation factors']['revenu'] = abs(df['price'] * df['amount'])
    
    if dataset['allocation method'] in ['economic allocation', 
            'recycling activity', 'combined production with byproducts']:
        #calculate allocation factors
        df['allocation factor'] = df['revenu'] / df['revenu'].sum()
    elif dataset['allocation method'] == 'true value allocation':
        #put to zero TVR if it was not there for some exchanges
        df = df.replace(to_replace = {'TVR': {np.nan: 0.}})
        
        #calculate true value for exchange with TVR
        TV_exchanges = df[df['TVR'] != 0.]
        TV_exchanges['amount*TVR'] = TV_exchanges['TVR'] * TV_exchanges['amount']
        TV_exchanges['amount*TVR/sum(amount*TVR)'] = TV_exchanges['amount*TVR'] / TV_exchanges['amount*TVR'].sum()
        TV_exchanges['TV'] = TV_exchanges['amount*TVR/sum(amount*TVR)'] * (
            TV_exchanges['revenu'].sum() / TV_exchanges['amount*TVR'].sum())
        
        #calculate true value for exchange without TVR, if any
        price_only_exchanges = df[df['TVR'] == 0.]
        if len(price_only_exchanges) > 0:
            price_only_exchanges['TV'] = price_only_exchanges['revenu'].copy()
            df = pd.concat([TV_exchanges, price_only_exchanges])
        else:
            df = TV_exchanges.copy()
        df['allocation factor'] = df['TV'] / df['TV'].sum()
    
    #remove allocation factors equal to zero
    df = df[df['allocation factor'] != 0.]
    dataset['allocation factors'] = df.set_index('name')
    
    return dataset


def allocate_with_factors(dataset):
    '''create datasets from an unallocated dataset, with allocation factors calculated
    with economic or true value allocation'''
    
    df = dataset['allocation factors']
    new_datasets = []
    for reference_product_name in list(df.index):
        new_dataset = utils.make_reference_product(reference_product_name, copy(dataset))
        factor = df.loc[reference_product_name, 'allocation factor']
        
        #multiply all exchange amounts by allocation factor, except reference product
        for exc in new_dataset['exchanges']:
            if exc['type'] != 'reference product':
                exc['amount'] = exc['amount'] * factor
        
        new_datasets.append(new_dataset)
        
    return new_datasets


def waste_treatment_allocation(dataset):
    
    #first allocated dataset: the treatment of the waste
    new_datasets = [utils.make_reference_product(dataset['reference product'], dataset)]
    
    #potential byproducts
    for bp in dataset['exchanges']:
        if bp['type'] == 'byproduct' and bp['amount'] != 0.:
            new_dataset = utils.make_reference_product(bp['name'], dataset)
            new_datasets.append(new_dataset)
    
    #those come for free in cut-off
    for new_dataset in new_datasets:
        for exc in new_dataset['exchanges']:
            if exc['type'] != 'reference product':
                #put to zero all the other exchanges
                exc['amount'] = 0.
    
    return new_datasets


def constrained_market_allocation(dataset):
    '''in this case, the conditional exchange is removed.'''
    #The use of the function flip_non_allocatable_byproducts has made the conditional exchange
    new_datasets = [utils.make_reference_product(dataset['reference product'], dataset)]
    
    return new_datasets


def recycling_activity_allocation(dataset):
    
    #flip the reference product to from technosphere
    for exc in dataset['exchanges']:
        if exc['type'] == 'reference product':
            exc['type'] = 'from technosphere'
            exc['amount'] = -exc['amount']
    
    #find allocation factors
    #if there is only one byproduct left, the allocation factor will be 100% and only one
    #dataset will be created
    dataset = info_for_allocation_factor(dataset)
    dataset = find_allocation_factors(dataset)
    new_datasets = allocate_with_factors(dataset)
    
    return new_datasets


def combined_production(dataset):
    dataset = copy(dataset)
    
    #establish relationship between variables with a graph matrix
    dataset = utils.build_graph(dataset, combined = True)
    
    #find the recalculation order with the graph
    dataset = utils.calculation_order(dataset)
    
    new_datasets = []
    
    #for each reference product
    for exc in dataset['exchanges']:
        if exc['type'] == 'reference product' and exc['amount'] != 0.:
            #do not allocate for child datasets that have the reference product already set to zero
            new_dataset = utils.make_reference_product(exc['name'], dataset)
            new_dataset = utils.recalculate(new_dataset)
            df = new_dataset['quantity data frame']
            df['amount'] = df['calculated amount'].copy()
            del df['calculated amount']
            new_dataset['quantity data frame'] = df.copy()
            new_dataset = utils.quantity_df_to_internal(new_dataset)
            new_datasets.append(new_dataset)
    
    return new_datasets


def allocate_after_subdivision(undefined_dataset, datasets):
    
    #each dataset needs to be allocated.  
    #datasets with the same reference product are grouped
    allocated_dataset_grouped = {}
    for dataset in datasets:
        dataset = info_for_allocation_factor(dataset)
        dataset = find_allocation_factors(dataset)
        new_datasets = allocate_with_factors(dataset)
        for new_dataset in new_datasets:
            if new_dataset['reference product'] not in allocated_dataset_grouped:
                allocated_dataset_grouped[new_dataset['reference product']] = []
            allocated_dataset_grouped[new_dataset['reference product']].append(new_dataset)
    
    
    new_datasets = []
    for reference_product in allocated_dataset_grouped:
        if len(allocated_dataset_grouped[reference_product]) == 1:
            #nothing to merge
            new_datasets.append(allocated_dataset_grouped[reference_product][0])
        else:
            #put exchanges and produciton volume in the same data frame
            to_merge = []
            for dataset in allocated_dataset_grouped[reference_product]:
                dataset = utils.build_quantity_df(dataset)
                to_merge.append(dataset['quantity data frame'].copy())
            to_merge = pd.concat(to_merge)
            
            #add the amounts of the same exchanges
            merged = pd.pivot_table(to_merge, values = ['amount'], 
                index = ['Ref'], aggfunc = np.sum)
            undefined_dataset['quantity data frame'] = merged.reset_index()
            new_dataset = utils.quantity_df_to_internal(undefined_dataset)
            new_dataset = utils.make_reference_product(reference_product, dataset)
            
            #fetch production volume info from pre-allocation dataset
            for exc in new_dataset['exchanges']:
                if exc['name'] == new_dataset['reference product'] and exc[
                        'type'] == 'reference product':
                    for exc_ in undefined_dataset['exchanges']:
                        if exc_['name'] == new_dataset['reference product'] and exc_[
                                'type'] == 'reference product':
                            exc['production volume'] = exc_['production volume']
                            break
                    break
            new_datasets.append(new_dataset)
    
    return new_datasets