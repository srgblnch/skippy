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

from copy import copy
import functools
import os
import PyTango
import traceback
from threading import Thread
from time import sleep


def identifier(idn, deviceObj):
    '''This method has been designed to understand from the answer of an
       instrument to the '*IDN?' command, what is the correct object that
       contains the set of commands for this instrument.
    '''
    company, model = splitIDN(idn)
    file = {'agilent technologies': agilent,
            'tektronix': tektronix,
            'rohde&schwarz': rohdeschwarz,
            'arroyo': arroyo,
            'albasynchrotron': albasynchrotron,
            'keithley instruments inc.': keithley,
            'fakeinstruments. inc': fakeinstrument,
            }[company](model)
    builder = Builder(deviceObj)
    builder.parseFile(file)
    return builder


def splitIDN(idn):
    # Only company and model in use. Perhaps one day the firmware version
    # would be useful but not found the case by now.
    idn = idn.strip().lower()
    if idn.count(',') == 3:
        separator = ','
    elif idn.count(' ') == 3:
        separator = ' '
    else:
        raise SyntaxError("Could not identify the separator in %r" % (idn))
    try:
        company, model, rest = idn.split(separator, 2)
        company = company.strip()
        model = model.strip()
        return company, model
    except Exception as e:
        raise SyntaxError("Could not identify the manufacturer and model "
                          "in %r" % (idn))


def _getFilePath(filename):
    path = os.path.dirname(__file__)
    full_path = os.path.join(path, filename)
    return full_path


#################################
# supported companies methods ---
def agilent(model):
    if model.startswith('dso'):
        return _getFilePath("instructions/scope/agilentDSO.py")
    elif model.startswith('n5171'):
        return _getFilePath("instructions/radioFrequencyGenerator/"
                            "keysightSignalGenerator.py")
    raise EnvironmentError("Agilent %s model not supported" % (model))


def tektronix(model):
    if model.startswith('dpo'):
        return _getFilePath("instructions/scope/tektronixDPO.py")
    elif model.upper().startswith('AFG'):
        return _getFilePath("instructions/arbitraryFunctionGenerator/"
                            "tektronicsAFG.py")
    raise EnvironmentError("Tektronix %s model not supported" % (model))


def rohdeschwarz(model):
    if model == 'sma100a':
        return _getFilePath("instructions/radioFrequencyGenerator/"
                            "rohdeSchwarzRFG.py")
    elif model.lower() == 'fsp-3':
        return _getFilePath("instructions/spectrumAnalyser/rohdeSchwarzFSP.py")
    raise EnvironmentError("Rohde&Schwarz %s model not supported" % (model))


def arroyo(model):
    if model == '5300':
        return _getFilePath("instructions/temperatureController/arroyo5300.py")
    raise EnvironmentError("Arroyo %s model not supported" % (model))


def albasynchrotron(model):
    if model == 'electrometer2':
        return _getFilePath('instructions/albaEm/albaEm.py')
    raise EnvironmentError("Alba Synchrotron %s model not supported" % (model))


def keithley(model):
    if model == 'model 2000':
        return _getFilePath("instructions/multimeter/keithley2000.py")
    elif model in ['model 2635a', 'model 2611']:
        return _getFilePath("instructions/sourcemeter/keithley26XX.py")
    raise EnvironmentError("Keithley %s model not supported" % (model))


def fakeinstrument(model):
    if model == 'tester':
        return _getFilePath("instructions/fakeinstruments/tester.py")
    raise EnvironmentError("Fake Instrument %s model not supported" % (model))
# done supported companies methods
##################################


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

