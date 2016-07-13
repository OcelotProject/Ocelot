# -*- coding: utf-8 -*-
import ocelot
from copy import copy
import numpy as np
import scipy as sp
import pandas as pd
import os
import time

if 0:
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
    if 1:
        ocelot.transformations.activity_overview.build_activity_overview(datasets, 
            support_excel_folder, support_pkl_folder, data_format)
    ocelot.utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    filename = 'ecoinvent_3.2_internal'
    #filename = 'after_combined_production_without_byproducts'
    #filename = 'ecoinvent_3.2_internal_after_allocation'
    #filename = 'after_allocation_treatment_and_recycling'
    #filename = 'after_combined_production_with_byproducts'
    #filename = 'after_economic_allocation'
    #filename = 'after_true_value_allocation'
    datasets = ocelot.utils.open_file(folder, filename)
    data_format = ocelot.utils.read_format_definition()
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    criteria = {
        #'allocation method': [
            #'recycling activity', 
              #'waste treatment', 
              #'economic allocation', 
                #'true value allocation'
                #'combined production without byproducts'
                #'combined production with byproducts'
              #], 
    'id': '40acc8ff-a89a-421f-8af3-c5b615c38bff'
        #'activity name': ['treatment of residue from mechanical treatment, laser printer, municipal incineration with fly ash extraction'], 
        #'location': ['CH'], 
                }
    activity_overview = ocelot.utils.open_file(folder, 'activity_overview')
    #datasets = ocelot.utils.filter_datasets(datasets, activity_overview, criteria)
    if 0:
        datasets = ocelot.transformations.calculate_available_PV.available_production_volume(
            datasets, '', support_excel_folder, support_pkl_folder)
        1/0
        datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
            datasets, data_format, '')
        folder = 'C:\ocelot_DB'
        filename = 'ecoinvent_3.2_internal_after_allocation'
        ocelot.utils.save_file(datasets, folder, filename)
    if 0:
        system_model_folder = r'C:\python\DB_versions\3.2\cut-off'
        ocelot.utils.validate_against_linking(datasets, system_model_folder, data_format, 
            folder, types_to_validate = ['from environment', 'to environment'])
    #datasets = ocelot.transformations.calculate_available_PV.calculate_available_PV(
    #    datasets, '', support_excel_folder, support_pkl_folder)
    available_PV_overview = ocelot.utils.open_file(support_pkl_folder, 'available_PV_overview')
    grouped = available_PV_overview.groupby('activity name')
    datasets = ocelot.utils.datasets_to_dict(datasets, ['name', 'location'])
    warning_limits = [.995, 1.05]
    RoW_creation_report = {}
    def is_RoW_created(sel, RoW_creation_report):
        exchange_type = sel.iloc[0]['exchange type']
        exchange_name = sel.iloc[0]['exchange name']
        to_add = {'activity name': activity_name, 
              'GLO present': True, 
              'nb of other locations': len(locations),
                'exchange type': exchange_type, 
                'exchange name': exchange_name, 
                'delete GLO': True}
        other_locations = str(locations)
        other_locations = other_locations.replace('{', ''
            ).replace('}', ''
            ).replace("'", '')
        to_add['other locations'] = other_locations
        GLO_line = sel[sel['location'] == 'GLO']
        GLO_PV = GLO_line['production volume'].sum()
        to_add['PV consumed by activity links'] = GLO_line[
                    'consumed by activity links'].sum()
        to_add['GLO PV'] = GLO_PV
        if GLO_PV == 0.:
            to_add['RoW PV before activity links'] = 0.
            to_add['RoW PV before activity links'] = 0.
            to_add['create RoW'] = 'not sure!' #fix me
            to_add['delete GLO'] = 'not sure!' # fix me
        else:
            local_PV = sel[sel['location'] != 'GLO']['production volume'].sum()
            to_add['local PV'] = local_PV
            ratio = local_PV/GLO_PV
            to_add['local/GLO PV'] = ratio
            if ratio > warning_limits[0]:
                to_add['create RoW'] = False
                to_add['RoW PV before activity links'] = 0.
                to_add['PV consumed by activity links'] = GLO_line[
                    'consumed by activity links'].sum()
                to_add['RoW PV after activity links'] = 0.
                if ratio < warning_limits[1]:
                    to_add['lower_limit < ratio < upper_limit'] = True
                else:
                    to_add['lower_limit < ratio < upper_limit'] = False
            else:
                to_add['lower_limit < ratio < upper_limit'] = False
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
    counter = 0
    for activity_name, group in grouped:
        print(counter, 'of', len(grouped))
        counter += 1
        locations = set(group['location'])
        if 'GLO' not in locations:
            for i in range(len(group)):
                to_add = {'activity name': activity_name, 
                          'GLO present': False, 
                          'exchange type': group.iloc[i]['exchange type'], 
                        'exchange name': group.iloc[i]['exchange name']}
                RoW_creation_report[len(RoW_creation_report)] = copy(to_add)
        else:
            locations.remove('GLO')
            if len(locations) == 0:
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
                exchange_type = 'reference product'
                sel = group[group['exchange type'] == exchange_type]
                for exchange_name in set(sel['exchange name']):
                    sel1 = sel[sel['exchange name'] == exchange_name]
                    RoW_creation_report = is_RoW_created(sel1, RoW_creation_report)
                if 'byproduct' in list(group['exchange type']):
                    last = RoW_creation_report[len(RoW_creation_report)-1]
                    exchange_type = 'byproduct'
                    sel = group[group['exchange type'] == exchange_type]
                    sel = sel[sel['byproduct classification'] == 'allocatable']
                    if len(sel) > 0:
                        for exchange_name in set(sel['exchange name']):
                            sel1 = sel[sel['exchange name'] == exchange_name]
                            byproduct_classification = sel1.iloc[0]['byproduct classification']
                            if last['create RoW']:
                                RoW_creation_report = is_RoW_created(sel1, RoW_creation_report)
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
    columns = ['activity name', 'GLO present', 
        'exchange type', 'exchange name', 
        'nb of other locations', 'other locations', 'GLO PV', 'local PV', 
        'local/GLO PV', 'lower_limit < ratio < upper_limit', 
        'delete GLO', 'create RoW', 'RoW PV before activity links', 
        'RoW PV after activity links', 'PV consumed by activity links', 
        'RoW created for reference product'
        ]
    folder = r'C:\ocelot_DB'
    filename = 'RoW_creation_report.xlsx'
    RoW_creation_report.to_excel(os.path.join(folder, filename), 
        columns = columns, index = False, merge_cells = False)