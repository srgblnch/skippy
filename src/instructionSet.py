# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

import PyTango
import traceback
import functools


def identifier(idn, deviceObj):
    '''This method has been designed to understand from the answer of an
       instrument to the '*IDN?' command, what is the correct object that
       contains the set of commands for this instrument.
    '''
    company = ''
    for separator in (',', ' '):
        try:
            company, model, serial, firmware = \
                idn.split('\n')[0].split(separator)[:4]
        except:
            continue
    # TODO: builder pattern to create the object with the instructions set
    #       for this instrument.
    if company.lower() == 'agilent technologies':
        if model.upper().startswith('DSO'):
            # This is a series of scopes and this has been tested with
            # the DSO80204B Agilent scope
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/scope/agilentDSO.py"
        else:
            raise EnvironmentError("Agilent %s model not supported" % (model))
    elif company.lower() == 'tektronix':
        if model.upper().startswith('DPO'):
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/scope/tektronixDPO.py"
        elif model.upper().startswith('AFG'):
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/arbitraryFunctionGenerator/tektronicsAFG.py"
        raise EnvironmentError("Tektronix %s model not supported" % (model))
    elif company.lower() == 'rohde&schwarz':
        if model.lower() == 'sma100a':
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/radioFrequencyGenerator/rohdeSchwarzRFG.py"
        elif model.lower() == 'fsp-3':
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/spectrumAnalyser/rohdeSchwarzFSP.py"
        else:
            raise EnvironmentError("Rohde&Schwarz %s model not supported"
                                   % (model))
    elif company.lower() == 'arroyo':
        if model.lower() == '5300':
            attrBuilder = AttributeBuilder(deviceObj)
            file = "instructions/temperatureController/arroyo5300.py"
        else:
            raise EnvironmentError("Arroyo %s model not supported" % (model))
    else:
        raise EnvironmentError("instrument not supported")
    attrBuilder.parseFile(file)
    return attrBuilder


def AttrExc(function):
    '''Decorates commands so that the exception is logged and also raised.
    '''
    # TODO: who has self._trace?
    def nestedMethod(self, attr, *args, **kwargs):
        inst = self  # < for pychecker
        try:
            return function(inst, attr, *args, **kwargs)
        except Exception, exc:
            traceback.print_exc(exc)
            # self._trace = traceback.format_exc(exc)
            raise
    functools.update_wrapper(nestedMethod, function)
    return nestedMethod


def latin1(x):
    return x.decode('utf-8').replace(u'\u2070', u'\u00b0').\
        replace(u'\u03bc', u'\u00b5').encode('latin1')


###############################
# Attribute functionalities ---

class RampObj(object):
    def __init__(self, name, *args, **kwargs):
        super(RampObj, self).__init__(*args, **kwargs)
        self._rampStep = None
        self._rampStepSpeep = None
        self._rampThread = None

    @property
    def rampStep(self):
        return self._rampStep

    @rampStep.setter
    def rampStep(self, value):
        self._rampStep = value

    @property
    def rampStepSpeep(self):
        return self._rampStepSpeep

    @rampStepSpeep.setter
    def rampStepSpeep(self, value):
        self._rampStepSpeep = value

    @property
    def rampThread(self):
        return self._rampThread

    @rampThread.setter
    def rampThread(self, value):
        self._rampThread = value


class RawDataObj(object):
    def __init__(self, *args, **kwargs):
        super(RawDataObj, self).__init__(*args, **kwargs)
        self._lastReadRaw = None

    @property
    def lastReadRaw(self):
        return self._lastReadRaw

    @lastReadRaw.setter
    def lastReadRaw(self, value):
        self._lastReadRaw = value


###############################
# Attribute Objects ---