class AttributeFunctionality(object):
    def __init__(self, name, owner, *args, **kwargs):
        super(AttributeFunctionality, self).__init__(*args, **kwargs)
        if name is None:
            raise AssertionError("Functionality must have a name")
        if owner is None:
            raise AssertionError("Functionality must have an owner")
        if not isinstance(owner, AttributeObj):
            raise AssertionError("Functionality owner must be an attribute "
                                 "object")
        self._name = name
        self._owner = owner

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "%s (%s)" % (self.name, self.__class__.__name__)

    def debug_stream(self, msg):
        self._owner.debug_stream("[%s] %s" % (self.name,msg))

    def info_stream(self, msg):
        self._owner.info_stream("[%s] %s" % (self.name,msg))

    def warn_stream(self, msg):
        self._owner.warn_stream("[%s] %s" % (self.name,msg))

    def error_stream(self, msg):
        self._owner.error_stream("[%s] %s" % (self.name,msg))

    def _buildrepr_(self, attributes):
        repr = "%s:\n" % self
        for key in attributes:
            attr = getattr(self, key)
            if attr is None:
                repr += "\t%s: None\n" % (key)
            elif isinstance(attr, list) and len(attr) == 0:
                repr += "\t%s: []\n" % (key)
            elif isinstance(attr, str):
                repr += "\t%s: %r\n" % (key, attr)
            elif hasattr(attr, '__call__'):
                args = [0]*attr.__code__.co_argcount
                repr += "\t%s: %r\n" % (key, attr(*args))
            else:
                repr += "\t%s: %s\n" % (key, attr)
        return repr


class RampObj(AttributeFunctionality):
    def __init__(self, *args, **kwargs):
        super(RampObj, self).__init__(*args, **kwargs)
        self._rampStep = None
        self._rampStepSpeep = None
        self._rampThread = None
    # FIXME: this is only a ramping for float attributes, should also support
    #        integers.
    # FIXME: prevent from attributes with a set of write values to have a ramp.

    def __repr__(self):
        return self._buildrepr_(['rampStep', 'rampStepSpeep'])

    @property
    def rampStep(self):
        return self._rampStep

    @rampStep.setter
    def rampStep(self, value):
        if value is not None:
            self._rampStep = float(value)

    @property
    def rampStepSpeep(self):
        return self._rampStepSpeep

    @rampStepSpeep.setter
    def rampStepSpeep(self, value):
        if value is not None:
            self._rampStepSpeep = float(value)

    @property
    def rampThread(self):
        return self._rampThread

#     @rampThread.setter
#     def rampThread(self, value):
#         self._rampThread = value

    def isRamping(self):
        if self.rampThread is not None and self.rampThread.isAlive():
            return True
        return False

    def prepareRamping(self):
        try:
            thread = Thread(target=self._rampProcedure,
                            name="%s_ramp" % (self._owner.name))
            thread.setDaemon(True)
        except Exception as e:
            self.error_stream("Prepare ramp exception: %s" % (e))
            return False
        else:
            self._rampThread = thread
            return True

    def launchRamp(self):
        try:
            self._rampThread.start()
        except:
            return False
        else:
            return True

    def _rampProcedure(self):
        '''Important things of the ramp procedure:
           - before do the evaluation of the next step is always doing a new
             read of the destination value. If the user has changed the
             destination value, the ramp will continue to the newer place.
           - the step and the time on each step will also be using the latest.
             If the user changes the ramp during one, the newer configuration
             will be used from then on.
           - The last step can be smaller than configured if (and ony if) the
             distance is smaller than the step.
           - The state of the device will be preserved after the ramp, but
             modified to MOVING while is working the ramp.
             # FIXME: run condition if there are two ramps and the second
             ends later. The first will restore the state, when the second is
             working and when this seconds finish will restore a moving state!
           TODO: future improvements for ramps:
           - Current ramp is like an step scan. There are other ramps possible:
             - On each step move a percentage of the distance (like move 2/3th
               until close enough).
             - Acceleration - motion - deceleration.
        '''
        # prepare
        backup_state = self.get_state()
        self.change_state_status(newState=PyTango.DevState.MOVING,
                                 rebuild=True)
        orig_pos = self._owner.rvalue
        dest_pos = self._owner.wvalue
        self.info_stream("In _rampProcedure(): ramp will start from %g to %g"
                         % (orig_pos, dest_pos))
        while not orig_pos == dest_pos:
            diff = abs(orig_pos - dest_pos)
            if diff < self.rampStep:
                new_pos = dest_pos  # Last step
            # else, do one step in the correct direction
            elif orig_pos > dest_pos:
                new_pos = orig_pos - self.rampStep
            elif orig_pos < dest_pos:
                new_pos = orig_pos + self.rampStep
            attrWriteCmd = self._owner.writeCmd(new_pos)
            self.info_stream("In _rampProcedure() step from %f to %f sending: "
                             "%s" % (orig_pos, dest_pos, attrWriteCmd))
            self.doHardwareWrite(attrWriteCmd)
            sleep(self.rampStepSpeed)
            # get newer values
            orig_pos = self._owner.rvalue
            dest_pos = self._owner.wvalue
        self.info_stream("In _rampProcedure(): finished the movement at %f"
                         % (dest_pos))
        # close
        self.change_state_status(newState=backup_state, rebuild=True)
        self._rampThread = None

    def get_state(self):
        return self._owner.get_state()

    def change_state_status(self, *args, **kwargs):
        self._owner.change_state_status(*args, **kwargs)

    def doHardwareWrite(self, cmd):
        self._owner.doHardwareWrite(cmd)


