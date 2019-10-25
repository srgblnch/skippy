# -*- coding: utf-8 -*-
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
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from .abstracts import AbstractSkippyObj
from .builder import Builder
from .communications import CommunicatorBuilder
from .dataformat import interpret_binary_format
from .identify import identifier
import numpy
from .monitor import Monitor
from PyTango import AttrQuality, CmdArgType, DevFailed, DevState
from .statemanager import StateManager
import struct
from time import sleep, time
import traceback
from .version import version
from .watchdog import WatchDog

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"

MINIMUM_TIMESTAMPS_THRESHOLD = 0.1
MINIMUM_QUERY_WINDOW = 1


class Skippy(AbstractSkippyObj):
    """
    This is the main object of this python module.
    """

    # internal important objects
    _statemachine = None
    _communications = None
    _identificator = None
    _idn = None
    _monitor = None
    _watchdog = None

    _timestampsThreshold = MINIMUM_TIMESTAMPS_THRESHOLD
    _queryWindow = MINIMUM_QUERY_WINDOW
    _read_after_write = False

    _attributes = {}
    _attributesFlags = {}
    _attrs2Monitor = None

    _instructions_file = None
    _avoid_IDN = None

    def __init__(self,
                 # communications parameters
                 terminator=None, port=None, baudrate=None,
                 bytesize=None, parity=None, stopbits=None, timeout=None,
                 xonxoff=None,
                 # startup flags
                 autoStandby=True, autoOn=True, autoStart=True,
                 nChannels=None, nFunctions=None, nMultiple=None,
                 # monitoring parameters
                 attrs2Monitor=None, instructions_file=None, avoid_IDN=False,
                 *args, **kwargs):
        """
        Object construction requires access parametrization to the instrument
        Like for a networked instruments will be:
        >>> skippy = Skippy(name='localhost', port=5025)
        """
        super(Skippy, self).__init__(*args, **kwargs)
        self._statemachine = StateManager(name="StateManager", parent=self)
        self._statemachine.setStateAndStatus(DevState.INIT, "Initializing...")
        # prepare communications:
        self._terminator = terminator
        self._port = port
        if timeout == -1:
            timeout = None
        self._serial = {'baudrate': baudrate, 'bytesize': bytesize,
                        'parity': parity, 'stopbits': stopbits,
                        'timeout': timeout, 'xonxoff': xonxoff}
        if isinstance(instructions_file, str) and \
                len(instructions_file) > 0:
            self._instructions_file = instructions_file
        self._avoid_IDN = avoid_IDN
        if not self._buildCommunications():
            raise Exception("Constructor cannot prepare the communications")
        self._autoStandby = autoStandby
        self._autoOn = autoOn
        self._autoStart = autoStart
        self._attrs2Monitor = attrs2Monitor
        self._nChannels = nChannels
        self._nFunctions = nFunctions
        self._nMultiple = nMultiple
        if not self._autoStandby:
            self.debug_stream("AutoStandby False, stop construction here")
            return
        if not self.Standby():
            self.warn_stream("Failed to go to the Standby state")
            return
        if not self._autoOn:
            self.debug_stream("AutoOn False, stop construction here")
            return
        if not self.On():
            self.warn_stream("Failed to go to the On state")
            return
        if not self._autoStart:
            self.debug_stream("AutoStart False, stop construction here")
            return
        if self._attrs2Monitor is None or len(self._attrs2Monitor) == 0:
            self.info_stream("No Start() when no attributes to monitor")
        elif not self.Start():
            self.warn_stream("Failed to go to the Running state")
            return
        if self._avoid_IDN:
            self.info_stream("Watchdog inhibited when there is no way to "
                             "identify the instrument")
        else:
            self._watchdog = WatchDog(name="WatchDog", parent=self)
            self._watchdog.start()

    @property
    def version(self):
        return version()

    @property
    def statemachineObj(self):
        return self._statemachine

    @property
    def communicationsObj(self):
        return self._communications

    @property
    def identificatorObj(self):
        return self._identificator

    @property
    def idn(self):
        return self._idn

    @property
    def monitorObj(self):
        return self._monitor

    @property
    def watchdogObj(self):
        return self._watchdog

    @property
    def attributes(self):
        return self._attributes

    # TODO: this object should work like a dictionary to access those
    #       attribute objects.

    @property
    def attributesFlags(self):
        return self._attributesFlags

    @property
    def timestampsThreshold(self):
        return self._timestampsThreshold

    @timestampsThreshold.setter
    def timestampsThreshold(self, value):
        try:
            value = float(value)
            if value >= MINIMUM_TIMESTAMPS_THRESHOLD:
                self._timestampsThreshold = value
                if self._monitor is not None:
                    self._monitor.changeGenericPeriod(value)
            else:
                self.warn_stream("Try to set TimestampsThreshold below "
                                 "the minimum")
        except Exception as e:
            self.error_stream("Impossible to set %r as TimestampsThreshold: %s"
                              % (value, e))

    @property
    def queryWindow(self):
        return self._queryWindow

    @queryWindow.setter
    def queryWindow(self, value):
        try:
            value = int(value)
            if value >= MINIMUM_QUERY_WINDOW:
                self._queryWindow = value
            else:
                self.warn_stream("Try to set QueryWindow below the minimum")
        except Exception as e:
            self.error_stream("Impossible to set %r as QueryWindow: %s"
                              % (value, e))

    @property
    def read_after_write(self):
        if self._communications:
            return self._communications.read_after_write

    @read_after_write.setter
    def read_after_write(self, value):
        self._read_after_write = value
        if self._communications:
            self._communications.read_after_write = value

    @property
    def nChannels(self):
        return self._nChannels

    @property
    def nFunctions(self):
        return self._nFunctions

    @property
    def nMultiple(self):
        return self._nMultiple

    def _buildCommunications(self, updateState=True):
        try:
            kwargs = {'instrumentName': self.name,
                      'parent': self,
                      'port': self._port, 'serial_args': self._serial,
                      'terminator': self._terminator}
            builder = CommunicatorBuilder(**kwargs)
            self._communications = builder.build()
            if self._read_after_write != self._communications.read_after_write:
                self._communications.read_after_write = self._read_after_write
        except SyntaxError as exception:
            self.error_stream("Error in the instrument name: {0}"
                              "".format(exception))
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="{0}: review the 'instrument' "
                                              "property".format(exception))
            return False
        except Exception as exception:
            self.error_stream("Generic exception: %s" % (exception))
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="initialisation exception: {0}"
                                              "".format(exception))
            traceback.print_exc()
            return False
        if updateState:
            self._change_state_status(newState=DevState.OFF)
        return True

    def connect(self, tries=4):
        if self._communications is None:
            self._buildCommunications()
        try:
            self._communications.connect()
            self._idn = ''
            if self._avoid_IDN:
                self.info_stream("Inhibited to identify the instrument")
                return True
            for i in range(1, tries+1):
                self._idn = self._communications.ask(
                    "*IDN?", waittimefactor=i)
                if isinstance(self._idn, str) and len(self._idn) > 0:
                    break
                # if self._reconnectAwaker.isSet():
                #     self.info_stream("Abort reconnection to the instrument")
                #     return False
                self.warn_stream("In connect() -no answer to the"
                                 " identification request (try {0})".format(i))
                sleep(self._communications.timeBetweenSendAndReceive*10)
            if isinstance(self._idn, str) and len(self._idn) == 0:
                self.error_stream("In connect() Cannot identify"
                                  " the instrument after {0} tries".format(i))
                return False
            self.info_stream("In connect() instrument "
                             "identification: {0!r}".format(self._idn))
            return True
        except Exception as e:
            msg = "Cannot connect to the instrument."
            self.error_stream("In connect() {0} due to: {1}".format(msg, e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine=msg)
            return False

    def disconnect(self):
        try:
            self.debug_stream("Disconnect communications")
            self._communications.disconnect()
            if self._communications.isConnected():
                return False
            return True
        except Exception as e:
            msg = "Exception disconnecting to the instrument."
            self.error_stream("In disconnect() %s due to: %s"
                              % (msg, e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine=msg)
            self._communications = None
            return False

    def build(self):
        # TODO: check it is already build
        try:
            if self._avoid_IDN is True:
                self.info_stream("Build without the information of IDN")
                self._identificator = Builder(name="Builder", parent=self)
            elif hasattr(self, '_idn') and self._idn not in [None, ""]:
                self.info_stream("Build based on the instrument identification")
                self._identificator = identifier(self._idn, self)
            else:
                raise Exception("*IDN? not available (but not inhibited)")
            if self._instructions_file is not None:
                self.info_stream("Build based on an specified file")
                self._identificator.parseFile(self._instructions_file)
        except Exception as _exception:
            if hasattr(self, '_idn'):
                msg = "identification error: {0} (*IDN?:{1!r})" \
                      "".format(_exception, self._idn)
            else:
                msg = "identification error: {0}".format(_exception)
            self.error_stream("{0} {1}".format(self.name, msg))
            self._change_state_status(newState=DevState.UNKNOWN,
                                      newLine=msg)
            return False
        else:
            return True

    def unbuild(self):
        # TODO: clean the attributes internal objects
        try:
            self._identificator.remove_alldynAttrs()
            return True
        except Exception as e:
            self.error_stream("Exception removing dynattributes: %s" % (e))
            return False

    def inject_extra_attributes(self, definitionString):
        """
        In a similar way than the attributes defined on the files that describe
        an instrument after an identification, this method can apply the same
        syntax to insert specific definitions on a given skippy object.
        :param definitionString: similar to a PyTango.DevVarStringArray to
        interpret it as Attribute(...) definition in a multi-line.
        :return:
        """
        if isinstance(definitionString, str) and len(definitionString) > 0:
            self.debug_stream(
                "definitionString: {0!r}".format(definitionString))
            try:
                if self._identificator is None:
                    self._identificator = Builder(name="Builder", parent=self)
                self._identificator.parse(definitionString)
                return True
            except Exception as exc:
                self.error_stream("Parser failed: {0}".format(exc))
                return False
        return False

    def Standby(self):
        """
            Two possible transition to Standby: from Off or from On
        """
        state = self._get_state()
        self.debug_stream("Standby() called from %s" % (state))
        if state == DevState.OFF:
            if self.connect():
                self._change_state_status(newState=DevState.STANDBY)
                return True
        elif state == DevState.ON:
            if self._identificator is None or self.__unbuilder():
                self._change_state_status(newState=DevState.STANDBY)
                return True
        return False

    def Off(self):
        state = self._get_state()
        self.debug_stream("Off() called from %s" % (state))
        if state == DevState.RUNNING:
            if self.Stop():
                self.Standby()
        elif state == DevState.ON:
            self.Standby()
        try:
            self._communications.close()
        except Exception as e:
            self.error_stream("Cannot disconnect from the instrument "
                              "due to: %s" % (e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="Off command failed")
            return False
        else:
            self._idn = ""
            self.info_stream("disconnected to the instrument %s"
                             % (self.Instrument))
            if self.unbuild():
                self._change_state_status(newState=DevState.OFF)
                return True
            return False

    def On(self):
        state = self._get_state()
        self.debug_stream("On() called from %s" % (state))
        if state == DevState.OFF:
            self.Standby()
        if self.build():
            self._monitor = Monitor(name="Monitor", parent=self,
                                    attrLst=self._attrs2Monitor)
            self._change_state_status(newState=DevState.ON)
            return True

    def Start(self):
        if self._monitor is None:
            self.warn_stream(
                "Monitor not yet build: ignored the Start() command")
            return False
        state = self._get_state()
        self.debug_stream("Start() called from %s" % (state))
        try:
            if state == DevState.ON:
                if len(self._attrs2Monitor) > 0:
                    self._monitor.Start()
                    return True
                else:
                    self.warn_stream("No attributes to be monitored")
            else:
                self.warn_stream("Try to start when not ready")
        except Exception as e:
            self.error_stream("In Start() Exception: %s" % (e))
        return False

    def Stop(self):
        state = self._get_state()
        self.debug_stream("Stop() called from %s" % (state))
        try:
            if state == DevState.RUNNING:
                self._monitor.Stop()
            return True
        except Exception as e:
            self.error_stream("In Stop() Exception: %s" % (e))
        return False

    @property
    def MonitoredAttributes(self):
        return self._attrs2Monitor

#     @MonitoredAttributes.setter
#     def MonitoredAttributes(self, value):
#         self._attrs2Monitor = value

    def monitorInsert(self, attrName, attrPeriod):
        if self._monitor is None:
            self.warn_stream("Monitor not yet build: ignored the append of "
                             "%s (%s)" % (attrName, attrPeriod))
            return
        if attrPeriod is None:
            attrPeriod = self.timestampsThreshold
        if attrPeriod == self.timestampsThreshold:
            monitoringType = 'Generic'
        else:
            monitoringType = attrPeriod
        ok = self._monitor.Insert(attrName, monitoringType)
        if self._get_state() == DevState.ON and self._autoStart:
            if not self._monitor.Start():
                return False
        return ok

    def monitorRemove(self, attrId):
        if self._monitor is None:
            self.warn_stream("Monitor not yet build: ignored the append of "
                             "id:%s" % (attrId))
            return False
        self.info_stream("In RemoveMonitoring(): Removing id:%s "
                         "attribute from monitoring" % (attrId))
        return self._monitor.Remove(attrId)

    def getMonitorPeriod(self, attrId):
        if self._monitor is None:
            self.warn_stream("Monitor not yet build: monitoring period "
                             "request ignored")
            return
        return self._monitor.getPeriod(attrId)

    def Read(self, query, ask_for_values=False):
        '''
            Given a string with a ';' separated list of scpi commands 'ask'
            to the instrument and return what the instrument responds.
        '''
        try:
            self.debug_stream("Asking: {0!r}".format(query))
            if ask_for_values:
                answer = self._communications.ask_for_values(query)
            else:
                answer = self._communications.ask(query)
            if len(answer) > 100:
                answer_repr = "{0!r}(...){1!r}".format(answer[:25],
                                                       answer[len(answer)-25:])
            else:
                answer_repr = "{0!r}".format(answer)
            self.debug_stream("Answer: {0}".format(answer_repr))
            if answer == '':
                # raise Exception("No answer from the instrument")
                self.error_stream("No answer from the instrument")
            return answer
        except MemoryError as e:
            self.error_stream("In Read() MemoryError exception: %s"
                              % (e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="Device memory error!")
            return None
        except Exception as e:
            self.error_stream("In Read() Exception: %r" % (e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="Fatal error and communications "
                                      "lost with the instrument!",
                                      important=True)
            return None

    def Write(self, cmd):
        '''
        '''
        try:
            self.debug_stream("Writing: %r" % (cmd))
            self._communications.write(cmd)
        except MemoryError as e:
            self.error_stream("In Write() MemoryError exception: %s"
                              % (e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="Device memory error!")
        except Exception as e:
            self.error_stream("In Write() Exception: %s" % (e))
            traceback.print_exc()
            self._change_state_status(newState=DevState.FAULT,
                                      newLine="Fatal error and communications "
                                      "lost with the instrument!",
                                      important=True)

    def fireEventsList(self, eventsAttrList):
        if self._parent is not None:
            self._parent.fireEventsList(eventsAttrList)

    def _readAttrProcedure(self, attrIdLst, fromMonitor=False):
        if self._get_state() in [DevState.FAULT, DevState.DISABLE,
                                 DevState.INIT]:
            self.debug_stream("Avoid read procedure in %s state"
                              % (self._get_state()))
            return
        try:
            scalarList, spectrumList, imageList = \
                self.__filterAttributes(attrIdLst, fromMonitor)
            if not len(scalarList) == 0:
                indexes, queries = self.__preHardwareRead(scalarList)
                answers = []
                for query in queries:
                    answer = self.Read(query)
                    answers.append(answer)
                msg = ""
                for answer in answers:
                    if answer is None:
                        self.error_stream("In _readAttrProcedure() "
                                          "Uou, we've got a null answer!")
                        self._change_state_status(newState=DevState.FAULT,
                                                  newLine="Communication "
                                                  "error to the instrument",
                                                  important=True)
                        return
                    elif len(answer) > 100:
                        msg = ''.join([msg, "%r(...)%r"
                                       % (answer[:25],
                                          answer[len(answer)-25:])])
                    else:
                        msg = ''.join([msg, "%r" % (answer)])
                self.debug_stream("In _readAttrProcedure() scalar answers:"
                                  " {ans!r}".format(ans=msg))
                self.__postHardwareScalarRead(indexes, answers)
            if not len(spectrumList) == 0:
                indexes, queries = self.__preHardwareRead(spectrumList, 1)
                answers = []
                for query in queries:
                    answer = self.Read(query)
                    if answer is not None:
                        answers.append(answer)
                self.debug_stream("In _readAttrProcedure() spectrum "
                                  "answers number: %s" % (len(answers)))
                self.__postHardwareSpectrumRead(indexes, answers)
            if not len(imageList) == 0:
                self.error_stream("Excluding 2 dimensional attributes")
        except DevFailed as e:
            self.error_stream("In _readAttrProcedure() Exception: %s" % (e))
            traceback.print_exc()
        except Exception as e:
            self.error_stream("In _readAttrProcedure() Exception: %s" % (e))

    def __filterAttributes(self, attr_id_lst, from_monitor):
        '''Avoid hardware readings of:
           - attributes that are internals to the device
           - attributes that reading is recent
           - attributes where its channel/function manager say closed
        '''
        try:
            t = time()
            delta_t = self._timestampsThreshold
            scalar = []
            spectrum = []
            image = []
            self.debug_stream(
                "__filterAttributes({0}, {1})".format(attr_id_lst,
                                                      from_monitor))
            for attr_index in attr_id_lst:
                attr_name = \
                    self._identificator.get_attribute_name_by_id(attr_index)
                # attr_obj = multiattr.get_attr_by_ind(attr_index)
                # attr_name = attr_obj.get_name()
                if attr_name not in self.attributes:
                    self.debug_stream(
                        "\texcluding {0!r}: is not a hw attr."
                        "".format(attr_name))
                    continue  # go to the next element in the loop
                if self.__is_attr_monitored(attr_index) and not from_monitor:
                    self.debug_stream(
                        "\texclude {0} because it is being monitored"
                        "".format(attr_name))
                    continue  # go to the next element in the loop
                if self.attributes[attr_name].hasSwitchAttribute():
                    switch_obj = self.attributes[attr_name].getSwitchAttrObj()
                    if switch_obj.rvalue is False:
                        self.debug_stream(
                            "\texclude {0} because switch off"
                            "".format(attr_name))
                        continue
                if not self.__is_timestamp_aging(self.attributes[attr_name]):
                    self.debug_stream(
                        "\texclude {0} because cache value is stil valid"
                        "".format(attr_name))
                    continue
                dimensions = self.attributes[attr_name].dim
                if dimensions == 0:
                    scalar.append(attr_name)
                elif dimensions == 1:
                    spectrum.append(attr_name)
                    # TODO: hardcoded attr_names!!!
                    for auxiliar_attr in ['WaveformDataFormat',
                                          'WaveformOrigin',
                                          'WaveformIncrement']:
                        if auxiliar_attr in self.attributes:
                            scalar.append(auxiliar_attr)
                elif dimensions == 2:
                    image.append(attr_name)
                else:
                    self.error_stream(
                        "\texclude {0} because too much dimensions"
                        "".format(attr_name))
            self.debug_stream(
                "In __filterAttributes():\n"
                "\tscalar list:\t{0};\n"
                "\tspectrum list:\t{1};\n"
                "\timage list:\t{2};".format(scalar, spectrum, image))
            # Remove repeated attributes
            for attr in scalar:
                while scalar.count(attr) > 1:
                    scalar.pop(scalar.index(attr))
            for attr in spectrum:
                while spectrum.count(attr) > 1:
                    spectrum.pop(spectrum.index(attr))
            for attr in image:
                while image.count(attr) > 1:
                    image.pop(image.index(attr))
            return scalar, spectrum, image
        except Exception as e:
            self.error_stream(
                "In __filterAttributes({0}) Exception: {1}"
                "".format(attr_id_lst, e))
            traceback.print_exc()
            return [], [], []
            # FIXME: does this return the same list object 3 times?
            #        could it return 3 Nones?

    def __is_attr_monitored(self, attr_index):
        if self._monitor is not None:
            is_running = self._get_state() == DevState.RUNNING
            if is_running and attr_index in self._monitor.monitoredIds:
                return True
        return False

    def __is_timestamp_aging(self, attr_obj):
        if attr_obj.timestamp is not None:
            return time() - attr_obj.timestamp >= self._timestampsThreshold
        return True

    def __preHardwareRead(self, attrList, window=None):
        '''Given a list of attributes to be read, prepare it.
           - Divide the attributes to be read in subsets of QueryWindow size.
           - Build the concatenations of queries per subset.
           Example: QueryWindow = 4
           Input: attrList = [a1,a2,a3,a4,a5,a6,a7,a8,a9,a10]
           Output: subsetsIndexes = [[a1,a2,a3,a4],
                                     [a5,a6,a7,a8],
                                     [a9,a10]]
                   subsetsQueries = ["cmd;cmd;cmd;cmd;",
                                     "cmd;cmd;cmd;cmd;",
                                     "cmd;cmd;"]
        '''
        try:
            if window is None:
                window = self._queryWindow
            subsetsIndexes = []
            subsetsQueries = []
            for i in range(0, len(attrList), window):
                subsetsIndexes.append(attrList[i:i+window])
                subsetsQueries.append("")
                for j in range(len(subsetsIndexes[len(subsetsIndexes)-1])):
                    attrName = subsetsIndexes[len(subsetsIndexes)-1][j]
                    attrCmd = self.attributes[attrName].readCmd
                    subsetsQueries[len(subsetsQueries)-1] = \
                        "%s%s;" % (subsetsQueries[len(subsetsQueries)-1],
                                   attrCmd)
            return subsetsIndexes, subsetsQueries
        except Exception as e:
            self.error_stream("In __preHardwareRead() Exception: %s" % (e))
            return None, None

    def __postHardwareScalarRead(self, indexes, answers):
        '''Given the answers organise them in the self.attributes dictionary.
           Example: QueryWindow = 4
           Input: indexes = [[a1,a2,a3,a4],
                             [a5,a6,a7,a8],
                             [a9,a10]]
                  answers = ["ans;ans;ans;ans;",
                             "ans;ans;ans;ans;",
                             "ans;ans;"]
        '''
        t = time()
        try:
            attrWithEvents = []
            for i, answer in enumerate(answers):
                if answer is not None:
                    for j, value in \
                            enumerate(answer.split('\n')[0].split(';')):
                        attrName = indexes[i][j]
                        attrStruct = self.attributes[attrName]
                        try:
                            # With formulas, they will be responsible to build
                            # the conversion.
                            if attrStruct.readFormula:
                                attrStruct.lastReadValue = value
                            # old way tries the transformation based on
                            # attribute type information.
                            elif self.__isScalarBoolean(attrName, value):
                                pass
                            elif self.__isScalarInteger(attrName, value):
                                pass
                            elif self.__isScalarFloat(attrName, value):
                                pass
                            elif self.__isScalarString(attrName, value):
                                pass
                            else:
                                self.warn_stream("In __postHardwareScalarRead"
                                                 "() Unrecognized data type "
                                                 "for %s" % (attrName))
                                attrStruct.lastReadValue = value
                        except Exception as e:
                            self.error_stream("In __postHardwareScalarRead() "
                                              "Exception of attribute %s: %s"
                                              % (attrName, e))
                            traceback.print_exc()
                            attrStruct.lastReadValue = None
                            attrStruct.quality = AttrQuality.ATTR_INVALID
                        finally:
                            attrStruct.timestamp = t
                            attrId = attrStruct.id
                            if self.__isRamping(attrName):
                                attrStruct.quality = AttrQuality.ATTR_CHANGING
                            elif attrStruct.quality != AttrQuality.ATTR_VALID:
                                attrStruct.quality = AttrQuality.ATTR_VALID
                            if self._monitor is not None and \
                                    attrId in self._monitor.monitoredIds:
                                attrWithEvents.\
                                    append([attrName,
                                            attrStruct.lastReadValue,
                                            attrStruct.quality
                                            ])
                else:
                    self.error_stream("In __postHardwareScalarRead() "
                                      "answer %s is None" % (i))
            self.fireEventsList(attrWithEvents)
        except Exception as e:
            self.error_stream("In __postHardwareScalarRead() Exception: %s"
                              % (e))

    def __isScalarBoolean(self, attrName, attrValue):
        if self.attributes[attrName].type in \
                [CmdArgType.DevBoolean]:
            try:
                if attrValue.lower() in ['true', 'false', 'on', 'off']:
                    value = True if attrValue.lower() in ['true', 'on'] \
                        else False
                else:
                    try:
                        value = bool(int(attrValue))
                    except ValueError as e:
                        self.warn_stream(
                            "Couldn't interpret {!r} as boolean".format(
                                attrValue))
                        raise e
                self.attributes[attrName].lastReadValue = value
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_VALID
            except:
                self.attributes[attrName].lastReadValue = None
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_INVALID
            return True
        else:
            return False

    def __isScalarInteger(self, attrName, attrValue):
        if self.attributes[attrName].type in [CmdArgType.DevUChar,
                                              CmdArgType.DevUShort,
                                              CmdArgType.DevShort,
                                              CmdArgType.DevULong,
                                              CmdArgType.DevLong,
                                              CmdArgType.DevULong64,
                                              CmdArgType.DevLong64]:
            try:
                self.debug_stream(
                    "{name} {ans}".format(name=attrName, ans=attrValue))
                if hasattr(attrValue, 'count') and \
                        attrValue.count('.') == 1:
                    self.attributes[attrName].lastReadValue = \
                        int(float(attrValue))
                else:
                    self.attributes[attrName].lastReadValue = int(attrValue)
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_VALID
            except:
                self.attributes[attrName].lastReadValue = None
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_INVALID
            return True
        else:
            return False

    def __isScalarFloat(self, attrName, attrValue):
        if self.attributes[attrName].type in [CmdArgType.DevFloat,
                                              CmdArgType.DevDouble]:
            try:
                if attrValue == '9.99999E+37':
                    # this is the instrument tag for non measurable
                    self.attributes[attrName].lastReadValue = float('NaN')
                    self.attributes[attrName].quality = \
                        AttrQuality.ATTR_WARNING
                else:
                    self.attributes[attrName].lastReadValue = float(attrValue)
                    self.attributes[attrName].quality = \
                        AttrQuality.ATTR_VALID
            except:
                self.attributes[attrName].lastReadValue = None
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_INVALID
            return True
        else:
            return False

    def __isScalarString(self, attrName, attrValue):
        if self.attributes[attrName].type in [CmdArgType.DevString]:
            try:
                self.attributes[attrName].lastReadValue = str(attrValue)
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_VALID
            except:
                self.attributes[attrName].lastReadValue = None
                self.attributes[attrName].quality = \
                    AttrQuality.ATTR_INVALID
            return True
        else:
            return False

    def __isRamping(self, attrName):
        isRamping = False
        try:
            if self.attributes[attrName].isRampeable():
                rampObj = self.attributes[attrName].getRampObj()
                if rampObj.isRamping():
                    isRamping = True
        except Exception as e:
            self.warn_stream("%s ramping question exception: %s"
                             % (attrName, e))
        return isRamping

    def __postHardwareSpectrumRead(self, indexes, answers):
        '''Given the answers organise them in the self.attributes dictionary.
           QueryWindow doesn't apply here, the spectrums are made in
           separated reads
           Input: indexes = [[s1],
                             [s2],
                             [a3]]
                  answers = ["f1,f2,f3,f4,...,fn",
                             "f1,f2,f3,f4,...,fn",,
                             "f1,f2,f3,f4,...,fn",]
           A waveform has always a first character '#'
           The second is a char with the number of elements in the next
           variable field. The third, represented with Rs, are the number of
           elements in the waveform that comes next.
           Example: answer = #532017... means, 5 elements will be in the second
                    field, and there will be 32017 elements in the third.
        '''
        t = time()
        try:
            attrWithEvents = []
            for i, answer in enumerate(answers):
                attrName = indexes[i][0]
                if len(answer) > 100:
                    answer_repr = "{0!r}(...){1!r}".format(
                        answer[:25], answer[len(answer)-25:])
                else:
                    answer_repr = "{0!r}".format(answer)
                self.debug_stream(
                    "__postHardwareSpectrumRead() for {0}: {1}".format(
                        attrName, answer_repr))
                attrStruct = self.attributes[attrName]

                # TODO: hardcoded attrNames!!!
                if 'WaveformDataFormat' in self.attributes:
                    dataFormatAttr = self.attributes['WaveformDataFormat']
                    dataFormat = dataFormatAttr.lastReadValue
                    if dataFormat.startswith('ASC'):
                        if attrStruct.hasRawData():
                            attrStruct.lastReadRaw = answer
                        if not attrStruct.hasArrayInterpreter():
                            attrStruct.lastReadValue = numpy.fromstring(
                                answer, dtype=float, sep=',')
                        else:
                            attrStruct.rvalue
                        attrStruct.timestamp = t
                        attrStruct.quality = AttrQuality.ATTR_VALID
                    else:
                        # process the header
                        if not answer[0] == '#':
                            self.error_stream(
                                "Wrong data receiver for the attribute %s"
                                % (attrName))
                            return
                        # save values for debugging
                        attrStruct.lastReadRaw = answer
                        # review the header, in answer[0] there is the '#' tag
                        headerSize = int(answer[1])
                        bodySize = int(answer[2:2+headerSize])
                        bodyBlock = answer[2+headerSize:
                                           2+headerSize+bodySize]
                        self.debug_stream(
                            "In __postHardwareSpectrumRead() waveform data: "
                            "header size %d bytes, wave size %d bytes (%d)"
                            % (2+headerSize, bodySize, len(bodyBlock)))
                        # prepare interpretation of the raw data
                        try:
                            format, divisor = interpret_binary_format(
                                dataFormat)
                        except AssertionError as exc:
                            self.error_stream(
                                "From attribute {0}: {1}".format(attrName,
                                                                 exc))
                            attrStruct.lastReadValue = []
                            attrStruct.timestamp = t
                            attrStruct.quality = AttrQuality.ATTR_INVALID
                            break
                        nIncompleteBytes = (len(bodyBlock) % divisor)
                        nCompletBytes = len(bodyBlock) - nIncompleteBytes
                        completBytes = bodyBlock[:nCompletBytes]
                        self.debug_stream(
                            "With %d bytes, found %d complete packs and %d "
                            "incomplete. (Expected %d single values)"
                            % (len(bodyBlock), nCompletBytes, nIncompleteBytes,
                               nCompletBytes/divisor))
                        # convert the received input to integers
                        try:
                            fmt = format*(nCompletBytes/divisor)
                            self.debug_stream(
                                "Preparing to unpack with  %r format "
                                "(len fmt %d, len bytes %d)"
                                % (format, len(fmt), len(completBytes)))
                            unpackInt = struct.unpack(fmt, completBytes)
                            # self.debug_stream("Unpacked: %s" % unpackInt)
                        except Exception as e:
                            self.error_stream(
                                "Data cannot be unpacked: %s" % (e))
                            traceback.print_exc()
                        else:
                            # expand the input when each float is codified in
                            # less than 4 bytes
                            if attrStruct.hasArrayInterpreter():
                                interpreter = attrStruct.arrayInterpreter
                                f = numpy.array(unpackInt, dtype=float)
                                o = float(interpreter.originAttr.rvalue)
                                i = float(interpreter.incrementAttr.rvalue)
                                attrStruct.lastReadValue = o+(i*f)
                                attrStruct.timestamp = t
                                attrStruct.quality = AttrQuality.ATTR_VALID
                else:
                    self.warn_stream(
                        "In __postHardwareSpectrumRead() Unrecognised "
                        "spectrum attribute, storing raw data")
                    attrStruct.lastReadValue = answer
                    attrStruct.timestamp = t
                    attrStruct.quality = AttrQuality.ATTR_VALID
                attrId = attrStruct.id
                if attrId in self._monitor.monitoredIds:
                    attrWithEvents.append(
                        [attrName, attrStruct.lastReadValue,
                         attrStruct.quality])
            self.fireEventsList(attrWithEvents)
        except Exception as e:
            self.error_stream("In __postHardwareSpectrumRead() Exception: %s"
                             % (e))
            traceback.print_exc()
