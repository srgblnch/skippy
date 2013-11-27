#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        commandSet.py
## 
## Project :     SCPI
##
## $Author :      sblanch$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##        (c) - Controls Software Section - ALBA/CELLS
##############################################################################

import PyTango
import traceback
import functools

def identifier(idn,deviceObj):
    '''This method has been designed to understand from the answer of an 
       instrument to the '*IDN?' command, what is the correct object that
       contains the set of commands for this instrument.
    '''
    company,model,serial,firmware = idn.split('\n')[0].split(',')
    #TODO: builder pattern to create the object with the instructions set
    #      for this instrument.
    if company.lower() == 'agilent technologies':
        if model.upper().startswith('DSO'):
            #This is a series of scopes and this has been tested with 
            #the DSO80204B Agilent scope
            attrList = AttributeBuilder(deviceObj)
            file = "instructions/scope/agilentDSO.py"
        else:
            raise EnvironmentError("Agilent %s model not supported"%(model))
    elif company.lower() == 'tektronix':
        if model.upper().startswith('DPO'):
            attrList = AttributeBuilder(deviceObj)
            file = "instructions/scope/tektronixDPO.py"
        elif model.upper().startswith('AFG'):
            attrList = AttributeBuilder(deviceObj)
            file = "instructions/arbitraryFunctionGenerator/tektronicsAFG.py"
        raise EnvironmentError("Tektronix %s model not supported"%(model))
    elif company.lower() == 'rohde&schwarz':
        if model.lower() == 'sma100a':
            attrList = AttributeBuilder(deviceObj)
            file = "instructions/radioFrequencyGenerator/rohdeSchwarzRFG.py"
        else:
            raise EnvironmentError("Rohde&Schwarz %s model not supported"%(model))
    else:
        raise EnvironmentError("instrument not supported")
    attrList.parseFile(file)

def AttrExc(function):
    '''Decorates commands so that the exception is logged and also raised.
    '''
    #TODO: who has self._trace?
    def nestedMethod(self, attr, *args, **kwargs):
        inst = self #< for pychecker
        try:
            return function(inst, attr, *args, **kwargs)
        except Exception, exc:
            traceback.print_exc(exc)
            #self._trace = traceback.format_exc(exc)
            raise
    functools.update_wrapper(nestedMethod,function)
    return nestedMethod

def latin1(x):
  return x.decode('utf-8').replace(u'\u2070', u'\u00b0').replace(u'\u03bc',u'\u00b5').encode('latin1')

class AttributeBuilder:
    def __init__(self,parent):
        '''parent: device object to who apply the dynamic attributes
           
        '''
        self.__device = parent
        self.__attributeList = list()
        self.locals_ = { }

        self.globals_ = globals()
        self.globals_.update({
            'Attribute':self.add_Attribute
        })
    
    def parseFile(self,fName):