class RawDataObj(AttributeFunctionality):
    def __init__(self, *args, **kwargs):
        super(RawDataObj, self).__init__(*args, **kwargs)
        self._lastReadRaw = None

    def __repr__(self):
        return self._buildrepr_(['rawData'])

    @property
    def lastReadRaw(self):
        return self._lastReadRaw

    @lastReadRaw.setter
    def lastReadRaw(self, value):
        self._lastReadRaw = value


###############################
# Attribute Objects ---
class AttributeObj(object):
    def __init__(self, name, type, dim, parent=None, *args, **kwargs):
        super(AttributeObj, self).__init__()  # *args, **kwargs)
        self._name = name
        self._type = type
        self._dim = dim
        self._parent = parent

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def dim(self):
        return self._dim

    def debug_stream(self, msg):
        msg = "[%s] %s" % (self.name, msg)
        if self._parent is not None:
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: %s" % (msg))

    def info_stream(self, msg):
        if self._parent is not None:
            self._parent.info_stream(msg)
        else:
            print("INFO:  %s" % (msg))

    def warn_stream(self, msg):
        if self._parent is not None:
            self._parent.warn_stream(msg)
        else:
            print("WARN:  %s" % (msg))

    def error_stream(self, msg):
        if self._parent is not None:
            self._parent.error_stream(msg)
        else:
            print("ERROR: %s" % (msg))

    def get_state(self):
        if self._parent is not None and\
                hasattr(self._parent, 'get_state'):
            return self._parent.get_state()

    def change_state_status(self, *args, **kwargs):
        if self._parent is not None and\
                hasattr(self._parent, 'change_state_status'):
            self._parent.change_state_status(*args, **kwargs)

    def _buildrepr_(self, attributes):
        repr = "%s (%s):\n" % (self.name, self.__class__.__name__)
        for key in attributes:
            if hasattr(self, key):
                attr = getattr(self, key)
                if attr is None:
                    repr += "\t%s: None\n" % (key)
                elif isinstance(attr, list) and len(attr) == 0:
                    repr += "\t%s: []\n" % (key)
                elif isinstance(attr, str):
                    repr += "\t%s: %r\n" % (key, attr)
                elif hasattr(attr, '__call__'):
                    args = [0]*attr.__code__.co_argcount
                    repr += "\t%s: %r\n" % (key, attr(*args))
                else:
                    repr += "\t%s: %s\n" % (key, attr)
            else:
                self.debug_stream("In _buildrepr_() doesn't have %s" % (key))
        return repr


