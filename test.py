# -*- coding: utf-8 -*-
import ocelot
from copy import copy
import numpy as np
import scipy as sp
import pandas as pd
import os
import time

if 1:
    folder = r'C:\python\DB_versions\3.2\undefined\datasets'
    datasets = ocelot.io.extract_ecospold2.extract_directory(folder, False)
    filename = 'ecoinvent_3.2_internal'
    folder = r'C:\ocelot_DB'
    logger = ''
    datasets = ocelot.transformations.find_allocation_method_cutoff.allocation_method(datasets, logger)
    datasets = ocelot.transformations.fix_known_issues_ecoinvent_32.fix_known_issues(
        datasets, '')
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    data_format = ocelot.utils.read_format_definition()
    if 0:
        ocelot.transformations.activity_overview.build_activity_overview(datasets, 
            support_excel_folder, support_pkl_folder, data_format)
    ocelot.utils.save_file(datasets, folder, filename)
    datasets = datasets[:100]
    filename = 'ecoinvent_3.2_internal_small'
    ocelot.utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    #filename = 'ecoinvent_3.2_internal'
    filename = 'ecoinvent_3.2_internal_after_allocation'
    #filename = 'after_allocation_treatment_and_recycling'
    #filename = 'after_combined_production_with_byproducts'
    #filename = 'ecoinvent_3.2_internal_small'
    #filename = 'after_economic_allocation'
    #filename = 'after_true_value_allocation'
    datasets = ocelot.utils.open_file(folder, filename)
    data_format = ocelot.utils.read_format_definition()
    criteria = {
        'allocation method': [
            'recycling activity', 
              'waste treatment'
              ], 
        #'activity name': ['petroleum refinery operation'], 
        #'location': ['GLO'], 
                }
    #datasets = ocelot.utils.filter_datasets(datasets, activity_overview, criteria)
    if 0:
        datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
            datasets, data_format, '')
        folder = 'C:\ocelot_DB'
        filename = 'ecoinvent_3.2_internal_after_allocation'
        ocelot.utils.save_file(datasets, folder, filename)
    #ocelot.utils.print_dataset_to_excel(dataset, folder, data_format, activity_overview)
    
    #for PV calculation
    #first, an activity link overview is required
    
    support_pkl_folder = r'C:\ocelot_DB'
    activity_overview = ocelot.utils.open_file(support_pkl_folder, 'activity_overview')
    if list(activity_overview.index.names) != ['activity id', 'exchange name']:
        activity_overview = activity_overview.set_index(['activity id', 'exchange name']
            ).sortlevel(level=0)
    activity_link_overview = {}
    if not list(data_format.index.names) == ['parent', 'in data frame']:
        data_format = data_format[~data_format['in data frame'].apply(ocelot.utils.is_empty)]
        data_format = data_format.set_index(['parent', 'in data frame']).sortlevel(level=0)
    for dataset in datasets:
        assert 'allocate_cutoff' in dataset['history'].keys()
        ref_exc = ocelot.utils.get_reference_product(dataset)
        if 'production volume' in ref_exc and ref_exc['production volume']['amount'] != 0.:
            for exc in dataset['exchanges']:
                if 'activity link' in exc and exc['type'] != 'reference product': # why link in RP?
                    sel = activity_overview.loc[(exc['activity link'], exc['name'])]
                    if type(sel) == pd.core.frame.DataFrame:
                        sel = sel.iloc[0]
                    to_add = {'activity name': dataset['name'], 
                              'location': dataset['location'], 
                        'reference product': dataset['main reference product'], 
                        'exchange name': exc['name'], 
                        'amount': exc['amount'], 
                        'activity link activity name': sel['activity name'], 
                        'activity link location': sel['location']
                        }
                    to_add['consumed amount'] = abs(to_add['amount'] / ref_exc['amount'
                        ] * ref_exc['production volume']['amount'])
                    if exc['activity link'] == dataset['id']:
                        to_add['note'] = 'loss'
                    elif to_add['amount'] < 0. and dataset['type'] == 'market activity':
                        to_add['note'] = 'conditional exchange'
                    activity_link_overview[len(activity_link_overview)] = copy(to_add)
    activity_link_overview = pd.DataFrame(activity_link_overview).transpose()
    filename = 'activity_link_overview.xlsx'
    writer = pd.ExcelWriter(os.path.join(support_pkl_folder, filename))
    columns = ['activity name', 'location', 'reference product', 
               'exchange name', 'activity link activity name', 
               'activity link location', 'amount', 'consumed amount', 
               'note']
    activity_link_overview.to_excel(writer, 'activity_link_overview', 
        index = False, merge_cells = False, columns = columns)
    activity_link_overview = activity_link_overview[activity_link_overview['note'] != 'loss']
    activity_link_overview = pd.pivot_table(activity_link_overview, 
        index = ['activity link activity name', 'activity link location', 'exchange name'], 
        values = ['consumed amount'], aggfunc = np.sum)
    available_PV_overview = {}
    counter = 0
    activity_overview = activity_overview.reset_index().set_index([
        'activity name', 'location', 'exchange name'])
    for dataset in datasets:
        counter += 1
        print(counter, 'of', len(datasets))
        for exc in dataset['exchanges']:
            if exc['type'] == 'reference product' and exc['name'] == dataset['main reference product']:
                if 'production volume' not in exc:
                    exc['available production volume'] = 0.
                    exc['production volume'] = {'amount': 0.}
                else:
                    exc['available production volume'] = copy(exc['production volume']['amount'])
                break
        index = (dataset['name'], dataset['location'], dataset['main reference product'])
        sel = activity_overview.loc[index]
        if type(sel) == pd.core.frame.DataFrame:
            sel = sel.iloc[0]
        to_add = {'activity name': dataset['name'], 
                  'location': dataset['location'], 
                    'exchange name': exc['name'], 
                    'production volume': exc['production volume']['amount']}
        if index in set(activity_link_overview.index):
            sel = activity_link_overview.loc[index]
            to_add['consumed by activity links'] = sel['consumed amount']
            if sel['consumed amount'] < exc['available production volume']:
                available = exc['available production volume'] - sel['consumed amount']
            else:
                available = 0.
        else:
            to_add['consumed by activity links'] = 0.
            available = exc['available production volume']
        to_add['available production volume'] = copy(available)
        available_PV_overview[len(available_PV_overview)] = copy(to_add)
        exc['available production volume'] = copy(available)
        dataset['history']['calculate_available_PV'] = time.ctime()
    available_PV_overview = pd.DataFrame(available_PV_overview).transpose()
    
    columns = ['activity name', 'location', 'exchange name', 'production volume', 
               'consumed by activity links', 'available production volume']
    available_PV_overview.to_excel(writer, 'available_PV_overview', columns = columns, 
        index = False, merge_cells = False)
    ocelot.utils.save_file(available_PV_overview, support_pkl_folder, 'available_PV_overview')
    writer.save()
    writer.close()