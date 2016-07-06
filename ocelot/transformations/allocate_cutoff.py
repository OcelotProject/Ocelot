# -*- coding: utf-8 -*-
import pandas as pd
from copy import copy, deepcopy
import numpy as np
from .. import utils

def dummy():
    return ''
		
def allocate_datasets_cutoff(datasets, data_format, logger):
    '''a new list of datasets is created, all made single output by the right allocation method'''
    allocated_datasets = []
    
    for dataset in datasets:
        print(dataset['name'], dataset['location'])
        dataset['last operation'] = 'allocate_datasets'
        
        #create the data frame representation of the quantitative information of the dataset
        if 'data frame' not in dataset:
            dataset = utils.internal_to_df(dataset, data_format)
        
        #flip non allocatable byproducts, if necessary
        dataset = flip_non_allocatable_byproducts(dataset)
        
        #allocate according to the previously determined method
        if dataset['allocation method'] == 'no allocation':
            new_datasets = [dataset]
        elif 'combined' in dataset['allocation method']:
            new_datasets = combined_production(dataset)
            if dataset['allocation method'] == 'combined production with byproducts':
                new_datasets = allocate_after_subdivision(dataset, new_datasets)
        elif dataset['allocation method'] == 'economic allocation':
            dataset = find_economic_allocation_factors(dataset)
            new_datasets = allocate_with_factors(dataset)
        elif dataset['allocation method'] == 'true value allocation':
            dataset = find_true_value_allocation_factors(dataset)
            new_datasets = allocate_with_factors(dataset)
        elif dataset['allocation method'] == 'waste treatment':
            new_datasets = waste_treatment_allocation(dataset)
        elif dataset['allocation method'] == 'recycling activity':
            new_datasets = recycling_activity_allocation(dataset)
        elif dataset['allocation method'] == 'constrained market':
            new_datasets = constrained_market_allocation(dataset)
        else:
            raise NotImplementedError('"%s" is not a recognized allocationMethod')
        
        #each dataset has to be scaled
        for dataset in new_datasets:
            dataset = utils.scale_exchanges(dataset)
        allocated_datasets.extend(new_datasets)
    return allocated_datasets

	
def flip_non_allocatable_byproducts(dataset):
    '''makes the non-allocatable byproducts an input from technosphere.  Sign has to be changed.'''
    
    
    df = dataset['data frame'].copy()
    to_technosphere = utils.select_exchanges_to_technosphere(df)
    to_flip = to_technosphere[to_technosphere['exchange type'] == 'byproduct']
    to_flip = to_flip[to_flip['byproduct classification'].isin(['waste', 'recyclable'])]
    if len(to_flip) > 0:
        #set the exchange type to "from technosphere" for all exchange amount and properties
        exchange_names = set(df.loc[list(tuple(to_flip.index))]['exchange name'])
        to_flip = df[df['exchange type'] == 'byproduct']
        to_flip = to_flip[to_flip['exchange name'].isin(exchange_names)]
        to_flip_indexes = tuple(to_flip.index)
        df.loc[to_flip_indexes, 'exchange type'] = 'from technosphere'
        
        #only the exchange amounts should have their sign changed
        to_flip_indexes = list(to_flip[to_flip['data type'] == 'exchanges'].index)
        df.loc[to_flip_indexes, 'amount'] = -df.loc[to_flip_indexes, 'amount']
        
        #check if mathematical relations have to be changed because of flipping
        if 'mathematical relation' in set(df.columns):
            indexes = df.loc[to_flip_indexes]
            if len(indexes) > 0:
                indexes = list(indexes[~indexes['mathematical relation'
                        ].apply(utils.is_empty)].index)
            if len(indexes) > 0:
                df.loc[indexes, 'mathematical relation'] = df.loc[
                    indexes, 'mathematical relation'].apply(
                    lambda m: '-(%s)' % m)
        
        #remove production volume for the flipped exchanges
        indexes = list(to_flip[to_flip['data type'] == 'production volume'].index)
        df = df.drop(indexes)
        
        dataset['data frame'] = df.copy()
        dataset = utils.reset_index_df(dataset)
    return dataset

	