class ROAttributeObj(AttributeObj):
    def __init__(self, readCmd, readFormula=None,
                 withRawData=False, *args, **kwargs):
        super(ROAttributeObj, self).__init__(*args, **kwargs)
        self._readCmd = readCmd
        self._readFormula = readFormula
        self._lastReadValue = None
        self._timestamp = None
        self._quality = PyTango.AttrQuality.ATTR_INVALID
        if withRawData:
            self._raw = RawDataObj("rawdata", self)
        else:
            self._raw = None

    def __str__(self):
        return "%s (%s) [%s, %s, %s]" % (self.name, self.__class__.__name__,
                                         self.rvalue, self.timestamp,
                                         self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'timestamp', 'quality', 'dim',
                                 'readCmd', 'readFormula'])

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

    def doHardwareRead(self, query):
        if self._parent is not None and hasattr(self._parent,
                                                'doHardwareRead'):
            return self._parent.doHardwareRead(query)

    @property
    def readFormula(self):
        return self._readFormula

    @property
    def rvalue(self):
        newReadValue = self.doHardwareRead(self.readCmd)
        if self._readFormula:
            self.debug_stream("Evaluating %r with VALUE=%r"
                              % (self._readFormula, newReadValue))
            try:
                formula = self._readFormula.replace("VALUE", "%r"
                                                    % newReadValue)
                self.debug_stream("eval(%r)" % (formula))
                return eval(formula)
            except Exception as e:
                self.warn_stream("Exception evaluating formula: %s" % (e))
        else:
            try:
                if self.type in [PyTango.DevDouble, PyTango.DevFloat]:
                    self._lastReadValue = float(newReadValue)
                elif self.type in [PyTango.DevShort, PyTango.DevUShort,
                                   PyTango.DevInt, PyTango.DevLong,
                                   PyTango.DevULong, PyTango.DevLong64,
                                   PyTango.DevULong64]:
                    self._lastReadValue = int(newReadValue)
                elif self.type in [PyTango.DevBoolean]:
                    self._lastReadValue = bool(newReadValue)
            except Exception as e:
                self.error_stream("Exception converting string to type %s"
                                  % (self.type))
                return None
        return self._lastReadValue

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


class RWAttributeObj(ROAttributeObj):
    # FIXME: this class is getting dirty due to the ramp: too many specific
    #        methods when the ramp should be encapsulated apart.
    def __init__(self, writeCmd=None, writeFormula=None, rampeable=False,
                 writeValues=None, *args, **kwargs):
        super(RWAttributeObj, self).__init__(*args, **kwargs)
        self._writeCmd = writeCmd
        self._writeFormula = writeFormula
        self._lastWriteValue = None
        self._ramp = None
        if rampeable:
            self.makeRampeable()
        self._writeValues = writeValues

    def __str__(self):
        return "%s (%s) [(%s, %s), %s, %s]" % (self.name,
                                               self.__class__.__name__,
                                               self.rvalue, self.wvalue,
                                               self.timestamp, self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'wvalue', 'timestamp', 'quality',
                                 'dim', 'readCmd', 'readFormula', 'writeCmd',
                                 # 'writeFormula'
                                 ])

    def isWritable(self):
        return True

    def hasWriteValues(self):
        return self._writeValues is not None

    @property
    def writeCmd(self):
        return self._writeCmd

    def doHardwareWrite(self, cmd):
        if self._parent is not None and\
                hasattr(self._parent, 'doHardwareWrite'):
            self._parent.doHardwareWrite(cmd)

    @property
    def writeFormula(self):
        return self._writeFormula

    @property
    def wvalue(self):
        return self._lastWriteValue

    @property
    def lastWriteValue(self):
        return self._lastWriteValue

    @lastWriteValue.setter
    def lastWriteValue(self, value):
        self._lastWriteValue = value

    def isRampeable(self):
        if self._ramp is None:
            return False
        return True

    def makeRampeable(self):
        if self._ramp is None:
            self._ramp = RampObj("ramp", self)

    def getRampObj(self):
        return self._ramp

    @property
    def writeValues(self):
        return self._writeValues

    def setWriteValues(self, writeValues):
        self._writeValues = writeValues


