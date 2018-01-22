# -*- coding: utf-8 -*-
import utils, pandas, re
import os, numpy, pyprind
from lxml import objectify
from copy import copy
from jinja2 import Environment, FileSystemLoader

#template and environment when writing to xml and spold2 with jinja2
template_path = r'C:\python\Ocelot\templates'
env = Environment(loader=FileSystemLoader(template_path), 
                  keep_trailing_newline = True, 
                  lstrip_blocks = True, 
                  trim_blocks = True)
groupCodes = {
    'ReferenceProduct': 0, 
    'ByProduct': 2, 
    'FromEnvironment': 4, 
    'FromTechnosphere': 5, 
    'ToEnvironment': 4}
tag_re = re.compile('\{http://www\S*\}')
#loading the excel schema for spold2.  Arranging it for ease of use in spold2 constructor

folder = r'C:\python\Ocelot'
filename = 'spold2_fields.xlsx'
schema = pandas.read_excel(os.path.join(folder, filename), 'schema')
schema = utils.replace_empty_in_df(schema)
schema_ = schema[~schema['spold2 element name'].apply(utils.is_empty)]
pedigreeCriteria = ['reliability', 'completeness', 
    'temporalCorrelation', 'geographicalCorrelation', 
    'furtherTechnologyCorrelation']
schema, dummy = utils.accelerate_df(schema_, 
    ['spold2 element name', 'spold2 field name'], force_to_dictionary = True)
end_object = {'str': str, 
              'int': int, 
              'float': float, 
              'bool': utils._bool}
class TestObject:
    def __init__(self, o, schema_sel = [], folder = '', filename = ''):
        if folder != '':
            with open(os.path.join(folder, filename), encoding='utf8') as f:
                root = objectify.parse(f).getroot()
                if hasattr(root, 'activityDataset'):
                    o = root.activityDataset
                    self.activityDataset = 'activityDataset'
                else:
                    o = root.childActivityDataset
                    self.activityDataset = 'childActivityDataset'
            self.folder = folder
            self.filename = filename
        element_tag = o.tag.replace(tag_re.match(o.tag).group(), '')
        
        for attr, value in o.attrib.items():
            key = (element_tag, attr)
            if key in schema:
                sel = schema[key]
                if not sel['ignore']:
                    setattr(self, sel['Python name'], end_object[sel['Python type']](value))
                        
        for c in o.iterchildren():
            field_tag = c.tag.replace(tag_re.match(c.tag).group(), '')
            key = (element_tag, field_tag)
            sel = schema[key]
            if not sel['ignore']:
                field = sel['Python name']
                if sel['multiple']:
                    if not hasattr(self, field):
                        setattr(self, field, [])
                    if field in ['tags', 'comment', 'synonyms']:
                        c = end_object[sel['Python type']](c)
                        if not utils.is_empty(c):
                            if 'EcoSpold01Location' not in c:    
                                getattr(self, field).append(c)
                    elif schema_sel['Python type'] == 'TTextAndImage':
                        if utils.is_empty(c.text):
                            getattr(self, field).append((c.get('index'), ''))
                        else:
                            getattr(self, field).append((c.get('index'), str(c.text)))
                    else:
                        getattr(self, field).append(TestObject(c, sel))
                elif sel['Python type'] in end_object:
                    setattr(self, field, end_object[sel['Python type']](c))
                elif utils.is_empty(sel['Python type']):
                    t = TestObject(c, sel)
                    for field in utils.list_attributes(t):
                        setattr(self, field, getattr(t, field))
                else:
                    setattr(self, field, TestObject(c, sel))
        if utils.is_empty(schema_sel):
            self.spold2_type = 'Dataset'
            self.flowData = []
            for field in ['intermediateExchange', 'elementaryExchange', 'parameters']:
                if hasattr(self, field):
                    self.flowData.extend(getattr(self, field))
                    delattr(self, field)
        elif not utils.is_empty(schema_sel['Python type']):
            self.spold2_type = schema_sel['Python type']
        else:
            self.spold2_type = ''#will not be stored anyway
        if self.spold2_type == 'Exchange':
            if hasattr(self, 'inputGroup'):
                if self.inputGroup in [5, '5']:
                    self.group = 'FromTechnosphere'
                elif self.inputGroup in [4, '4']:
                    self.group = 'FromEnvironment'
                else:
                    raise ValueError
            elif hasattr(self, 'outputGroup'):
                if self.outputGroup in [2, '2']:
                    self.group = 'ByProduct'
                elif self.outputGroup in [0, '0']:
                    self.group = 'ReferenceProduct'
                elif self.outputGroup in [4, '4']:
                    self.group = 'ToEnvironment'
                else:
                    raise ValueError
            if 'From' in self.group:
                self.groupType = 'inputGroup'
            else:
                self.groupType = 'outputGroup'
            self.groupCode = groupCodes[self.group]
            if 'Environment' in self.group:
                self.validation_extra_info = 'elementaryExchange'
                self.exchangeType = 'elementaryExchange'
            else:
                self.validation_extra_info = 'intermediateExchange'
                self.exchangeType = 'intermediateExchange'
            #remove dummy properties, or not store them in the first place
            #remove legacy comments
        elif self.spold2_type == 'TUncertainty':
            for c in o.iterchildren():
                if 'pedigreeMatrix' not in c.tag and 'comment' not in c.tag:
                    self.type = c.tag.replace(tag_re.match(c.tag).group(), '')
            self.pedigreeMatrix = []
            for criteria in pedigreeCriteria:
                if hasattr(self, criteria):
                    self.pedigreeMatrix.append(int(getattr(self, criteria)))
                else:
                    self.pedigreeMatrix.append(5)
            if self.type == 'lognormal':
                assert hasattr(self, 'varianceWithPedigreeUncertainty')
            if 'productionVolumeUncertainty' in element_tag:
                self.field = 'productionVolumeUncertainty'
            else:
                self.field = 'uncertainty'
    
    def write_to_spold(self, folder = ''):
        data = utils.object_to_dict(self)
        for field, v in data.items():
            if field == 'comment' and self.spold2_type in [
                    'Exchange', 'TProperty', 'TParameter', 'TUncertainty']:
                v = '\n'.join(v)
            if isinstance(v, str):
                data[field] = utils.replace_HTML_entities(v)
            elif type(v) in [int, set, float]:
                pass
            elif isinstance(v, bool):
                data[field] = str(v).lower()
            elif isinstance(v, list):
                for i in range(len(v)):
                    if self.spold2_type == 'TTextAndImage':
                        data[field][i] = (v[i][0], utils.replace_HTML_entities(v[i][1]))
                    elif hasattr(data[field][i], 'write_to_spold'):
                        data[field][i] = v[i].write_to_spold()
                    elif isinstance(v[i], str):
                        data[field][i] = utils.replace_HTML_entities(v[i])
                    elif type(v[i]) in [int, set, float]:
                        pass
                    else:
                        NotImplementedError
            elif hasattr(v, 'write_to_spold'):
                data[field] = v.write_to_spold()
            else:
                raise NotImplementedError
        template_name = '{}_2.xml'.format(self.spold2_type)
        template = env.get_template(template_name)
        output = template.render(**data)
        if self.spold2_type == 'Dataset':
            output_filename = os.path.join(folder, self.filename)
            writer = open(output_filename, 'w', encoding = 'utf-8')
            writer.write(output)
            writer.close()
        else:
            return output
