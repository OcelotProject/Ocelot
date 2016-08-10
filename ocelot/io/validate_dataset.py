# -*- coding: utf-8 -*-
import re
from .. import utils
import pandas as pd
import os
import numpy as np

def dummy():
    return ''


def prepare_validation():
    
    #load and format useful variables
    folder = r'C:\Ocelot\ocelot\data'
    filename = 'compartments.xlsx'
    data_format = utils.read_format_definition()
    compartments = pd.read_excel(os.path.join(folder, filename), 'Sheet1')
    compartments = compartments.set_index(['compartment', 'subcompartment']).sortlevel(level=0)
    data_formats = separate_data_format(data_format)
    
    return data_formats, compartments


def validate_dataset(dataset, data_formats, compartments):
    
    local_report = []
    
    #validate the meta information of the dataset
    local_report = validate_meta(dataset, data_formats, local_report)
    
    #validate the exchanges with their uncertainty, PV and properties
    local_report = validate_exchanges(dataset, compartments, data_formats, local_report)
    
    #validate the parameters, if any
    local_report = validate_parameters(dataset, data_formats, local_report)
    
    return local_report


def adjust_mandatory_by_uncertainty_type(data_format):
    
    #extract the different types of uncertainty
    data_format_uncertainty = data_format[data_format['parent'] == 'uncertainty']
    uncertainty_types = data_format_uncertainty[data_format_uncertainty['in dataset'
        ] == 'type'].iloc[0]['allowed values']
    uncertainty_types = uncertainty_types.split(', ')
    
    #the data format spreadsheet tells which field is mandatory depending on the uncertainty type
    data_format_uncertainty_by_type = {}
    for uncertainty_type in uncertainty_types:
        df = data_format_uncertainty.copy()
        
        #create one dataset per uncertainty type and mark as mandatory certain fields
        for index in data_format_uncertainty.index:
            if uncertainty_type in str(data_format_uncertainty.loc[index, 'description']):
                df.loc[index, 'mandatory/optional'] = 'mandatory'
        data_format_uncertainty_by_type[uncertainty_type] = df.copy()
    
    return data_format_uncertainty_by_type


def separate_data_format(data_format):
    
    #put data format in different data frames according to the parent field
    data_formats = {}
    for parent in ['exchanges', 'dataset', 'production volume', 'properties', 'parameters']:
        data_formats[parent] = data_format[data_format['parent'] == parent]
    data_formats['uncertainty'] = adjust_mandatory_by_uncertainty_type(data_format)
    
    return data_formats


def validate_exchanges(dataset, compartments, data_formats, local_report):
    
    #validate different elements with different functions
    for exc in dataset['exchanges']:
        
        #fields directly in the exchange
        for i in range(len(data_formats['exchanges'])):
            sel = data_formats['exchanges'].iloc[i]
            local_report = validate(exc, sel, local_report, 'exchanges')
            
        #combination of compartment/subcompartment
        local_report = validate_elementary_exchange(exc, compartments, local_report)
        
        #uncertainty
        local_report = validate_uncertainty(exc, data_formats, local_report)
        
        #production volume
        local_report = validate_PV(exc, data_formats, local_report)
        
        #properties
        local_report = validate_properties(exc, data_formats, local_report)
    
    return local_report


def validate_elementary_exchange(exc, compartments, local_report):
    
    #check for invalid combination of compartment and subcompartment
    if 'elementary' in exc['tag']:
        index = []
        for field in ['compartment', 'subcompartment']:
            if field not in exc:
                1/0 #missing field
            else:
                index.append(exc[field])
        if len(index) == 2:
            if tuple(index) not in compartments.index:
                1/0 #wrong compartment/subcompartment combination
    
    return local_report


def validate_uncertainty(element, data_formats, local_report):
    
    #validate uncertainty
    if 'uncertainty' in element:
        u = element['uncertainty']
        for i in range(len(data_formats['uncertainty'][u['type']])):
            sel = data_formats['uncertainty'][u['type']].iloc[i]
            local_report = validate(u, sel, local_report, 'uncertainty')
    
    return local_report


def validate_PV(exc, data_formats, local_report):
    
    #only for reference products and byproducts
    if exc['type'] in ['reference product', 'byproduct']:
        if 'production volume' not in exc:
            1/0 #missing field
        else:
            PV = exc['production volume']
            
            #validate the different fields
            for i in range(len(data_formats['production volume'])):
                sel = data_formats['production volume'].iloc[i]
                local_report = validate(PV, sel, local_report, 'production volume')
            
            #validate the uncertainty
            local_report = validate_uncertainty(PV, data_formats, local_report)
    
    return local_report


def validate_parameters(dataset, data_formats, local_report):
    
    #if there are parameters
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            
            #validate the different fields
            for i in range(len(data_formats['parameters'])):
                sel = data_formats['parameters'].iloc[i]
                local_report = validate(p, sel, local_report, 'parameters')
            
            #validate the uncertainty
            local_report = validate_uncertainty(p, data_formats, local_report)
    
    return local_report


def validate_properties(exc, data_formats, local_report):
    
    #if there are properties in the exchanges
    if 'properties' in exc:
        for p in exc['properties']:
            
            #validate the different fields
            for i in range(len(data_formats['properties'])):
                sel = data_formats['properties'].iloc[i]
                local_report = validate(p, sel, local_report, 'properties')
            
            #validate the uncertainty
            local_report = validate_uncertainty(p, data_formats, local_report)
    
    return local_report


def find_selected_type(s):
    
    #transforms a string into a type
    if s == 'str':
        expected_type = [str]
    elif s == 'dict':
        expected_type = [dict]
    elif s == 'list':
        expected_type = [list]
    elif s == 'float':
        expected_type = [float, np.float64]
    elif s == 'int':
        expected_type = int
    else:
        1/0
    return expected_type


def validate(element, sel, local_report, element_type):
    
    field = sel['in dataset']
    if field not in element:
        #this is only a mistake if the field is mandatory
        if sel['mandatory/optional'] == 'mandatory':
            1/0 #missing field

    elif type(element[field]) not in find_selected_type(sel['type']):
        #wrong type of content
        1/0 #wrong type
        
    elif not utils.is_empty(sel['allowed values']):
        #the field might have restricted range of values
        allowed = sel['allowed values'].split(', ')
        if str(element[field]) not in allowed:
            1/0 #illegal value
    
    return local_report


def validate_meta(dataset, data_formats, local_report):
    
    #validate the different fields
    for i in range(len(data_formats['dataset'])):
        sel = data_formats['dataset'].iloc[i]
        local_report = validate(dataset, sel, local_report, 'dataset')
        field = sel['in dataset']
        
        #check the date format
        if 'date' in field:
            date_pattern = '\d{4}-\d{2}-\d{2}'
            g = re.search(date_pattern, dataset[field])
            if g == None:
                1/0 #date in wrong format

    return local_report