class Builder:
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
        self.__device.info_stream("Start parsing the attribute file: %s"
                                  % (fName))
        try:
            execfile(str(fName), self.globals_, self.locals_)
        except Exception as e:
            self.__device.debug_stream("Builder.parseFile Exception: "
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
            - readFormula: evaluable string to be applied to the answer from
                           the instrument to modify it to become the device
                           answer to the attribute.
            TODO writeFormula: evaluable string to be applied to the value set
                            to an attribute before format the string to be
                            send to the instrument.
        '''
        # preconditions
        if not type(attributeDefinition) == dict:
            raise AttributeError("Invalid definition of the attribute %s"
                                 % (attributeName))
        for k in ['type', 'dim', 'readCmd']:
            if k not in attributeDefinition:
                msg = "In %s Invalid definition, key %s is mandatory"\
                    % (attributeName, k)
                self.__device.error_stream(msg)
                raise KeyError(msg)

        # If the attribute definition includes channels and functions,
        # do it in loop
        if 'channels' in attributeDefinition or \
                'functions' in attributeDefinition or \
                'multiple' in attributeDefinition:
            self.__prepareChannelLikeGroup(attributeName, attributeDefinition)
        # when is a single attribute, no loop required
        else:
            try:
                attr = self.__getAttrObj(attributeName, attributeDefinition)
                self.__device.debug_stream("Added: %r" % (attr))
            except Exception as e:
                self.__device.error_stream("NOT added attribute: %s "
                                           "due to exception: %s"
                                           % (attributeName, e))
                traceback.print_exc()

    def __prepareChannelLikeGroup(self, attributeName, attributeDefinition):
        if 'channels' in attributeDefinition and \
                attributeDefinition['channels']:
            if self.__device.NumChannels <= 0:
                raise ValueError("Could not prepare channels for %s because "
                                 "not well defined the device property about"
                                 "how many have to be created"
                                 % (attributeName))
            self.__buildGroup(attributeName, attributeDefinition,
                              self.__device.NumChannels, "Ch")
        if 'functions' in attributeDefinition and \
                attributeDefinition['functions']:
            if self.__device.NumFunctions <= 0:
                raise ValueError("Could not prepare functions for %s because "
                                 "not well defined the device property about"
                                 "how many have to be created"
                                 % (attributeName))
            self.__buildGroup(attributeName, attributeDefinition,
                              self.__device.NumFunctions, "Fn")
        if 'multiple' in attributeDefinition and \
                attributeDefinition['multiple']:
            try:
                scpiPrefix = attributeDefinition['multiple']['scpiPrefix']
                attrSuffix = attributeDefinition['multiple']['attrSuffix']
                number = self.__checkNumberOfMultiple(attributeName,
                                                      scpiPrefix)
                self.__buildGroup(attributeName, attributeDefinition, number,
                                  attrSuffix)
            except Exception as e:
                self.__device.error_stream("NOT added attribute: %s "
                                           "due to exception: %s"
                                           % (attributeName, e))
                # traceback.print_exc()

    def __checkNumberOfMultiple(self, attributeName, scpiPrefix):
        scpiPrefix = scpiPrefix.lower()
        number = None
        e = "Could not prepare 'Multiple' attributes for %s " % (attributeName)
        if len(self.__device.NumMultiple) > 0:
            for element in self.__device.NumMultiple:
                element = element.lower()
                if element.startswith("%s:" % scpiPrefix):
                    try:
                        _, number = element.split('%s:' % (scpiPrefix))
                        number = int(number)
                        break
                    except:
                        number = -1
                        break
            if number == -1:
                e += "because element %r of NumMultiple property "\
                    "couldn't be interpreted correctly." % (element)
            elif number is None:
                e += "because no description in NumMultiple property "\
                    "has %s." % (scpiPrefix)
            else:
                return number
        else:
            e += "because not well defined the device property about "\
                "how many have to be created."
        raise ValueError(e)

    def __buildGroup(self, name, definition, number, attrSuffix):
        attrName = "%s%s" % (name, attrSuffix)
        for i in range(1, number+1):
            defcopy = copy(definition)
            if attrSuffix in ['Ch', 'Fn']:
                if attrSuffix == 'Ch':
                    ch, fn, multiple = i, None, None
                if attrSuffix == 'Fn':
                    ch, fn, multiple = None, i, None
            else:
                ch, fn, multiple = None, None, i
            try:
                attr = self.__getAttrObj("%s%d" % (attrName, i),
                                         defcopy, channel=ch, function=fn,
                                         multiple=multiple)
                self.__device.debug_stream("Added attribute: %s"
                                           % (attr.get_name()))
            except Exception as e:
                self.__device.error_stream("NOT added attribute: "
                                           "%s%d due to exception: "
                                           "%s" % (attrName,
                                                   i, e))
                traceback.print_exc()

    def __getAttrObj(self, attrName, definition, channel=None, function=None,
                     multiple=None):
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
            raise AttributeError("Not supported multiple dimensions")
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
            attr.set_memorized()
            attr.set_memorized_init(True)
        attr.set_default_properties(aprop)
        self.__device.add_attribute(attr, r_meth=readmethod,
                                    w_meth=writemethod)
        self._attributeList.append(attrName)
        # prepare internal structure ---
        if channel or function or multiple:
            if channel:
                like = "channel"
            elif function:
                like = "function"
            elif multiple and 'scpiPrefix' in definition['multiple'] and\
                    'attrSuffix' in definition['multiple']:
                like = definition['multiple']['scpiPrefix']
            else:
                raise AttributeError("Wrong definition of multiple attribute")
            number = channel or function or multiple
            self.__prepareChannelLikeAttr(like, number, definition, attrName)
        else:
            readCmd = definition['readCmd']
            if 'writeCmd' not in definition:
                # writeCmd = definition['writeCmd']
                definition['writeCmd'] = None
        if 'readFormula' not in definition:
            # readFormula = definition['readFormula']
            definition['readFormula'] = None
        # if 'writeFormula' not in definition:
        #     # writeFormula = definition['writeFormula']
        #     writeFormula = None
        # build internal structure ---
        if definition['writeCmd'] is None:
            self.__buildROObj(attrName, definition)
        else:
            self.__buildRWObj(attrName, definition, readmethod, writemethod)
            if 'writeValues' in definition:
                self.__prepareWriteValues(attrName, definition, aprop, attr)
        return attr

    def __prepareChannelLikeAttr(self, like, number, definition, attrName):
        if like == 'channel':
            scpiPrefix = "CHAN"
            attrSuffix = "Ch"
        elif like == 'function':
            scpiPrefix = "FUNC"
            attrSuffix = "Fn"
        else:
            scpiPrefix = definition['multiple']['scpiPrefix']
            attrSuffix = definition['multiple']['attrSuffix']
        definition['readCmd'] = definition['readCmd'](scpiPrefix, number)
        if 'writeCmd' not in definition:
            definition['writeCmd'] = None
        else:
            definition['writeCmd'] = definition['writeCmd'](scpiPrefix, number)
        if 'manager' in definition and definition['manager'] is True:
            self.__device.attributesFlags["%s%d"
                                          % (attrSuffix, number)] = attrName

    def __buildROObj(self, attrName, definition):
        self.__device.attributes[attrName] =\
            ROAttributeObj(name=attrName, type=definition['type'],
                           dim=definition['dim'][0],
                           readCmd=definition['readCmd'],
                           readFormula=definition['readFormula'],
                           parent=self.__device)

    def __buildRWObj(self, attrName, definition, readmethod, writemethod):
        if 'rampeable' in definition:
            self.__device.attributes[attrName] =\
                RWAttributeObj(name=attrName, type=definition['type'],
                               dim=definition['dim'][0],
                               readCmd=definition['readCmd'],
                               writeCmd=definition['writeCmd'],
                               readFormula=definition['readFormula'],
                               # writeFormula=definition['writeFormula'],
                               rampeable=True,
                               parent=self.__device)
            self.configureRamping(attrName, definition,
                                  readmethod, writemethod)
        else:
            self.__device.attributes[attrName] =\
                RWAttributeObj(name=attrName, type=definition['type'],
                               dim=definition['dim'][0],
                               readCmd=definition['readCmd'],
                               writeCmd=definition['writeCmd'],
                               readFormula=definition['readFormula'],
                               # writeFormula=definition['writeFormula'],
                               parent=self.__device)

    def __prepareWriteValues(self, attrName, definition, aprop, attr):
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
            rampObj = self.__device.attributes[attrName].getRampObj()
            rampObj.rampStep = value
        except:
            rampObj = self.__device.attributes[attrName].getRampObj()
            rampObj.rampStep = None
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
            rampObj = self.__device.attributes[attrName].getRampObj()
            rampObj.rampStepSpeed = value
        except:
            rampObj = self.__device.attributes[attrName].getRampObj()
            rampObj.rampStepSpeed = None

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