#         self.__device.debug_stream('%30s\t%10s\t%5s\t%6s\t%6s'\
#                                    %("attrName","Type",'RO/RW',"read","write"))
        self.__device.info_stream("Start parsing the attribute file")
        try:
            execfile(fName,self.globals_,self.locals_)
        except Exception,e:
            self.__device.debug_stream("AttributeBuilder.parseFile Exception: "\
                                       "%s\n%s"%(e,traceback.format_exc()))
        self.__device.debug_stream('Parse of the attribute file done.')

    def parse(self, text):
        exec text in self.globals_, self.locals_
    
    def add_Attribute(self,attributeName,attributeDefinition):
        '''Method to dynamically add an attribute
           The parameter is a the name of the attribute, followed by a 
           dictionary with mandatory keys:
           - type: tango data type of the attribute
           - dim:  dimensions of the attribute.
                   it can be: 0 for scalars
                             [1,X] for spectrums and its length
                             [2,X,Y] for images and its dimensions
           - readCmd: method to be called to have the scpi read command
           There are also optional keys:
           - writeCmd:  method to be called to have the scpi write command
           - channels:  boolean to indicate if this must be replicated 
                        per all the channels
           - functions: boolean to indicate if this must be replicated 
                        per all the functions
           TODO: attribute configuration (like unit, label, etc)
        '''
        #preconditions
        if not type(attributeDefinition) == dict:
            raise AttributeError("Invalid definition of the attribute %s"
                                 %(attributeName))
        for k in ['type','dim','readCmd']:
            if not attributeDefinition.has_key(k):
                raise KeyError("Invalid definition, key %s is mandatory"%(k))

        #If the attribute definition includes channels and functions, 
        #do it in loop
        if attributeDefinition.has_key('channels') or attributeDefinition.has_key('functions'):
            if attributeDefinition.has_key('channels') and \
               attributeDefinition['channels'] and \
               self.__device.NumChannels > 0:
                for ch in range(1,self.__device.NumChannels+1):
                    try:
                        attr = self.__getAttrObj( "%sCh%d"%(attributeName,ch),attributeDefinition,channel=ch)
                        self.__device.debug_stream("Added attribute: %s"%attr.get_name())
                    except Exception,e:
                        self.__device.error_stream("NOT added attribute: %sCh%d "\
                                                   "due to exception: %s"
                                                   %(attributeName,ch,e))
                        traceback.print_exc()
            if attributeDefinition.has_key('functions') and \
               attributeDefinition['functions'] and \
               self.__device.NumFunctions > 0:
                for fn in range(1,self.__device.NumFunctions+1):
                    try:
                        attr = self.__getAttrObj("%sFn%d"%(attributeName,fn),attributeDefinition,function=fn)
                        self.__device.debug_stream("Added attribute: %s"%attr.get_name())
                    except Exception,e:
                        self.__device.error_stream("NOT added attribute: %sFn%d "\
                                                   "due to exception: %s"
                                                   %(attributeName,fn,e))
                        traceback.print_exc()
        #when is a single attribute, no loop required
        else:
            try:
                attr = self.__getAttrObj(attributeName, attributeDefinition)
                self.__device.debug_stream("Added attribute: %s"%attr.get_name())
            except Exception,e:
                self.__device.error_stream("NOT added attribute: %s "\
                                           "due to exception: %s"
                                           %(attributeName,e))
                traceback.print_exc()

    def __getAttrObj(self,attrName,definition,channel=None,function=None):
        #TODO: image dimensions
        if definition['dim'] == [0]:
            if definition.has_key('writeCmd'):
                attr = PyTango.Attr(attrName,definition['type'],PyTango.READ_WRITE)
                readmethod = AttrExc(getattr(self.__device,'read_attr'))
                writemethod = AttrExc(getattr(self.__device,'write_attr'))
            else:
                attr = PyTango.Attr(attrName,definition['type'],PyTango.READ)
                readmethod = AttrExc(getattr(self.__device,'read_attr'))
                writemethod = None
        elif definition['dim'][0] == 1:
            if definition.has_key('writeCmd'):
                attr = PyTango.SpectrumAttr(attrName,definition['type'],
                                            PyTango.READ_WRITE,definition['dim'][1])
                readmethod = AttrExc(getattr(self.__device,'read_attr'))
                writemethod = AttrExc(getattr(self.__device,'write_attr'))
            else:
                attr = PyTango.SpectrumAttr(attrName,definition['type'],
                                            PyTango.READ,definition['dim'][1])
                readmethod = AttrExc(getattr(self.__device,'read_attr'))
                writemethod = None
        else:
            raise AttributeError("Not supported dimensions")
        #attribute properties
        aprop = PyTango.UserDefaultAttrProp()
        if definition.has_key('unit'):
            aprop.set_unit(latin1(definition['unit']))
        if definition.has_key('min'):
            aprop.set_min_value(str(definition['min']))
        if definition.has_key('max'):
            aprop.set_max_value(str(definition['max']))
        if definition.has_key('format'):
            aprop.set_format(latin1(definition['format']))
        if definition.has_key('description'):
            aprop.set_description(latin1(definition['description']))
        if definition.has_key('label'):
            aprop.set_label(latin1(definition['label']))
        if definition.has_key('memorized'):
            attr.set_memorized_init(True)
        attr.set_default_properties(aprop)
        
        self.__device.add_attribute(attr, r_meth=readmethod, w_meth=writemethod)
        self.__attributeList.append(attr)
        self.__device.attributes[attrName] = {'lastReadValue':None,
                                              'timestamp':None,
                                              'quality':PyTango.AttrQuality.ATTR_INVALID}
        if definition.has_key('writeCmd'):
            self.__device.attributes[attrName]['lastWriteValue'] = None
        if channel:
            self.__device.attributes[attrName]['readStr'] = definition['readCmd']("CHAN",channel)
            if definition.has_key('writeCmd'):
                self.__device.attributes[attrName]['writeStr'] = definition['writeCmd']("CHAN",channel)
            if definition.has_key('manager') and definition['manager'] == True:
                self.__device.attributesFlags["Ch%d"%channel] = attrName
        elif function:
            self.__device.attributes[attrName]['readStr'] = definition['readCmd']("FUNC",function)
            if definition.has_key('writeCmd'):
                self.__device.attributes[attrName]['writeStr'] = definition['writeCmd']("FUNC",function)
            if definition.has_key('manager') and definition['manager'] == True:
                self.__device.attributesFlags["Fn%d"%function] = attrName
        else:
            self.__device.attributes[attrName]['readStr'] = definition['readCmd']
            if definition.has_key('writeCmd'):
                self.__device.attributes[attrName]['writeStr'] = definition['writeCmd']
        if definition.has_key('rampeable'):
            db = PyTango.Database()
            step = PyTango.Attr(attrName+"Step",definition['type'],PyTango.READ_WRITE)
            step.set_memorized_init(True)
            self.__device.add_attribute(step, r_meth=readmethod, w_meth=writemethod)
            self.__attributeList.append(step)
            try:
                self.__device.attributes[attrName]['rampStep'] = float(db.get_device_attribute_property(self.__device.get_name(),attrName+"Step")[attrName+"Step"]['__value'][0])
            except:
                self.__device.attributes[attrName]['rampStep'] = None
            stepspeed = PyTango.Attr(attrName+"StepSpeed",PyTango.CmdArgType.DevDouble,PyTango.READ_WRITE)
            stepspeed.set_memorized_init(True)
            self.__device.add_attribute(stepspeed, r_meth=readmethod, w_meth=writemethod)
            self.__attributeList.append(stepspeed)
            try:
                self.__device.attributes[attrName]['rampStepSpeed'] = float(db.get_device_attribute_property(self.__device.get_name(),attrName+"StepSpeed")[attrName+"StepSpeed"]['__value'][0])
            except:
                self.__device.attributes[attrName]['rampStepSpeed'] = None
            self.__device.attributes[attrName]['rampThread'] = None
        if definition.has_key('writeValues'):
            self.__device.attributes[attrName]['writeValues'] = definition['writeValues']
        self.__device.attributes[attrName]['type'] = definition['type']
        self.__device.attributes[attrName]['dim'] = definition['dim'][0]
        self.__device.debug_stream("New attribute build: %s:%s"
                                   %(attrName,self.__device.attributes[attrName]))
        return attr
        
    #TODO: remove dynamic attributes
    #      remember to clean the self.__device.attributes 
    #      and the self.__attributeList
