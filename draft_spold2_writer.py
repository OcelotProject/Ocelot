# -*- coding: utf-8 -*-
import utils, spold2_utils
import os, numpy, inspect
from lxml import objectify
from copy import copy
from jinja2 import Environment, FileSystemLoader

#template and environment when writing to xml and spold2 with jinja2
template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates', 'spold')
env = Environment(loader=FileSystemLoader(template_path), 
                  keep_trailing_newline = True, 
                  lstrip_blocks = True, 
                  trim_blocks = True)

end_object = {'str': str, 
              'int': int, 
              'float': float, 
              'bool': utils._bool}
spold2_types = {}
class TestObject:
    def __init__(self, o, schema_sel = [], folder = '', filename = ''):
        if folder != '':
            with open(os.path.join(folder, filename), encoding='utf8') as f:
                root = objectify.parse(f).getroot()
                if hasattr(root, 'activityDataset'):
                    o = root.activityDataset
                else:
                    o = root.childActivityDataset
        element_tag = o.tag.replace(spold2_utils.tag_re.match(o.tag).group(), '')
        for attr, value in o.attrib.items():
            key = (element_tag, attr)
            if key in spold2_utils.schema:
                sel = spold2_utils.schema[key]
                if not sel['ignore']:
                    field = sel['Python name']
                    assert not utils.is_empty(field)
                    setattr(self, field, end_object[sel['Python type']](value))
                    
        for c in o.iterchildren():
            field_tag = c.tag.replace(spold2_utils.tag_re.match(c.tag).group(), '')
            key = (element_tag, field_tag)
            sel = spold2_utils.schema[key]
            if not sel['ignore']:
                field = sel['Python name']
                if sel['multiple']:
                    assert not utils.is_empty(field)
                    if not hasattr(self, field):
                        setattr(self, field, [])
                    if field in ['tags', 'comment', 'synonyms']:
                        c = end_object[sel['Python type']](c)
                        if not utils.is_empty(c):
                            getattr(self, field).append(end_object[sel['Python type']](c))
                    else:
                        getattr(self, field).append(TestObject(c, sel))
                elif 'Comment' in field or field == 'details':
                    setattr(self, field, [])
                    variables = []
                    for cc in c.iterchildren():
                        t = cc.tag.replace(spold2_utils.tag_re.match(o.tag).group(), '')
                        if t in ['text', 'imageUrl']:
                            if utils.is_empty(cc.text):
                                getattr(self, field).append((t, cc.get('index'), ''))
                            else:
                                getattr(self, field).append((t, cc.get('index'), str(cc.text)))
                        else:
                            1/0#handle me
                elif utils.is_empty(sel['Python type']):
                    t = TestObject(c, sel)
                    for field in utils.list_attributes(t):
                        setattr(self, field, getattr(t, field))
                elif sel['Python type'] in end_object:
                    assert not utils.is_empty(field)
                    setattr(self, field, end_object[sel['Python type']](c))
                else:
                    if field == 'activityName':
                        1/0
                    assert not utils.is_empty(field)
                    setattr(self, field, TestObject(c, sel))
        if utils.is_empty(schema_sel):
            self.spold2_type = 'Dataset'
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
            self.groupCode = spold2_utils.meta_translator[self.groupType][self.group]
            if 'Environment' in self.group:
                self.validation_extra_info = 'elementaryExchange'
                self.exchangeType = 'elementaryExchange'
            else:
                self.validation_extra_info = 'intermediateExchange'
                self.exchangeType = 'intermediateExchange'
            #remove dummy properties, or not store them in the first place
            #remove legacy comments
            if hasattr(self, 'productionVolumeUncertainty'):
                self.productionVolumeUncertainty.field = 'productionVolumeUncertainty'
        elif self.spold2_type == 'TUncertainty':
            1/0
        elif self.spold2_type == 'TParameter':
            if not hasattr(self, 'unitName') or utils.is_empty(self.unitName):
                #these are listed as optional in the schema, but it causes problem later
                #so they are forced to "dimensionless" when absent
                self.unitName = 'dimensionless'
                self.unitId = '577e242a-461f-44a7-922c-d8e1c3d2bf45'
        if hasattr(self, 'uncertainty'):
            self.uncertainty.field = 'uncertainty'
