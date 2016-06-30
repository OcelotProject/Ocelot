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
            allocatedDatasets, logs = combinedProduction(dataset, logs, masterData)
            if dataset['allocation method'] == 'combinedProductionWithByProduct':
                allocatedDatasets, logs = mergeCombinedProductionWithByProduct(allocatedDatasets, logs)
        elif dataset['allocation method'] == 'economic allocation':
            dataset = find_economic_allocation_factors(dataset)
            new_datasets = allocate_with_factors(dataset)
        elif dataset['allocation method'] == 'trueValueAllocation':
            dataset = find_true_value_allocation_factors(dataset)
            new_datasets = allocate_with_factors(dataset)
        elif dataset['allocation method'] == 'waste treatment':
            new_datasets = waste_treatment(dataset)
        elif dataset['allocation method'] == 'recyclingActivity':
            allocatedDatasets, logs = recyclingActivity(dataset, logs, masterData)
        elif dataset['allocation method'] == 'constrainedMarket':
            allocatedDatasets, logs = constrainedMarketAllocation(dataset, logs)
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
        to_flip_indexes = tuple(to_flip[to_flip['data type'] == 'exchanges'].index)
        df.loc[to_flip_indexes, 'amount'] = -df.loc[to_flip_indexes, 'amount']
        if 'mathematical relation' in set(df.columns):
            s = set(df.loc[to_flip_indexes, 'mathematical relation'])
            s.difference_update(set([np.nan]))
            assert len(s) == 0 #the mathematical formula should be changed too
        
        #remove production volume for the flipped exchanges
        indexes = list(to_flip[to_flip['data type'] == 'production volume'].index)
        df = df.drop(indexes)
        
        dataset['data frame'] = df.copy()
        
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
        rows = 'exchange id', columns = ['property name'], aggfunc = np.sum)
    allocation_factors = allocation_factors[['price', 'true value relation'
        ]].set_index('exchange id')
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
    dataset['allocation factors'] = allocation_factors.copy().set_index('exchange id')
    
    return allocation_factors


def allocate_with_factors(dataset, new_datasets):
    '''create datasets from an unallocated dataset, with allocation factors calculated
    with economic or true value allocation'''
    
    allocation_factors = dataset['allocation factors']
    for chosen_product_exchange_id in list(allocation_factors.index):
        new_dataset = utils.make_reference_product(chosen_product_exchange_id, dataset)
        
        #multiply all exchange amounts by allocation factor, except reference product
        df = new_dataset['data frame'].copy()
        exchanges = df[df['data type'] == 'exchanges']
        indexes = list(exchanges.index)
        indexes.remove(new_dataset['main reference product index'])
        df.loc[indexes, 'amount'] = df.loc[indexes, 'amount'
            ] * allocation_factors.loc[chosen_product_exchange_id, 'allocation factor']
        new_dataset['data frame'] = df.copy()
        new_datasets.append(deepcopy(new_dataset))
    return new_datasets


def waste_treatment(dataset):
    
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