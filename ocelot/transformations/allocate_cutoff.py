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
            'extract_ecospold2'])
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
        for dataset in new_datasets:
            dataset = utils.scale_exchanges(dataset)
            allocated_datasets.append(dataset)
    
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
    if dataset['allocation method'] in ['economic allocation', 'recycling activity']:
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
    dataset['allocation factors'] = df.copy()
    
    return dataset
	
def find_allocation_factors(dataset):
    df = dataset['allocation factors'].copy()
    
    #calculate revenu
    dataset['allocation factors']['revenu'] = abs(df['price'] * df['amount'])
    
    if dataset['allocation method'] in ['economic allocation', 'recycling activity']:
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
        new_dataset = utils.make_reference_product(reference_product_name, dataset)
        factor = df.loc[reference_product_name, 'allocation factor']
        
        #multiply all exchange amounts by allocation factor, except reference product
        for exc in new_dataset['exchanges']:
            if exc['type'] != 'reference product':
                exc['amount'] = exc['amount'] * factor
        
        new_datasets.append(deepcopy(new_dataset))
        
    return new_datasets


def waste_treatment_allocation(dataset):
    
    #first allocated dataset: the treatment of the waste
    new_datasets = [utils.make_reference_product(dataset['reference product'], dataset)]
    
    #potential byproducts
    for bp in dataset['exchanges']:
        if bp['type'] == 'byproduct' and bp['amount'] != 0.:
            new_dataset = utils.make_reference_product(bp['name'], dataset)
            for exc in new_dataset['exchanges']:
                #put to zero all the other exchanges
                exc['amount'] = 0.
            new_datasets.append(new_dataset)
    
    return new_datasets


def constrained_market_allocation(dataset):
    '''in this case, the conditional exchange is removed.  Done by simply using the 
    utils.make_reference_product function'''
    
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
    #are recyclable not supposed to be allocated anything?
    dataset = copy(dataset)
    df = dataset['data frame'].copy()
    
    #establish relationship between variables with a graph matrix
    dataset = utils.build_graph(dataset, combined = True)
    
    #find the recalculation order with the graph
    dataset = utils.calculation_order(dataset)
    
    df = dataset['data frame']
    new_datasets = []
    
    #select the reference products
    sel = df[df['exchange type'] == 'reference product']
    reference_products_ids = list(sel[sel['data type'] == 'exchanges']['exchange id'])
    
    #for each reference product
    for chosen_product_exchange_id in reference_products_ids:
        df = dataset['data frame']
        #do not allocate for child datasets that have the reference product already set to zero
        exchanges_to_technosphere = utils.select_exchanges_to_technosphere(df)
        sel = exchanges_to_technosphere[
            exchanges_to_technosphere['exchange id'] == chosen_product_exchange_id].iloc[0]
        if sel['amount'] != 0.:
            new_dataset = utils.make_reference_product(chosen_product_exchange_id, dataset)
            new_dataset = utils.recalculate(new_dataset)
            df = new_dataset['data frame']
            if df.loc[new_dataset['main reference product index'], 'amount'] != 0. or True:
                df['amount'] = df['calculated amount'].copy()
                del df['calculated amount']
                new_dataset['data frame'] = df.copy()
                new_datasets.append(new_dataset)
    
    return new_datasets


def allocate_after_subdivision(undefined_dataset, datasets):
    
    #PV get erased in the process, but can be retrieved from the undefined dataset
    for_PV = undefined_dataset['data frame'].copy()
    for_PV = for_PV[for_PV['data type'] == 'produciton volume']
    #each dataset needs to be allocated
    allocated_dataset_ungrouped = []
    for dataset in datasets:
        dataset = find_economic_allocation_factors(dataset)
        to_add = allocate_with_factors(dataset)
        allocated_dataset_ungrouped.extend(to_add)
    
    #grouping of datasets with the same reference product
    allocated_dataset_grouped = {}
    for dataset in allocated_dataset_ungrouped:
        if dataset['main reference product'] not in allocated_dataset_grouped:
            allocated_dataset_grouped[dataset['main reference product']] = []
        allocated_dataset_grouped[dataset['main reference product']].append(dataset)
    
    new_datasets = []
    for reference_product in allocated_dataset_grouped:
        if len(allocated_dataset_grouped[reference_product]) == 1:
            #nothing to merge
            new_datasets.append(allocated_dataset_grouped[reference_product][0])
        else:
            #put exchanges and produciton volume in the same data frame
            to_merge = []
            for dataset in allocated_dataset_grouped[reference_product]:
                df = dataset['data frame'].copy()
                df = df[df['data type'] == 'exchanges']
                to_merge.append(df)
            to_merge = pd.concat(to_merge)
            
            #add the amounts of the same exchanges
            merged = pd.pivot_table(to_merge, values = ['amount'], 
                index = ['Ref'], aggfunc = np.sum)
            
            #put back the amounts in the data frame with all the information
            df = df.set_index('Ref')
            cols = list(df.columns)
            cols.remove('amount')
            cols.remove('length')
            cols.remove('calculation order')
            merged = df[cols].join(merged)
            
            #add parameters, properties and production volumes
            df = dataset['data frame'].copy()
            df = df[df['data type'].isin(['properties', 'parameters'])]
            merged = pd.concat([merged.reset_index(), df, 
                for_PV[for_PV['exchange name'] == reference_product]])
            new_dataset = copy(dataset)
            new_dataset['data frame'] = merged.copy()
            new_dataset = utils.reset_index_df(new_dataset)
            
            new_datasets.append(new_dataset)
    
    return new_datasets