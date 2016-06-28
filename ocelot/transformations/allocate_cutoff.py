def allocate_datasets_cutoff(datasets, data_format, logger):
	'''a new list of datasets is created, all made single output by the right allocation method'''
	
	new_datasets = []
	for dataset in datasets:
		dataset['last operation'] = 'allocate_datasets'
		
		#create the data frame representation of the quantitative information of the dataset
		if 'data frame' not in dataset:
			dataset = ocelot.utils.internal_to_df(dataset, data_format)
		
		#flip non allocatable byproducts, if necessary
		dataset = flip_non_allocatable_byproducts(dataset)
		
		#allocate according to the previously determined method
		if dataset['allocation method'] == 'noAllocation':
			new_datasets.append(dataset)
		elif 'combined' in dataset['allocation method']:
			allocatedDatasets, logs = combinedProduction(dataset, logs, masterData)
			if dataset['allocation method'] == 'combinedProductionWithByProduct':
				allocatedDatasets, logs = mergeCombinedProductionWithByProduct(allocatedDatasets, logs)
		elif dataset['allocation method'] == 'economic allocation':
			dataset = find_economic_allocation_factors(dataset)
			new_datasets = allocate_with_factors(dataset, new_datasets)
		elif dataset['allocation method'] == 'trueValueAllocation':
			dataset = find_true_value_allocation_factors(dataset)
			new_datasets = allocate_with_factors(dataset, new_datasets)
		elif dataset['allocation method'] == 'wasteTreatment':
			allocatedDatasets, logs = wasteTreatment(dataset, logs, masterData)
		elif dataset['allocation method'] == 'recyclingActivity':
			allocatedDatasets, logs = recyclingActivity(dataset, logs, masterData)
		elif dataset['allocation method'] == 'constrainedMarket':
			allocatedDatasets, logs = constrainedMarketAllocation(dataset, logs)
		else:
			raise NotImplementedError('"%s" is not a recognized allocationMethod')
			#each dataset has to be scaled, remove unnecessary info
		
	return datasets

	
def flip_non_allocatable_byproducts(dataset):
	'''makes the non-allocatable byproducts an input from technosphere.  Sign has to be changed.'''
	
    #all waste in byproduct should be labeled FromTechnosphere
	#this includes also their production volume and properties
	df = dataset['data frame'].copy()
    to_flip = df[df['exchange type'] == 'byproduct']
    to_flip = to_flip[to_flip['classification'].isin(['waste', 'recyclable'])]
	if len(to_flip) > 0:
		to_flip_indexes = list(to_flip.index)
		df.loc[to_flip_indexes, 'exchange type'] = 'from technosphere'
		
		#only the exchange amounts should have their sign changed
		to_flip = to_flip[to_flip['data type'] == 'exchanges']
		to_flip_indexes = list(to_flip.index)
		df.loc[to_flip_indexes, 'amount'] = -df.loc[to_flip_indexes, 'amount']
		
		dataset['data frame'] = df.copy()
	
    return dataset

	
def select_exchanges_to_technosphere(df):
	'''selects only the lines of the data frame with an exchange amount to technosphere'''
	
    sel = df[df['data type'] == 'exchanges']
    sel = sel[sel['exchange type'].isin(['byproduct', 'reference product'])]
	
    return sel

	
def find_economic_allocation_factors(dataset):
	
    #selecting only prices of allocatable outputs to technosphere
	df = dataset['data frame']
    allocation_factors = df[df['property name'] == 'price']
	allocation_factors = allocation_factors[allocation_factors[
        'byproduct classification'] == 'allocatable']
	allocation_factors = allocation_factors[allocation_factors['exchange type'
		].isin(['reference product', 'byproduct'])]
    allocation_factors = allocation_factors.rename(columns = {'amount': 'price'})
	allocation_factors = allocation_factors[['price']].set_index('exchange id')
    
    #join the exchange amounts
	sel = ocelot.utils.select_exchanges_to_technosphere(df).set_index(
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
	dataset['allocation factors'] = allocation_factors.copy().set_index('exchange id')
	
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
	allocation_factors = allocation_factors.rename(columns = 'true value relation': 'TVR')
	
	#join the exchange amounts
	sel = ocelot.utils.select_exchanges_to_technosphere(df).set_index(
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
	
    #extract once exchanges and exchanges to technosphere indexes for convenience
	df = dataset['data frame'].copy()
    exchanges = df[df['data type'] == 'exchanges']
	allocation_factors = dataset['allocation factors']
    for chosen_product_exchange_id in list(allocation_factors.index):
        new_dataset = make_reference_product(chosen_product_exchange_id, dataset)
		
        #multiply all exchange amounts by allocation factor, except reference product
        indexes = list(exchanges.index)
        indexes.remove(new_dataset['main reference product index'])
		df = new_dataset['data frame'].copy()
        df.loc[indexes, 'amount'] = df.loc[indexes, 'amount'
            ] * allocation_factors.loc[chosen_product_exchange_id, 'allocation factor']
		new_dataset['data frame'] = df.copy()
        new_datasets.append(new_dataset)
    return new_datasets


def make_reference_product(chosen_product_exchange_id, dataset):
	
    #find new reference product
	df = dataset['data frame']
    exchanges_to_technosphere = select_exchanges_to_technosphere(df)
	sel = exchanges_to_technosphere[
        exchanges_to_technosphere['exchange id'] == chosen_product_exchange_id].iloc[0]
    
	#add new reference product to metainformation
    dataset['main reference product'] = sel['exchange name']
    dataset['main reference product index'] = sel['exchange name'].index
    
    #put to zero the amount of the other coproducts
    indexes = list(exchanges_to_technosphere.index)
    indexes.remove(sel['exchange name'].index)
	allocated_df = df.copy()
    allocated_df.loc[indexes, 'amount'] = 0.
	
    #make the selected coproduct the reference product
    indexes = allocated_df[allocated_df['exchange id'
        ] == chosen_product_exchange_id]
    indexes = indexes[indexes['exchange type'
        ].isin(['reference product', 'byproduct'])]
    indexes = list(indexes.index)
	
	#remove the production volume of the other outputs to technosphere
    allocated_df.loc[indexes, 'exchange type'] = 'reference product'
    conditions = ~((allocated_df['data type'] == 'production volume') & (
        allocated_df['exchange type'] != 'reference product'))
    allocated_df = allocated_df[conditions]
	
	dataset['data frame'] = allocated_df.copy()
	
    return dataset