def find_economic_allocation_factors(dataset):
    #selecting only prices of allocatable outputs to technosphere
    df = dataset['data frame']
    allocation_factors = df[df['property name'] == 'price']
    allocation_factors = allocation_factors[allocation_factors[
        'byproduct classification'] == 'allocatable']
    allocation_factors = allocation_factors[allocation_factors['exchange type'
        ].isin(['reference product', 'byproduct'])]
    allocation_factors = allocation_factors.rename(columns = {'amount': 'price'})
    allocation_factors = allocation_factors[['price', 'exchange id']].set_index('exchange id')
    
    #join the exchange amounts
    sel = utils.select_exchanges_to_technosphere(df).set_index(
        'exchange id')[['exchange name', 'amount']]
    allocation_factors = allocation_factors.join(sel)
    
    #calculate revenu
    allocation_factors['revenu'] = abs(allocation_factors['price'
        ] * allocation_factors['amount'])
        
    #calculate allocation factors
    allocation_factors['allocation factor'] = allocation_factors['revenu'
        ] / allocation_factors['revenu'].sum()
        
    #remove allocation factors equal to zero
    allocation_factors = allocation_factors[allocation_factors['allocation factor'] != 0.]
    
    #calculate allocation factors
    dataset['allocation factors'] = allocation_factors.copy()
    
    return dataset


def find_true_value_allocation_factors(dataset):
    
    #select price and true value relation properties
    df = dataset['data frame']
    allocation_factors = df[df['property name'].isin(['price', 'true value relation'])]
    allocation_factors = allocation_factors[allocation_factors[
        'byproduct classification'] == 'allocatable']
    allocation_factors = allocation_factors[allocation_factors['exchange type'
        ].isin(['reference product', 'byproduct'])]
    allocation_factors = pd.pivot_table(allocation_factors, values = 'amount', 
        index = 'exchange id', columns = ['property name'], aggfunc = np.sum)
    allocation_factors = allocation_factors[['price', 'true value relation']]
    allocation_factors = allocation_factors.rename(columns = {'true value relation': 'TVR'})
    
    #join the exchange amounts
    sel = utils.select_exchanges_to_technosphere(df).set_index(
        'exchange id')[['exchange name', 'amount']]
    allocation_factors = allocation_factors.join(sel)
    
    #put to zero TVR if it was not there for some exchanges
    allocation_factors = allocation_factors.replace(to_replace = {
        'TVR': {np.nan: 0.}})
        
    #calculate revenu
    allocation_factors['revenu'] = abs(allocation_factors['price'
        ] * allocation_factors['amount'])
    
    #calculate true value for exchange with TVR
    price_only_exchanges = allocation_factors[allocation_factors['TVR'] == 0.]
    allocation_factors = allocation_factors[allocation_factors['TVR'] != 0.]
    allocation_factors['amount*TVR'] = allocation_factors['TVR'] * allocation_factors['amount']
    allocation_factors['amount*TVR/sum(amount*TVR)'] = allocation_factors['amount*TVR'] / allocation_factors['amount*TVR'].sum()
    allocation_factors['TV'] = allocation_factors['amount*TVR/sum(amount*TVR)'] * (
        allocation_factors['revenu'].sum() / allocation_factors['amount*TVR'].sum())
    
    #calculate true value for exchange without TVR, if any
    if len(price_only_exchanges) > 0:
        price_only_exchanges['TV'] = price_only_exchanges['revenu'].copy()
        allocation_factors = pd.concat([allocation_factors, price_only_exchanges])
    allocation_factors['allocation factor'] = allocation_factors['TV'
        ] / allocation_factors['TV'].sum()
        
    #calculate allocation factors
    dataset['allocation factors'] = allocation_factors.copy()
    
    return dataset