class BaseClass:
    def __init__(self, o, is_child = False):
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
    
    def get(self, field, default_value = False):
        if hasattr(self, field):
            return getattr(self, field)
        elif default_value is False:
            raise ValueError('Field "{}" missing in this instance of object "{}"'.format(field, self.object_class))
        else:
            return default_value
    
    def prepare_for_spold(self, MD, mapping):
        data = utils.object_to_dict(self)
        for field in data:
            if self.object_class in ['Exchange', 'TProperty', 'TParameter', 'TUncertainty'
                    ] and field == 'comment':
                data[field] = '\n'.join(data[field])
            if type(data[field]) in constructors['bool']:
                data[field] = str(data[field]).lower()
            elif type(data[field]) in [str, objectify.StringElement]:
                data[field] = utils.replace_HTML_entities(data[field])
            elif type(data[field]) in [objectify.ObjectifiedElement, int, set, float, 
                     numpy.float64, numpy.int64, numpy.long, dict, numpy.int32, type(None)]:
                pass
            elif hasattr(data[field], 'prepare_for_spold'):
                data[field] = data[field].prepare_for_spold(MD, mapping)
            elif type(data[field]) == list:
                for i in range(len(data[field])):
                    if self.object_class == 'TTextAndImage' and field == 'variables':
                        data[field][i] = (data[field][i][0], utils.replace_HTML_entities(data[field][i][1]))
                    if hasattr(data[field][i], 'prepare_for_spold'):
                        data[field][i] = data[field][i].prepare_for_spold(MD, mapping)
                    elif type(data[field]) in [str, objectify.StringElement]:
                        data[field] = utils.replace_HTML_entities(data[field])
                    elif type(data[field]) in [objectify.ObjectifiedElement, int, set, float, 
                             numpy.float64, numpy.int64, numpy.long, dict, numpy.int32, type(None)]:
                        pass
                    else:
                        NotImplementedError
            else:
                raise NotImplementedError
        if hasattr(self, 'template_name'):
            template_name = self.template_name
        else:
            template_name = '{}_2.xml'.format(self.object_class)
        template = env.get_template(template_name)
        output = template.render(**data)
        return output

class Dataset(BaseClass):
    '''This class works on undefined and linked datasets'''
    def __init__(self, folder, filename, allow_pkl_read = True, refresh_pkl = False):
        
        #basic information
        self.refresh_pkl = refresh_pkl
        self.object_class = 'Dataset'
        self.validation_extra_info = ''
        self.filename = filename
        self.folder = folder
        
        #stem is used by the Multi_Dataset constructor
        self.use_pkl_source = False
        if allow_pkl_read:
            alternate_folder, alternate_filename = self.pkl_name_from_spold()
            if os.path.exists(alternate_folder):
                pkl_file = os.path.join(alternate_folder, alternate_filename)
                if os.path.exists(pkl_file):
                    self.use_pkl_source = True
            else:
                os.makedirs(alternate_folder)
        use_spold = True
        if self.use_pkl_source:
            try:
                f = utils.pkl_load(alternate_folder, alternate_filename)
                for attr in utils.list_attributes(f):
                    setattr(self, attr, getattr(f, attr))
                use_spold = False
            except:
                pass#will be go on to spold reading
        if use_spold:
            with open(os.path.join(folder, filename), encoding='utf8') as f:
                root = objectify.parse(f).getroot()
                if hasattr(root, 'activityDataset'):
                    stem = root.activityDataset
                else:
                    stem = root.childActivityDataset
            if 'child' in stem.tag:
                self.activityDataset = 'childActivityDataset'
            else:
                self.activityDataset = 'activityDataset'
            self.is_child = self.activityDataset == 'childActivityDataset'
            
            for attr, value in iterate_object(stem, self.is_child).items():
                setattr(self, attr, value)
            
            for group in spold2_utils.groups:
                setattr(self, group, [])
            for field in ['intermediateExchange', 'elementaryExchange']:
                if hasattr(self, field):
                    for exc in getattr(self, field):
                        if exc.group != 'parentvalue':
                            getattr(self, exc.group).append(exc)
        if not hasattr(self, 'classifications_dict'):
            self.classifications_dict = {c.classificationSystem: c for c in self.classifications}
        if self.refresh_pkl:
            alternate_folder, alternate_filename = self.pkl_name_from_spold()
            utils.pkl_dump(alternate_folder, alternate_filename, self)
        
        self.all_exchanges = {}
        fields = ['group', 'name', 'compartment', 'subcompartment', 'activityLinkId']
        for exc in self.iterate_exchanges():
            baseline = exc.baseline()
            key = tuple([baseline[field] for field in fields])
            self.all_exchanges[key] = copy(exc)
    
    def pkl_name_from_spold(self):
        alternate_folder = os.path.dirname(self.folder)
        a = os.path.basename(self.folder)
        alternate_folder = os.path.join(alternate_folder, '{}_pkl'.format(a))
        alternate_filename = self.filename.split('.')
        alternate_filename[-1] = 'pkl'
        alternate_filename = '.'.join(alternate_filename)
        return alternate_folder, alternate_filename
    
    def get_all_exchanges(self):
        l = []
        for group in spold2_utils.groups:
            l.extend(self.get(group))
        
        return l
            
    def write_to_spold(self, result_folder, hide_confidential = True, cute_name = False, 
            refresh_exchanges = True, indexes = '', MD = '', 
            A_offset = 0, mapping = '', counter = '', timestamp = '', 
            source_number = '', person_number = '', mapping_restrictedAccess = '', 
            version = '', LCI_folder = '', impactAssessmentResult = False):
        if refresh_exchanges:
            self.exchanges = self.get_all_exchanges()
        if cute_name:
            self.build_cute_name()
        if not hasattr(self, 'exchanges'):
            counter = 0
            self.exchanges = []
            for exc in self.iterate_exchanges():
                counter += 1
                exc.number = counter
                self.exchanges.append(exc)
        
        if not hasattr(self, 'fileAttributes'):
            self.fileAttributes = FileAttribute({})
        print('creating %s in %s' % (self.filename, result_folder))
        output_filename = os.path.join(result_folder, self.filename)
        output = self.prepare_for_spold(MD, mapping)
        if '\ufeff' in output:
            output = output.replace('\ufeff', '')
        writer = open(output_filename, 'w', encoding = 'utf-8')
        writer.write(output)
        writer.close()
    
