# -*- coding: utf-8 -*-
import pandas as pd
from copy import copy
import os
from .. import utils

def dummy():
    return ''

def calculate_RoW_PV(support_pkl_folder, support_excel_folder, warning_limits = [.995, 1.05]):
    #required to know how much is taken by activity links to calculate the PV of RoW
    available_PV_overview = utils.open_file(support_pkl_folder, 'available_PV_overview')
    
    #group datasets by activity name
    grouped = available_PV_overview.groupby('activity name')
    RoW_creation_report = {}
    for activity_name, group in grouped:
        
        #check how many locations have this activity name
        locations = set(group['location'])
        if 'GLO' not in locations:
            #this happens for import activities
            for i in range(len(group)):
                to_add = {'activity name': activity_name, 
                          'GLO present': False, 
                          'create RoW': False, 
                          'exchange type': group.iloc[i]['exchange type'], 
                        'exchange name': group.iloc[i]['exchange name']}
                RoW_creation_report[len(RoW_creation_report)] = copy(to_add)
        
        else:
            #There is a GLO, remove it from the location list
            locations.remove('GLO')
            
            if len(locations) == 0:
                #There was only GLO, so no RoW creation
                for i in range(len(group)):
                    to_add = {'activity name': activity_name, 
                          'GLO present': True, 
                          'nb of other locations': 0, 
                          'delete GLO': False, 
                          'exchange type': group.iloc[i]['exchange type'], 
                        'exchange name': group.iloc[i]['exchange name'], 
                          'create RoW': False}
                    RoW_creation_report[len(RoW_creation_report)] = copy(to_add)
            else:
                #There is GLO and other locations.  RoW might be created. 
                #Start with the reference products
                exchange_type = 'reference product'
                sel = group[group['exchange type'] == exchange_type]
                for exchange_name in set(sel['exchange name']):
                    sel1 = sel[sel['exchange name'] == exchange_name]
                    RoW_creation_report = is_RoW_created(sel1, RoW_creation_report, locations, 
                        activity_name, warning_limits)
                        
                #Maybe for byproducts
                if 'byproduct' in list(group['exchange type']):
                    last = RoW_creation_report[len(RoW_creation_report)-1]
                    exchange_type = 'byproduct'
                    sel = group[group['exchange type'] == exchange_type]
                    sel = sel[sel['byproduct classification'] == 'allocatable']
                    
                    #Only for allocatable byproducts
                    if len(sel) > 0:
                        for exchange_name in set(sel['exchange name']):
                            sel1 = sel[sel['exchange name'] == exchange_name]
                            if last['create RoW']:
                                #Only if the RoW is created for the reference product
                                RoW_creation_report = is_RoW_created(sel1, RoW_creation_report, 
                                    locations, activity_name, warning_limits)
                            else:
                                to_add = {'activity name': activity_name, 
                                  'GLO present': True, 
                                  'nb of other locations': len(locations),
                                    'exchange type': exchange_type, 
                                    'exchange name': exchange_name, 
                                    'delete GLO': True, 
                                    'create RoW': False, 
                                    'RoW created for reference product': False}
                                RoW_creation_report[len(RoW_creation_report)] = copy(to_add)
    RoW_creation_report = pd.DataFrame(RoW_creation_report).transpose()
    save_RoW_creation_report(RoW_creation_report, support_excel_folder, support_pkl_folder)


def is_RoW_created(sel, RoW_creation_report, locations, activity_name, warning_limits):
    #Gathering info about the exchange to technosphere
    exchange_type = sel.iloc[0]['exchange type']
    exchange_name = sel.iloc[0]['exchange name']
    to_add = {'activity name': activity_name, 
          'GLO present': True, 
          'nb of other locations': len(locations),
            'exchange type': exchange_type, 
            'exchange name': exchange_name, 
            'delete GLO': True}
    other_locations = str(locations)
    to_add['other locations'] = other_locations.replace('{', ''
        ).replace('}', '').replace("'", '')
    GLO_line = sel[sel['location'] == 'GLO']
    to_add['GLO exchange amount'] = GLO_line['exchange amount'].sum()
    
    if to_add['GLO exchange amount'] == 0.:
        #Datasets in general are not created if the reference product amount is equal to zero
        to_add['create RoW'] = False
    
    else:
        #still has to check if there is total or near-total coverage by local datasets
        to_add['PV consumed by activity links'] = GLO_line[
                'consumed by activity links'].sum()
        GLO_PV = GLO_line['production volume'].sum()
        to_add['GLO PV'] = GLO_PV
        local_PV = sel[sel['location'] != 'GLO']['production volume'].sum()
        to_add['local PV'] = local_PV
        if GLO_PV == 0.:
            #will be created anyway, but no contribution to market shares
            ratio = 0.
        else:
            ratio = local_PV/GLO_PV
        to_add['local/GLO PV'] = ratio
        if ratio > warning_limits[0]:
            to_add['create RoW'] = False
            to_add['RoW PV before activity links'] = 0.
            to_add['PV consumed by activity links'] = GLO_line[
                'consumed by activity links'].sum()
            to_add['RoW PV after activity links'] = 0.
            if ratio < warning_limits[1]:
                to_add['near-full coverage warning'] = True
            else:
                to_add['near-full coverage warning'] = False
        else:
            to_add['near-full coverage warning'] = False
            to_add['create RoW'] = True
            to_add['RoW PV before activity links'] = GLO_PV - local_PV
            to_add['RoW PV after activity links'] = to_add['RoW PV before activity links'
                ] - to_add['PV consumed by activity links']
            if to_add['RoW PV after activity links'] < 0.:
                to_add['RoW PV after activity links'] = 0.
    if exchange_type == 'byproduct':
        to_add['RoW created for reference product'] = True
    RoW_creation_report[len(RoW_creation_report)] = copy(to_add)
    return RoW_creation_report

def save_RoW_creation_report(RoW_creation_report, support_excel_folder, support_pkl_folder):
    columns = ['activity name', 'GLO present', 'exchange type', 'exchange name', 
        'nb of other locations', 'other locations', 'GLO PV', 'GLO exchange amount', 'local PV', 
        'local/GLO PV', 'near-full coverage warning', 'delete GLO', 'create RoW', 
        'RoW PV before activity links', 'RoW PV after activity links', 
        'RoW created for reference product', 'PV consumed by activity links'
        ]
    filename = 'RoW_creation_report.xlsx'
    RoW_creation_report.to_excel(os.path.join(support_excel_folder, filename), 
        columns = columns, index = False, merge_cells = False)
    utils.save_file(RoW_creation_report, support_pkl_folder, 'RoW_creation_report')