def allocate_with_factors(dataset):
    '''create datasets from an unallocated dataset, with allocation factors calculated
    with economic or true value allocation'''
    
    allocation_factors = dataset['allocation factors']
    new_datasets = []
    for chosen_product_exchange_id in list(allocation_factors.index):
        new_dataset = utils.make_reference_product(chosen_product_exchange_id, dataset)
        #multiply all exchange amounts by allocation factor, except reference product
        df = new_dataset['data frame']
        exchanges = df[df['data type'] == 'exchanges'].copy()
        indexes = list(exchanges.index)
        indexes.remove(new_dataset['main reference product index'])
        df.loc[indexes, 'amount'] = df.loc[indexes, 'amount'
            ] * allocation_factors.loc[chosen_product_exchange_id, 'allocation factor']
        new_dataset['data frame'] = df.copy()
        new_datasets.append(deepcopy(new_dataset))
        
    return new_datasets


def waste_treatment_allocation(dataset):
    
    #first allocated dataset: the treatment of the waste
    dataset = copy(dataset)
    df = dataset['data frame']
    exchanges_to_technosphere = utils.select_exchanges_to_technosphere(df)
    sel = exchanges_to_technosphere[exchanges_to_technosphere[
        'exchange type'] == 'reference product']
    chosen_product_exchange_id = sel.iloc[0]['exchange id']
    new_dataset = utils.make_reference_product(chosen_product_exchange_id, dataset)
    new_datasets = [new_dataset]
    by_products = exchanges_to_technosphere[exchanges_to_technosphere[
            'exchange type'] == 'byproduct']
    if len(by_products) > 0:
        #put to zero all the other exchanges
        indexes = set(df[df['data type'] == 'exchanges'].index)
        indexes.difference_update(set(by_products.index))
        df.loc[indexes, 'amount'] = 0.
        dataset['data frame'] = df.copy()
        
        #create a new dataset for each byproduct
        for chosen_product_exchange_id in set(by_products['exchange id']):
            new_datasets.append(utils.make_reference_product(chosen_product_exchange_id, dataset))
    
    return new_datasets


def constrained_market_allocation(dataset):
    '''in this case, the conditional exchange is removed.  Done by simply using the 
    utils.make_reference_product function'''
    
    sel = utils.select_exchanges_to_technosphere(dataset['data frame'])
    chosen_product_exchange_id = sel[sel['exchange type'] == 'reference product'
        ].iloc[0]['exchange id']
    new_datasets = [utils.make_reference_product(chosen_product_exchange_id, dataset)]
    
    return new_datasets


def recycling_activity_allocation(dataset):
    dataset = copy(dataset)
    df = dataset['data frame']
    #flip the reference product to FromTechnosphere
    indexes = list(tuple(df[df['exchange type'] == 'reference product'].index))
    df.loc[indexes, 'exchange type'] = 'from technosphere'
    index = tuple(df[df['data type'] == 'exchanges'].index)[0]
    df.loc[index, 'amount'] = -df.loc[index, 'amount']
    
    exchanges_to_technosphere = utils.select_exchanges_to_technosphere(dataset['data frame'])
    if len(exchanges_to_technosphere) == 1:
        #no allocation required
        chosen_product_exchange_id = exchanges_to_technosphere.iloc[0]['exchange id']
        new_datasets = [utils.make_reference_product(chosen_product_exchange_id, dataset)]
    else:
        dataset['data frame'] = df.copy()
        sel = df[df['exchange type'] == 'byproduct']
        if 'true value relation' in set(sel['property name']):
            #true value allocation.  Does not happen, but would work
            dataset = find_true_value_allocation_factors(dataset)
        else:
            #economic allocation
            dataset = find_economic_allocation_factors(dataset)
        new_datasets = allocate_with_factors(dataset)
    return new_datasets


def combined_production(dataset):
    
    #are recyclable not supposed to be allocated anything?
    dataset = copy(dataset)
    
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
        new_dataset = utils.make_reference_product(chosen_product_exchange_id, dataset)
        new_dataset = utils.recalculate(new_dataset)
        df = new_dataset['data frame']
        if df.loc[new_dataset['main reference product index'], 'amount'] != 0.:
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