class Exchange(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'Exchange'
        
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
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
        else:
            if not is_child:
                raise ValueError
            else:
                self.group = 'parentvalue'
        if 'From' in self.group:
            self.groupType = 'inputGroup'
        else:
            self.groupType = 'outputGroup'
        self.groupCode = spold2_utils.meta_translator[self.groupType][self.group]
        
        if hasattr(self, 'properties'):
            self.properties_dict = {p.name: p for p in self.properties}
        if 'Environment' in self.group:
            self.validation_extra_info = 'elementaryExchange'
            self.exchangeType = 'elementaryExchange'
        else:
            self.validation_extra_info = 'intermediateExchange'
            self.exchangeType = 'intermediateExchange'
        self.add_default_values()
        if hasattr(self, 'properties'):
            for i in range(len(self.properties)):
                self.properties[i].exchange_baseline = self.baseline()
        else:
            self.properties = []
        self.remove_dummy_properties()
        self.properties_dict = {p.name: p for p in self.properties}#fix me? which one is used?
        if not hasattr(self, 'classifications_dict') and 'Environment' not in self.group:
            self.classifications_dict = {c.classificationSystem: c for c in self.classifications}#fix me? which one is used?
        self.comment = [c for c in self.comment if 'EcoSpold01Location=' not in c]
        if hasattr(self, 'productionVolumeUncertainty'):
            self.productionVolumeUncertainty.field = 'productionVolumeUncertainty'
        if hasattr(self, 'uncertainty'):
            self.uncertainty.field = 'uncertainty'
    
    def remove_dummy_properties(self):
        to_remove = 'EcoSpold01Allocation'
        self.properties = [p for p in self.properties if to_remove not in p.name]
        self.properties_dict = {p.name: p for p in self.properties}
    
    
    def write_to_spold(self, indexes, MD, mapping):
        if self.amount <= 0. and hasattr(self, 'uncertainty'):
            delattr(self, 'uncertainty')
        if 'Environment' in self.group:
            self.exchangeType = 'elementaryExchange'
        else:
            self.exchangeType = 'intermediateExchange'
        if hasattr(self, 'comment') and type(self.comment) == list:
            self.comment = '\n'.join(self.comment)
    
        
class TTextAndImage(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'TTextAndImage'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        self.comments_original = []
        for i in range(1000):
            had_comment = False
            for field in ['text', 'imageUrl']:
                if hasattr(self, field) and len(getattr(self, field)) > i:
                    if not utils.is_empty(getattr(self, field)[i]):
                        self.comments_original.append((field, getattr(self, field)[i]))
                        had_comment = True
            if not had_comment and i > 0:
                break
        self.comments = []
        if not hasattr(self, 'variables'):
            self.variables = []
        for i in range(len(self.comments_original)):
            field, c = self.comments_original[i]
            if '{{' in c:
                c = c.replace('{{ ', '{{').replace(' }}', '}}')
                for var, value in self.variables:
                    c = c.replace('{{'+var+'}}', value)
            self.comments.append((field, c))
        
        #assembling the comments in one string, for printing convenience
        self.len = len(self.comments)
        if len(self.comments) == 0:
            self.assembled = ''
        else:
            self.assembled = self.comments[0][1]
            if len(self.comments) > 1:
                for c in self.comments[1:]:
                    self.assembled = '{}\n{}'.format(self.assembled, c[1])
        self.assembled = self.assembled.replace(spold2_utils.imageUrl_tag_replace[0], spold2_utils.imageUrl_tag_replace[1])
    
    
class TUncertainty(BaseClass):
    def __init__(self, o, prefix = '', is_child = False):
        self.object_class = 'TUncertainty'
        #self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        for c in o.iterchildren():
            if 'pedigreeMatrix' in c.tag:
                self.pedigreeMatrix = []
                for criteria in spold2_utils.pedigreeCriteria:
                    if hasattr(self, criteria):
                        self.pedigreeMatrix.append(int(getattr(self, criteria)))
                    elif is_child:
                        self.pedigreeMatrix.append('parentvalue')
                    else:
                        raise ValueError
            elif 'comment' not in c.tag:
                self.type = c.tag.replace(spold2_utils.tag_re.match(c.tag).group(), '')
        self.validation_extra_info = self.type
        
        if self.type in ['lognormal', 'normal']:
            if not hasattr(self, 'pedigreeMatrix') or utils.is_empty(
                    self.pedigreeMatrix) or self.pedigreeMatrix == [
                    '']*len(spold2_utils.pedigreeCriteria):
                self.pedigreeMatrix = [5, 5, 5, 5, 5]
                
        #calculate varianceWithPedigreeUncertainty if possible and missing
        if hasattr(self, 'pedigreeMatrix') and (
                {0, ''}.isdisjoint(set(self.pedigreeMatrix)) and 
                hasattr(self, 'variance') and not hasattr(
                self, 'varianceWithPedigreeUncertainty')):
            self.varianceWithPedigreeUncertainty = self.calculate_varianceWithPedigreeUncertainty()
        self.validation_extra_info = self.type
        if hasattr(self, 'uncertainty'):
            self.uncertainty.field = 'uncertainty'
    
    def calculate_varianceWithPedigreeUncertainty(self):
        forbiden = {0, ''}.intersection(set(self.pedigreeMatrix))
        assert len(forbiden) == 0, 'Pedigree contains forbiden element(s): %s' % str(forbiden)
        assert hasattr(self, 'variance'), 'Variance not available'
        numpy.sum(numpy.multiply(numpy.array(self.pedigreeMatrix, ndmin = 2).transpose(), 
                                 spold2_utils.pedigree_factors))
        var = copy(self.variance)
        for i in range(len(self.pedigreeMatrix)):
            var += spold2_utils.pedigree_factors[i, self.pedigreeMatrix[i]]
        
        return var
    
    def calculate_mu(self):
        if self.type == 'lognormal':
            self.mu = numpy.log(self.meanValue)
    
class TClassification(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'TClassification'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
    
class TProperty(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'TProperty'
        self.validation_extra_info = ''
        self.add_default_values()
        self.exchange_baseline = {}
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        if not hasattr(self, 'unitName'):
            self.unitName = ''
    
class TParameter(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'TParameter'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        
        if not hasattr(self, 'unitName') or utils.is_empty(self.unitName):
            #these are listed as optional in the schema, but it causes problem later
            #so they are forced to "dimensionless" when absent
            self.unitName = 'dimensionless'
            self.unitId = '577e242a-461f-44a7-922c-d8e1c3d2bf45'
        if hasattr(self, 'uncertainty'):
            self.uncertainty.field = 'uncertainty'
    
        
class DataGeneratorAndPublication(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'DataGeneratorAndPublication'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        
class DataEntryBy(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'DataEntryBy'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)

    
class FileAttribute(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'FileAttribute'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        
        
class ModellingAndValidation(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'ModellingAndValidation'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)
        
        
class Review(BaseClass):
    def __init__(self, o, is_child = False):
        self.object_class = 'Review'
        self.validation_extra_info = ''
        self.add_default_values()
        for attr, value in iterate_object(o, is_child).items():
            setattr(self, attr, value)  
    
constructors = {
    #standard
    'int': [int, numpy.int32], 
    'str': [str], 
    'float': [float, numpy.float32, numpy.float64], 
    #ecoinvent
    'FileAttributes': [FileAttribute], 
    'fileAttributes': [FileAttribute], 
    'TTextAndImage': [TTextAndImage], 
    'DataGeneratorAndPublication': [DataGeneratorAndPublication], 
    'dataGeneratorAndPublication': [DataGeneratorAndPublication], 
    'TClassification': [TClassification], 
    'bool': [utils._bool, numpy.bool, numpy.bool8, numpy.bool_], 
    'Exchange': [Exchange], 
    'Exchanges': [Exchange], 
    'TProperty': [TProperty], 
    'TUncertainty': [TUncertainty], 
    'TParameter': [TParameter], 
    'DataEntryBy': [DataEntryBy], 
    'dataEntryBy': [DataEntryBy], 
    'ModellingAndValidation': [ModellingAndValidation], 
    'modellingAndValidation': [ModellingAndValidation], 
    'Review': [Review], 
    'review': [Review], 
                }


def iterate_object(o, is_child):
    d = {}
    element_tag = o.tag.replace(spold2_utils.tag_re.match(o.tag).group(), '')
    for attr, value in o.attrib.items():
        key = (element_tag, attr)
        sel = spold2_utils.schema[key]
        if not sel['ignore']:
            field = sel['Python name']
            assert not utils.is_empty(field)
            d[field] = constructors[sel['Python type']][0](value)
        
    for c in o.iterchildren():
        field_tag = c.tag.replace(spold2_utils.tag_re.match(c.tag).group(), '')
        key = (element_tag, field_tag)
        if key == ('childActivityDataset', 'originalActivityDataset'):
            for cc in c.iterchildren():
                if 'ecoSpold' in cc.tag:
                    break
            d['originalActivityDataset'] = Dataset('', '', stem = cc.activityDataset, 
                 allow_pkl_read = False, refresh_pkl = False)
        else:
            sel = spold2_utils.schema[key]
            if not sel['ignore']:
                field = sel['Python name']
                if sel['multiple']:
                    assert not utils.is_empty(field)
                    if field not in d:
                        d[field] = []
                    if field == 'text':
                        if int(c.get('index')) >= len(d[field]):
                            d[field].extend(['']*(int(c.get('index')) - len(d[field])+1))
                        d[field][int(c.get('index'))] = str(c.text)
                    elif field == 'variables':
                        d[field].append((c.get('name'), str(c.text)))
                    else:
                        try:
                            signature = str(inspect.signature(constructors[sel['Python type']][0]))
                        except ValueError:
                            signature = []
                        except:
                            1/0#fix me now
                        if 'is_child' in signature:
                            d[field].append(constructors[sel['Python type']][0](c, is_child = is_child))
                        else:
                            d[field].append(constructors[sel['Python type']][0](c))
                elif utils.is_empty(sel['Python type']):
                    d.update(iterate_object(c, is_child))
                else:
                    assert not utils.is_empty(field)
                    try:
                        signature = str(inspect.signature(constructors[sel['Python type']][0]))
                    except ValueError:
                        signature = []
                    except:
                        1/0#fix me now
                    if 'is_child' in signature:
                        d[field] = constructors[sel['Python type']][0](c, is_child = is_child)
                    else:
                        d[field] = constructors[sel['Python type']][0](c)
            
    return d

if __name__ == '__main__':
    folder = r'C:\Dropbox (ecoinvent)\ei-int\technical\releases\3.4\Undefined\datasets'
    filename = '0a3ac992-aa33-4872-9b01-6e1857b79d9b.spold'
    f = TestObject('', folder = folder, filename = filename)