class AttributeObj(object):
    def __init__(self, name, type, dim, readCmd, withRawData=False,
                 *args, **kwargs):
        super(AttributeObj, self).__init__(*args, **kwargs)
        self._name = name
        self._type = type
        self._dim = dim
        self._readCmd = readCmd
        self._lastReadValue = None
        self._timestamp = None
        self._quality = PyTango.AttrQuality.ATTR_INVALID
        if withRawData:
            self._raw = RawDataObj()
        else:
            self._raw = None

    def __str__(self):
        return "%s {lastReadValue: %s, timestamp: %s, quality: %s, dim: %s}"\
               % (self.name, self.lastReadValue, self.timestamp, self.quality,
                  self.dim)

    def __repr__(self):
        return "%s, readCmd: %s}"\
               % (self.__str__()[:-1], self.readCmd)

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def dim(self):
        return self._dim

    def isWritable(self):
        return False

    def isRampeable(self):
        return False

    def hasWriteValues(self):
        return False

    def hasRawData(self):
        if self._raw is None:
            return False
        return True

    @property
    def readCmd(self):
        return self._readCmd

    @property
    def lastReadValue(self):
        return self._lastReadValue

    @lastReadValue.setter
    def lastReadValue(self, value):
        self._lastReadValue = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        self._quality = value

    def _makeRawDataProperties(self):
        setattr(self, 'lastReadRaw', self._makeLastReadRawProperty())

    def _makeLastReadRawProperty(self):
        def getter(self):
            return self._raw.lastReadRaw

        def setter(self, value):
            self._raw.lastReadRaw = value

        return property(getter, setter)


class WAttributeObj(AttributeObj):
    def __init__(self, writeCmd=None, rampeable=False, writeValues=None,
                 *args, **kwargs):
        super(WAttributeObj, self).__init__(*args, **kwargs)
        self._writeCmd = writeCmd
        self._lastWriteValue = None
        self._ramp = None
        if rampeable:
            self.makeRampeable()
        self._writeValues = writeValues

    def __str__(self):
        return "%s {lastReadValue: %s, lastWriteValue: %s, timestamp: %s, "\
               "quality: %s, dim: %s}"\
               % (self.name, self.lastReadValue, self.lastWriteValue,
                  self.timestamp, self.quality, self.dim)

    def __repr__(self):
        return "%s, readCmd: %s, writeCmd: %s}"\
               % (self.__str__()[:-1], self.readCmd, self.writeCmd)

    def isWritable(self):
        return True

    def isRampeable(self):
        if self._ramp is None:
            return False
        return True

    def hasWriteValues(self):
        return self._writeValues is not None

    @property
    def writeCmd(self):
        return self._writeCmd

    @property
    def lastWriteValue(self):
        return self._lastWriteValue

    @lastWriteValue.setter
    def lastWriteValue(self, value):
        self._lastWriteValue = value

    def makeRampeable(self):
        if self._ramp is None:
            self._ramp = RampObj()
            setattr(self, 'rampStep', self._makeRampStepProperty())
            setattr(self, 'rampStepSpeed', self._makeRampStepSpeedProperty())
            setattr(self, 'rampThread', self._makeRampThreadProperty())

    def _makeRampStepProperty(self):
        def getter(self):
            return self._ramp.rampStep

        def setter(self, value):
            self._ramp.rampStep = value

        return property(getter, setter)

    def _makeRampStepSpeedProperty(self):
        def getter(self):
            return self._ramp.rampStepSpeed

        def setter(self, value):
            self._ramp.rampStepSpeed = value

        return property(getter, setter)

    def _makeRampThreadProperty(self):
        def getter(self):
            return self._ramp.rampThread

        def setter(self, value):
            self._ramp.rampThread = value

        return property(getter, setter)

    def setWriteValues(self, writeValues):
        self._writeValues = writeValues


