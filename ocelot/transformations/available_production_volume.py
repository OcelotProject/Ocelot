# -*- coding: utf-8 -*-
import pandas as pd
from cPickle import dump, load
from copy import copy
import os
import numpy as np

def available_production_volume(datasets, logger, support_excel_folder, support_pkl_folder):
    """Calculates available production volume for market shares by removing 
        consumption by activity links"""
        
    #first, an activity link overview is required
    activity_overview = load(os.path.join(support_pkl_folder, 'activity_overview.pkl'))
    activity_overview = activity_overview.set_index(['activity id', 'product']).sortlevel(level=0)
    df = pd.DataFrame()
    for dataset in datasets:
        data = {}
        for exc in dataset['exchanges']:
            if exc['type'] in ['from technosphere', 'byproduct'] and 'activity link' in exc:
                sel = activity_overview.loc[(exc['activity link'], exc['name'])]
                to_add = {
                    'exchange name': exc['name'], 
                    'amount': exc['amount'], 
                    'supplying activity name': sel['activity name'], 
                    'supplying location': sel['location'], 
                    }
                if exc['activity link'] == dataset['id']:
                    to_add['note'] = 'loss'
                elif to_add['amount'] < 0. and dataset['type'] == 'market activity':
                    to_add['note'] = 'conditional exchange'
                data[len(data)] = copy(to_add)
        if len(data) > 0:
            data = pd.DataFrame(data).transpose()
            data['activity name'] = dataset['name']
            data['location'] = dataset['location']
            ref_exc = get_reference_product(dataset) #from utils
            data['consumed amount'] = data['amount'].abs() / ref_exc['amount'
                ] * ref_exc['production volume']['amount']
            df = pd.concat(df, data)
    pivot = pd.pivot_table(df, values = 'consumed amount', 
                rows = ['supplying activity name', 'supplying location', 'exchange name'], 
                aggfunc = np.sum)
    for dataset in datasets:
        for exc in iterate_outouts_to_technosphere(dataset):
            #careful, is it really stored?
            index = (dataset['name'], dataset['location'], exc['name'])
            if index in pivot.index:
                exc['production volume']['consumed by activity links'] = pivot.loc[index, 'consumed amount']
            else:
                exc['production volume']['consumed by activity links'] = 0.
            exc['production volume']['available production volume'] = max(0., 
               exc['production volume']['amount'] - 
               exc['production volume']['consumed by activity links'])
    
    cols = ['filepath', 'activity id', 'activity name', 'location', 'activity type', 
            'technology level', 'access restricted', 'allocation method', 
            'exchange type', 'exchange name', 'amount', 'unit', 'byproduct classification']
    df.to_excel(writer, cols = cols, index = False, merge_cells = False)
    filename = 'activity_overview.pkl'
    dump(df, os.path.join(support_pkl_folder, filename))
    
    return df