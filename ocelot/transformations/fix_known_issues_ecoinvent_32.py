# -*- coding: utf-8 -*-
import time

def dummy():
    return ''
def fix_known_issues(datasets, logger):
    for dataset in datasets:
        dataset['history']['fix_known_issues_ecoinvent_32'] = time.ctime()
        if dataset['name'] == 'clinker production':
            for exc in dataset['exchanges']:
                if 'production volume' in exc:
                    if 'mathematical relation' in exc['production volume']:
                        if 'clinker_PV' in exc['production volume']['mathematical relation']:
                            exc['production volume']['mathematical relation'
                                ] = exc['production volume']['mathematical relation'
                                ].replace('clinker_PV', 'clinker_pv')
                    if 'variable' in exc['production volume']:
                        if exc['production volume']['variable'] == 'clinker_PV':
                            exc['production volume']['variable'] = 'clinker_pv'
        elif dataset['name'] == 'cement production, alternative constituents 6-20%':
            for exc in dataset['exchanges']:
                if 'mathematical relation' in exc: 
                    if 'ggbfs' in exc['mathematical relation']:
                        exc['mathematical relation'
                            ] = exc['mathematical relation'].replace('ggbfs', 'GGBFS')
                if 'variable' in exc and exc['variable'] == 'ggbfs':
                    exc['variable'] = 'GGBFS'
        elif dataset['name'] == 'ethylene glycol production':
            #yield is a reserved word that cannot be used as a variable in Python
            for p in dataset['parameters']:
                if 'variable' in p and p['variable'] == 'yield':
                    p['variable'] = 'YIELD'
            for exc in dataset['exchanges']:
                if 'mathematical relation' in exc:
                    if 'yield' in exc['mathematical relation']:
                        exc['mathematical relation'] = exc['mathematical relation'
                            ].replace('yield', 'YIELD')
        elif dataset['name'] == 'petroleum and gas production, off-shore':
            for exc in dataset['exchanges']:
                if 'mathematical relation' in exc:
                    if 'petroleum_APV' in exc['mathematical relation']:
                        exc['mathematical relation'] = exc['mathematical relation'
                            ].replace('petroleum_APV', 'petroleum_apv')
                        #never executed...  maybe it was a mistake.  Keep until proven otherwise
                        1/0
                    if '\r\n' in exc['mathematical relation']:
                        exc['mathematical relation'
                            ] = exc['mathematical relation'].replace('\r\n', '')
        elif dataset['name'] == 'benzene chlorination':
            for exc in dataset['exchanges']:
                if 'production volume' in exc:
                    if 'mathematical relation' in exc['production volume']:
                        if 'avoirdupois' in exc['production volume']['mathematical relation']:
                            exc['production volume']['mathematical relation'
                                ] = exc['production volume']['mathematical relation'
                                ].replace("UnitConversion(152000000, 'pound avoirdupois', 'kg')", 
                                '68949040.24')
        for exc in dataset['exchanges']:
            if 'mathematical relation' in exc:
                exc['mathematical relation'] = fixMathematicalRelation(
                    exc['mathematical relation'])
            if 'production volume' in exc:
                if 'mathematical relation' in exc['production volume']:
                    exc['production volume']['mathematical relation'
                        ] = fixMathematicalRelation(
                        exc['production volume']['mathematical relation'])
            if 'properties' in exc:
                for p in exc['properties']:
                    if 'mathematical relation' in p:
                        p['mathematical relation'] = fixMathematicalRelation(
                            p['mathematical relation'])
        if 'parameters' in dataset:
            for p in dataset['parameters']:
                if 'mathematical relation' in p:
                    p['mathematical relation'] = fixMathematicalRelation(
                        p['mathematical relation'])
    
    return datasets


def fixMathematicalRelation(m):
    for before, after in [('ABS(', 'abs('), ('%', 'e-2'), ('^', '**')]:
        m = m.replace(before, after)
    #also, need to replace division by int by division by float
    return m