class AttributeBuilder:
    def __init__(self, parent):
        '''parent: device object to who apply the dynamic attributes
        '''
        self.__device = parent
        self._attributeList = list()
        self.locals_ = {}

        self.globals_ = globals()
        self.globals_.update({
            'Attribute': self.add_Attribute
        })

    def parseFile(self, fName):
        # self.__device.debug_stream('%30s\t%10s\t%5s\t%6s\t%6s'
        #                            % ("attrName", "Type", 'RO/RW', "read",
        #                               "write"))
        self.__device.info_stream("Start parsing the attribute file")
        try:
            execfile(fName, self.globals_, self.locals_)
        except Exception as e:
            self.__device.debug_stream("AttributeBuilder.parseFile Exception: "
                                       "%s\n%s" % (e, traceback.format_exc()))
        self.__device.debug_stream('Parse of the attribute file done.')

    def parse(self, text):
        exec text in self.globals_, self.locals_

    def add_Attribute(self, attributeName, attributeDefinition):
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
           - format:    format to display information
           - label:     human string about the attribute
           - description: longer text for humans
           - unit:      extra attribute information
           - min/max:   ranges
           - memorized: to be stored the writes in a database
           TODO: attribute input validation
           TODO: dependencies between attributes (state-like, mode,...)
           TODO: expert attributes flag
           TODO: formulas to transform input before send and write after
                 receive.
        '''
        # preconditions
        if not type(attributeDefinition) == dict:
            raise AttributeError("Invalid definition of the attribute %s"
                                 % (attributeName))
        for k in ['type', 'dim', 'readCmd']:
            if k not in attributeDefinition:
                raise KeyError("Invalid definition, key %s is mandatory" % (k))

        # If the attribute definition includes channels and functions,
        # do it in loop
        if 'channels' in attributeDefinition or \
                'functions' in attributeDefinition:
            if 'channels' in attributeDefinition and \
                    attributeDefinition['channels'] and \
                    self.__device.NumChannels > 0:
                for ch in range(1, self.__device.NumChannels+1):
                    try:
                        attr = self.__getAttrObj("%sCh%d"
                                                 % (attributeName, ch),
                                                 attributeDefinition,
                                                 channel=ch)
                        self.__device.debug_stream("Added attribute: %s"
                                                   % (attr.get_name()))
                    except Exception as e:
                        self.__device.error_stream("NOT added attribute: "
                                                   "%sCh%d due to exception: "
                                                   "%s" % (attributeName,
                                                           ch, e))
                        traceback.print_exc()
            if 'functions' in attributeDefinition and \
               attributeDefinition['functions'] and \
               self.__device.NumFunctions > 0:
                for fn in range(1, self.__device.NumFunctions+1):
                    try:
                        attr = self.__getAttrObj("%sFn%d"
                                                 % (attributeName, fn),
                                                 attributeDefinition,
                                                 function=fn)
                        self.__device.debug_stream("Added attribute: %s"
                                                   % (attr.get_name()))
                    except Exception as e:
                        self.__device.error_stream("NOT added attribute: "
                                                   "%sFn%d due to exception: "
                                                   "%s" % (attributeName,
                                                           fn, e))
                        traceback.print_exc()
        # when is a single attribute, no loop required
        else:
            try:
                attr = self.__getAttrObj(attributeName, attributeDefinition)
                self.__device.debug_stream("Added attribute: %s"
                                           % (attr.get_name()))
            except Exception as e:
                self.__device.error_stream("NOT added attribute: %s "
                                           "due to exception: %s"
                                           % (attributeName, e))
                traceback.print_exc()

    def __getAttrObj(self, attrName, definition, channel=None, function=None):
        # TODO: image dimensions
        if definition['dim'] == [0]:
            if 'writeCmd' in definition:
                attr = PyTango.Attr(attrName, definition['type'],
                                    PyTango.READ_WRITE)
                readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                writemethod = AttrExc(getattr(self.__device, 'write_attr'))
            else:
                attr = PyTango.Attr(attrName, definition['type'], PyTango.READ)
                readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                writemethod = None
        elif definition['dim'][0] == 1:
            if 'writeCmd' in definition:
                attr = PyTango.SpectrumAttr(attrName, definition['type'],
                                            PyTango.READ_WRITE,
                                            definition['dim'][1])
                readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                writemethod = AttrExc(getattr(self.__device, 'write_attr'))
            else:
                attr = PyTango.SpectrumAttr(attrName, definition['type'],
                                            PyTango.READ, definition['dim'][1])
                readmethod = AttrExc(getattr(self.__device, 'read_attr'))
                writemethod = None
        else:
            raise AttributeError("Not supported dimensions")
        # attribute properties
        aprop = PyTango.UserDefaultAttrProp()
        if 'unit' in definition:
            aprop.set_unit(latin1(definition['unit']))
        if 'min' in definition:
            aprop.set_min_value(str(definition['min']))
        if 'max' in definition:
            aprop.set_max_value(str(definition['max']))
        if 'format' in definition:
            aprop.set_format(latin1(definition['format']))
        if 'description' in definition:
            aprop.set_description(latin1(definition['description']))
        if 'label' in definition:
            aprop.set_label(latin1(definition['label']))
        if 'memorized' in definition:
            attr.set_memorized_init(True)
        attr.set_default_properties(aprop)
        self.__device.add_attribute(attr, r_meth=readmethod,
                                    w_meth=writemethod)
        self._attributeList.append(attrName)
        # prepare internal structure ---
        if channel:
            readCmd = definition['readCmd']("CHAN", channel)
            if 'writeCmd' in definition:
                writeCmd = definition['writeCmd']("CHAN", channel)
            if 'manager' in definition and definition['manager'] is True:
                self.__device.attributesFlags["Ch%d" % channel] = attrName
        elif function:
            readCmd = definition['readCmd']("FUNC", function)
            self.__device.attributes[attrName]['readStr'] = readCmd
            if 'writeCmd' in definition:
                writeCmd = definition['writeCmd']("FUNC", function)
            if 'manager' in definition and definition['manager'] is True:
                self.__device.attributesFlags["Fn%d" % function] = attrName
        else:
            readCmd = definition['readCmd']
            if 'writeCmd' in definition:
                writeCmd = definition['writeCmd']
        # build internal structure ---
        if 'writeCmd' not in definition:
            self.__device.attributes[attrName] =\
                AttributeObj(name=attrName, type=definition['type'],
                             dim=definition['dim'][0], readCmd=readCmd)
        else:
            if 'rampeable' not in definition:
                self.__device.attributes[attrName] =\
                    WAttributeObj(name=attrName, type=definition['type'],
                                  dim=definition['dim'][0],
                                  readCmd=readCmd, writeCmd=writeCmd)
                self.configureRamping(attrName, definition,
                                      readmethod, writemethod)
            else:
                self.__device.attributes[attrName] =\
                    WAttributeObj(name=attrName, type=definition['type'],
                                  dim=definition['dim'][0],
                                  readCmd=readCmd, writeCmd=writeCmd,
                                  rampeable=True)
            if 'writeValues' in definition:
                self.__device.attributes[attrName].\
                    setWriteValues(definition['writeValues'])
                # this is a very important information to have
                # in the attr descrition
                if 'description' in definition:
                    prefix = definition['description']+". "
                else:
                    prefix = ""
                descr = "%sAllowed values: %s"\
                        % (prefix, repr(definition['writeValues']))
                aprop.set_description(descr)
                attr.set_default_properties(aprop)
        return attr

    def configureRamping(self, attrName, definition, readmethod, writemethod):
        db = PyTango.Database()
        step = PyTango.Attr(attrName+"Step", definition['type'],
                            PyTango.READ_WRITE)
        step.set_memorized()
        step.set_memorized_init(True)
        self.__device.add_attribute(step, r_meth=readmethod,
                                    w_meth=writemethod)
        self._attributeList.append(attrName+"Step")
        try:
            devName = self.__device.get_name()
            stepAttrName = attrName+"Step"
            attrProp = db.get_device_attribute_property(devName,
                                                        stepAttrName)
            propertyValueStr = attrProp[stepAttrName]['__value'][0]
            value = float(propertyValueStr)
            self.__device.attributes[attrName].rampStep = value
        except:
            self.__device.attributes[attrName].rampStep = None
        stepspeed = PyTango.Attr(attrName+"StepSpeed",
                                 PyTango.CmdArgType.DevDouble,
                                 PyTango.READ_WRITE)
        stepspeed.set_memorized()
        stepspeed.set_memorized_init(True)
        self.__device.add_attribute(stepspeed, r_meth=readmethod,
                                    w_meth=writemethod)
        self._attributeList.append(attrName+"StepSpeed")
        try:
            devName = self.__device.get_name()
            stepSpeedAttrName = attrName+"StepSpeed"
            attrProp = db.get_device_attribute_property(devName,
                                                        stepSpeedAttrName)
            propertyValueStr = attrProp[attrName+"StepSpeed"]['__value'][0]
            value = float(propertyValueStr)
            self.__device.attributes[attrName].rampStepSpeed = value
        except:
            self.__device.attributes[attrName].rampStepSpeed = None
        self.__device.attributes[attrName].rampThread = None

    # remove dynamic attributes
    def remove_attribute(self, attrName):
        if self.__device:
            if attrName in self._attributeList:
                try:
                    self.__device.remove_attribute(attrName)
                except Exception as e:
                    self.__device.error_stream("In remove_attribute(%s) "
                                               "Exception: %s"
                                               % (attrName, e.desc))
                else:
                    attrIdx = self._attributeList.index(attrName)
                    self._attributeList.pop(attrIdx)
                    # self.__device.debug_stream("In remove_attribute(%s): "
                    #                            "done" %(attrName))
            else:
                self.__device.warn_stream("In remove_attribute(%s): it "
                                          "wasn't in the list" % (attrName))
        else:
            print "!"*20
            print attrName

    def remove_alldynAttrs(self):
        while len(self._attributeList) > 0:
            self.remove_attribute(self._attributeList[0])
    #      remember to clean the self.__device.attributes
    #      and the self._attributeList