def to_apply(x):
    if '\n' in x:
        x = '\n'.join(set(x.split('\n')))
def collect(o, df, path):
    attributes = set(utils.list_attributes(o))
    attributes.difference_update(set(['spold2_type']))
    for attr in attributes:
        v = getattr(o, attr)
        if type(v) in [str, int, float, bool]:
            p = copy(path)
            p.append(attr)
            to_add = {'path': '\n'.join(p), 'value': str(v).strip()}
            df.append(to_add)
        elif isinstance(v, list):
            if attr in ['flowData']:
                field = 'id'
            elif attr in ['classifications']:
                field = 'classificationId'
            elif attr in ['tags', 'comment', 'pedigreeMatrix', 'text', 'synonyms', 'imageUrl', 'variables']:
                field = ''
            elif attr in ['properties']:
                field = 'propertyId'
            elif attr in ['reviews']:
                field = 'reviews'
            else:
                1/0
            for e in v:
                p = copy(path)
                if field == 'reviews':
                    if hasattr(e, 'reviewDate'):
                        p.extend([field, e.reviewerId, e.reviewDate])
                    else:
                        p.extend([field, e.reviewerId, ''])
                elif field == '':
                    p.extend([field, str(e).strip()])
                elif type(e) in [str, int, tuple]:
                    p.extend([field, str(e).strip()])
                else:
                    if hasattr(e, field):
                        p.extend([field, getattr(e, field)])
                    else:
                        p.extend([field, getattr(e, 'parameterId')])
                df = collect(e, df, p)
        elif hasattr(v, 'spold2_type'):
            p = copy(path)
            p.append(attr)
            df = collect(v, df, p)
        else:
            1/0
    
    if hasattr(o, 'spold2_type') and o.spold2_type == 'Dataset':
        df = utils.list_to_df(df)
        df = df[~df['path'].isin(['filename', 'folder'])]
        df['value'] = df['value'].apply(to_apply)
        df.set_index('path', inplace = True)
    return df

def test_writer():
    folder = r'C:\Dropbox (ecoinvent)\ei-int\technical\releases\3.4\Undefined\datasets'
    result_folder = r'C:\Dropbox (ecoinvent)\ei-int\technical\releases\3.4\Undefined\test'
    filelist = utils.build_file_list(folder)
    error_report = []
    for filename in pyprind.prog_bar(filelist):
        f = TestObject('', '', folder = folder, filename = filename)
        f_df = collect(f, [], [])
        f.write_to_spold(result_folder)
        g = TestObject('', '', folder = result_folder, filename = filename)
        g_df = collect(g, [], [])
        df = f_df.join(g_df, how = 'outer', lsuffix = '_original', rsuffix = '_exported').reset_index()
        df = utils.replace_empty_in_df(df)
        df['different'] = df['value_original'] != df['value_exported']
        df = df[df['different']]
        if len(df):
            df['filename'] = filename
            df['activityName'] = f.activityName
            df['geography'] = f.geography
            error_report.append(df)
    if len(error_report):
        columns = ['filename', 'activityName', 'geography', 'path', 'value_original', 'value_exported']
        df = pandas.concat(error_report)
        dfs = [(df, 'Sheet1', columns)]
        utils.dataframe_to_excel(result_folder, 'error_report.xlsx', dfs)
    else:
        print('No errors!')

if __name__ == '__main__':
    folder = r'C:\Dropbox (ecoinvent)\ei-int\technical\releases\3.4\Undefined\datasets'
    result_folder = r'C:\Dropbox (ecoinvent)\ei-int\technical\releases\3.4\Undefined\test'
    filelist = utils.build_file_list(folder)
    for filename in pyprind.prog_bar(filelist):
        f = TestObject('', '', folder = folder, filename = filename)
        
        break