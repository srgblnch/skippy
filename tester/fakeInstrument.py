from __future__ import print_function
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

try:
    import argparse
except:
    argparse = None
from datetime import datetime
from instrAttrs import (ROinteger, RWinteger, ROfloat, RWfloat,
                        ROIntegerFallible, Format,
                        ROIntegerArray, ROFloatArray, Waveform,
                        ROboolean, RWboolean, ROBooleanArray, ROFloatChannel)
from instrIdn import InstrumentIdentification, __version__
import os
from psutil import process_iter, Process
import PyTango
import signal
import scpilib
from select import select
from subprocess import Popen, PIPE
import sys
from time import sleep
import traceback

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


DevServer = 'Skippy'
DevInstance = 'FakeInstrument'
DevClass = 'Skippy'
DevName = 'fake/skyppy/instrument-01'


class FakeInstrument(object):

    _identity = None
    _port = None
    _scpiObj = None
    _attrObjs = {}

    def __init__(self, port=5025, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._port = port
        self._build_fake_scpi()

    def _build_fake_scpi(self):
        version = "{0}scpilib{1}" \
                  "".format(__version__, scpilib.version.version())
        self._identity = InstrumentIdentification(
            'FakeInstruments. Inc', 'Tester', 0, version)
        self._scpiObj = scpilib.scpi(local=True, debug=True, port=self._port,
                                     log2File=True, loggerName="SkippyTester")
        self._build_special_commands()
        self._build_normal_commands()
        self.open()

    def __str__(self):
        return "{0}".format(self._scpiObj)

    def __repr__(self):
        return "{0!r}".format(self._scpiObj)

    def tree(self):
        return "{0!r}".format(self._scpiObj._commandTree)

    def open(self):
        self._scpiObj.open()

    def close(self):
        self._scpiObj.close()

    def _build_special_commands(self):
        self._scpiObj.addSpecialCommand('IDN', self._identity.idn)

    def _build_normal_commands(self):
        self._attrObjs['roboolean'] = self.__build_ROBoolean()
        self._attrObjs['rwboolean'] = self.__build_RWBoolean()
        self._attrObjs['rointeger'] = self.__build_ROInteger()
        self._attrObjs['rwinteger'] = self.__build_RWInteger()
        self._attrObjs['rofloat'] = self.__build_ROfloat()
        self._attrObjs['rwfloat'] = self.__build_RWfloat()
        self._attrObjs['rampeable'] = self.__build_RampeableFloat()
        self._attrObjs['fallible'] = self.__build_FallibleInteger()
        self._attrObjs['formatarray'] = self.__build_ArrayFormater()
        self._attrObjs['originarray'] = self.__build_ArrayOrigin()
        self._attrObjs['incrementarray'] = self.__build_ArrayIncrement()
        self._attrObjs['robooleanarray'] = self.__build_ROBooleanArray()
        self._attrObjs['rointegerarray'] = self.__build_ROIntegerArray()
        self._attrObjs['rofloatarray'] = self.__build_ROFloatArray()
        self._attrObjs['waveform'] = self.__build_Waveform()
        self._attrObjs['rofloatarray_ch'] = self.__build_ROFloatArray_Ch()
        self._attrObjs['rofloatarray_fn'] = self.__build_ROFloatArray_Fn()
        # self._attrObjs['multiple'] = self._build_ROFloatArray_Multiple()

    def __build_ROBoolean(self):
        robooleanObj = ROboolean()
        self._scpiObj.addCommand('source:readable:boolean:value',
                                 readcb=robooleanObj.value, default=True)
        return robooleanObj

    def __build_RWBoolean(self):
        rwbooleanObj = RWboolean()
        self._scpiObj.addCommand('source:writable:boolean:value',
                                 readcb=rwbooleanObj.value,
                                 writecb=rwbooleanObj.value,
                                 default=True)
        return rwbooleanObj

    def __build_ROInteger(self):
        rointegerObj = ROinteger()
        self._scpiObj.addCommand('source:readable:short:value',
                                 readcb=rointegerObj.value, default=True)
        self._scpiObj.addCommand('source:readable:short:upper',
                                 readcb=rointegerObj.upperLimit,
                                 writecb=rointegerObj.upperLimit)
        self._scpiObj.addCommand('source:readable:short:lower',
                                 readcb=rointegerObj.lowerLimit,
                                 writecb=rointegerObj.lowerLimit)

        return rointegerObj

    def __build_RWInteger(self):
        rwinteger = RWinteger()
        self._scpiObj.addCommand('source:writable:short:value',
                                 readcb=rwinteger.value,
                                 writecb=rwinteger.value,
                                 default=True)
        self._scpiObj.addCommand('source:writable:short:upper',
                                 readcb=rwinteger.upperLimit,
                                 writecb=rwinteger.upperLimit)
        self._scpiObj.addCommand('source:writable:short:lower',
                                 readcb=rwinteger.lowerLimit,
                                 writecb=rwinteger.lowerLimit)
        return rwinteger

    def __build_ROfloat(self):
        rofloat = ROfloat()
        self._scpiObj.addCommand('source:readable:float:value',
                                 readcb=rofloat.value, default=True)
        self._scpiObj.addCommand('source:readable:float:upper',
                                 readcb=rofloat.upperLimit,
                                 writecb=rofloat.upperLimit)
        self._scpiObj.addCommand('source:readable:float:lower',
                                 readcb=rofloat.lowerLimit,
                                 writecb=rofloat.lowerLimit)
        return rofloat

    def __build_RWfloat(self):
        rwfloat = RWfloat()
        self._scpiObj.addCommand('source:writable:float:value',
                                 readcb=rwfloat.value,
                                 writecb=rwfloat.value,
                                 default=True)
        self._scpiObj.addCommand('source:writable:float:upper',
                                 readcb=rwfloat.upperLimit,
                                 writecb=rwfloat.upperLimit)
        self._scpiObj.addCommand('source:writable:float:lower',
                                 readcb=rwfloat.lowerLimit,
                                 writecb=rwfloat.lowerLimit)
        return rwfloat

    def __build_RampeableFloat(self):
        rampeable = RWfloat()
        self._scpiObj.addCommand('rampeable:value',
                                 readcb=rampeable.value,
                                 writecb=rampeable.value,
                                 default=True)
        self._scpiObj.addCommand('rampeable:upper',
                                 readcb=rampeable.upperLimit,
                                 writecb=rampeable.upperLimit)
        self._scpiObj.addCommand('rampeable:lower',
                                 readcb=rampeable.lowerLimit,
                                 writecb=rampeable.lowerLimit)
        return rampeable

    def __build_FallibleInteger(self):
        fallible = ROIntegerFallible()
        self._scpiObj.addCommand('fallible:value',
                                 readcb=fallible.value,
                                 writecb=fallible.value,
                                 default=True)
        self._scpiObj.addCommand('fallible:upper',
                                 readcb=fallible.upperLimit,
                                 writecb=fallible.upperLimit)
        self._scpiObj.addCommand('fallible:lower',
                                 readcb=fallible.lowerLimit,
                                 writecb=fallible.lowerLimit)
        return fallible

    def __build_ArrayFormater(self):
        formatarray = Format()
        self._scpiObj.addCommand('dataformat',
                                 readcb=formatarray.value,
                                 writecb=formatarray.value)
        return formatarray

    def __build_ArrayOrigin(self):
        origin4arrays = RWfloat()
        self._scpiObj.addCommand('dataorigin',
                                 readcb=origin4arrays.value,
                                 writecb=origin4arrays.value)
        return origin4arrays

    def __build_ArrayIncrement(self):
        increment4arrays = RWfloat()
        self._scpiObj.addCommand('dataincrement',
                                 readcb=increment4arrays.value,
                                 writecb=increment4arrays.value)
        return increment4arrays

    def __build_ROBooleanArray(self):
        robooleanarray = ROBooleanArray()
        self._scpiObj.addCommand('source:readable:array:boolean:value',
                                 readcb=robooleanarray.value, default=True)
        return robooleanarray

    def __build_ROIntegerArray(self):
        rointegerarray = ROIntegerArray()
        self._scpiObj.addCommand('source:readable:array:short:value',
                                 readcb=rointegerarray.value, default=True)
        self._scpiObj.addCommand('source:readable:array:short:upper',
                                 readcb=rointegerarray.upperLimit,
                                 writecb=rointegerarray.upperLimit)
        self._scpiObj.addCommand('source:readable:array:short:lower',
                                 readcb=rointegerarray.lowerLimit,
                                 writecb=rointegerarray.lowerLimit)
        self._scpiObj.addCommand('source:readable:array:short:samples',
                                 readcb=rointegerarray.samples,
                                 writecb=rointegerarray.samples)
        return rointegerarray

    def __build_ROFloatArray(self):
        rofloatarray = ROFloatArray()
        self._scpiObj.addCommand('source:readable:array:float:value',
                                 readcb=rofloatarray.value, default=True)
        self._scpiObj.addCommand('source:readable:array:float:upper',
                                 readcb=rofloatarray.upperLimit,
                                 writecb=rofloatarray.upperLimit)
        self._scpiObj.addCommand('source:readable:array:float:lower',
                                 readcb=rofloatarray.lowerLimit,
                                 writecb=rofloatarray.lowerLimit)
        self._scpiObj.addCommand('source:readable:array:float:samples',
                                 readcb=rofloatarray.samples,
                                 writecb=rofloatarray.samples)
        return rofloatarray

    def __build_ROFloatArray_Ch(self):
        return self.__build_ROFloatArray_aux('channel', 4)

    def __build_ROFloatArray_Fn(self):
        return self.__build_ROFloatArray_aux('functions', 8)

    def __build_ROFloatArray_aux(self, name, how_many):
        root_obj = self._scpiObj._commandTree
        source_obj = self._scpiObj.addComponent('source', root_obj)
        readable_obj = self._scpiObj.addComponent('readable', source_obj)
        channels_obj = self._scpiObj.addChannel(name, how_many, readable_obj)
        rofloatarray_ch = ROFloatChannel(how_many)
        for i in range(1, how_many+1):

            floatcomponent_obj = self._scpiObj.addComponent(
                'float', channels_obj)
            for (attrName, cb_func) in \
                    [('upper', rofloatarray_ch.upperLimit),
                     ('lower', rofloatarray_ch.lowerLimit),
                     ('samples', rofloatarray_ch.samples),
                     ('switch', rofloatarray_ch.switch),
                     ('value', rofloatarray_ch.value)]:
                if attrName == 'value':
                    default = True
                else:
                    default = False
                self._scpiObj.addAttribute(
                    attrName, floatcomponent_obj,
                    readcb=cb_func, writecb=cb_func, default=default)
        return rofloatarray_ch

    def _build_ROFloatArray_Multiple(self):
        pass


    def __build_Waveform(self):
        # TODO: this should become a test for channel as well as state for them
        waveform = Waveform()
        self._scpiObj.addCommand('source:switchable:array:float:value',
                                 readcb=waveform.value, default=True)
        self._scpiObj.addCommand('source:switchable:array:float:switch',
                                 readcb=waveform.switch,
                                 writecb=waveform.switch)
        self._scpiObj.addCommand('source:switchable:array:float:samples',
                                 readcb=waveform.samples,
                                 writecb=waveform.samples)
        self._scpiObj.addCommand('source:switchable:array:float:periods',
                                 readcb=waveform.periods,
                                 writecb=waveform.periods)
        return waveform



global manager
manager = None
global exitCode
exitCode = -1


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestLogger(object):
    def __init__(self, *args, **kwargs):
        super(TestLogger, self).__init__(*args, **kwargs)

    def log(self, msg, color=None):
        if color:
            print("{0}{1}{2}".format(color, msg, bcolors.ENDC))
        else:
            print("{0}".format(msg))


class TestDevice(TestLogger):

    _device_name = None
    _device_instance = None
    _device_process = None

    def __init__(self, device_name, device_instance, extra_properties=None,
                 *args, **kwargs):
        super(TestDevice, self).__init__(*args, **kwargs)
        self._device_name = device_name
        self._device_instance = device_instance
        if isinstance(extra_properties, dict):
            self._extra_properties = extra_properties
        else:
            self._extra_properties = {}
        self._create_device_server()
        self._start_device_server()

    def __del__(self):
        self._stop_device_server()
        self._delete_device()

    @property
    def name(self):
        return self._device_name

    def _create_device_server(self):
        tangodb = PyTango.Database()
        self.log("Creating a {0} device in {1}:{2}"
                 "".format(self._device_name, tangodb.get_db_host(),
                           tangodb.get_db_port()),
                 color=bcolors.HEADER)
        devInfo = PyTango.DbDevInfo()
        devInfo.name = self._device_name
        devInfo._class = DevClass
        devInfo.server = DevServer+"/"+self._device_instance
        tangodb.add_device(devInfo)
        self.log("Server {0}/{1} added"
                 "".format(DevServer, self._device_instance),
                 color=bcolors.OKBLUE)
        if 'Instrument' not in self._extra_properties:
            self._extra_properties['Instrument'] = 'localhost'
        if 'NumChannels' not in self._extra_properties:
            self._extra_properties['NumChannels'] = "4"
        if 'NumFunctions' not in self._extra_properties:
            self._extra_properties['NumFunctions'] = "8"
        for (propertyName, propertyValue) in self._extra_properties.iteritems():
            self.set_device_property(propertyName, propertyValue)

    def set_device_property(self, property_name, property_value):
        _property = PyTango.DbDatum(property_name)
        _property.value_string.append(property_value)
        self.log("Set property {0}: {1}"
                 "".format(property_name, property_value),
                 color=bcolors.OKBLUE)
        PyTango.Database().put_device_property(self._device_name, _property)

    def remove_device_property(self, property_name):
        PyTango.Database().delete_device_property(
            self._device_name, property_name)

    def device_init_command(self):
        try:
            proxy = PyTango.DeviceProxy(self._device_name)
            proxy.Init()
            for i in range(10, 0, -1):
                if not proxy.State() in [PyTango.DevState.ON]:
                    self.log("Waiting the device ({0}) it is in {0} state"
                             "".format(i, proxy.State()))
                    sleep(1)
                else:
                    return True
        except Exception as exc:
            self.log("* Init() failed *\n", color=bcolors.FAIL)
            self.log(exc)
        return False

    def device_update_dynamic_attributes_command(self):
        try:
            proxy = PyTango.DeviceProxy(self._device_name)
            result = proxy.updateDynamicAttributes()
            self.log("updated dynamic attributes")
            return result
        except Exception as exc:
            self.log("* update dynamic attributes failed *\n",
                     color=bcolors.FAIL)
            self.log(exc)
        return False

    def _delete_device(self):
        try:
            tangodb = PyTango.Database()
            self.log("Remove a {0} device in {1}:{2}"
                     "".format(self._device_name, tangodb.get_db_host(),
                               tangodb.get_db_port()),
                     color=bcolors.OKBLUE)
            tangodb.delete_device(self._device_name)
            tangodb.delete_server("{0}/{1}".format(
                DevServer, self._device_instance))
        except Exception as exc:
            self.log("* Deletion failed, please review manually "
                     "for garbage *\n", color=bcolors.FAIL)
            self.log(exc)

    def _start_device_server(self):
        if not self._is_already_running():
            try:
                self._device_process = Popen([DevServer,
                                              self._device_instance, "-v4"])
            except OSError:
                launcher = "/usr/lib/tango/"+DevServer
                self._device_process = Popen([launcher,
                                              self._device_instance, "-v4"])
            self.log("Launched the device server has pid {0}"
                     "".format(self._device_process.pid), color=bcolors.OKBLUE)
        else:
            self.log("Test device already running!", color=bcolors.WARNING)

    def _stop_device_server(self):
        if self._device_process is None:
            return
        process = Process(self._device_process.pid)
        if not self.__stop_process(process):
            self.log(" Process {0} needs to be killed".format(process.pid),
                     color=bcolors.WARNING)
            self.__kill_process(process)
        self.log("Test device stopped")

    def _is_already_running(self):
        procs = []
        for proc in process_iter():
            if proc.name() == 'python':
                cmd = proc.cmdline()
                if len(cmd) == 3 and \
                        cmd[1].lower().startswith(DevServer.lower()) and\
                        cmd[2].lower() == DevInstance.lower():
                    self.log("found process {0}".format(proc.pid))
                    procs.append(proc)
        if len(procs) == 0:
            return False
        if len(procs) > 1:
            self.log("ALERT: the device seems to be running more than once",
                     color=bcolors.FAIL)
        return True

    def __stop_process(self, process):
        nChildren = len(process.children())
        if nChildren > 0:
            self.log("Process {0} has {1} children to be stopped"
                     "".format(process.pid, nChildren), color=bcolors.OKBLUE)
            for child in process.children():
                if not self.__stop_process(child):
                    self.log("Process {0} still running, proceed to kill"
                             "".format(child.pid), color=bcolors.WARNING)
                    self.__kill_process(child)
        process.terminate()
        for i in range(10):  # 1 second waiting
            if not process.is_running():
                return True
            print(".", end='')  # , flush=True) # it is not that future
            sys.stdout.flush()
            process.terminate()
            sleep(0.1)
        return False

    def __kill_process(self, process):
        try:
            process.kill()
        except Exception as exc:
            pass


dynAttr_sample_content = \
    'Attribute("float_scalar_ro_bis",\n' \
    '          {\'type\': PyTango.CmdArgType.DevFloat,\n' \
    '           \'dim\': [0],\n' \
    '           \'readCmd\': "source:readable:float:value?"\n' \
    '           })\n' \
    '\n' \
    'Attribute("float_scalar_rw_bis",\n' \
    '          {\'type\': PyTango.CmdArgType.DevFloat,\n' \
    '           \'dim\': [0],\n' \
    '           \'readCmd\': "source:writable:float:value?",\n' \
    '           \'writeCmd\': \n' \
    '               lambda value: "source:writable:float:"\n' \
    '                             "value {0}".format(value)\n' \
    '           })'


class TestManager(TestLogger):

    _instrument = None
    _tester = None

    def __init__(self, *args, **kwargs):
        super(TestManager, self).__init__(*args, **kwargs)
        self._instrument = FakeInstrument()
        self.log("FakeInstrument build: {0!r}".format(self._instrument))
        self.log("\tCommand tree: {0}".format(self._instrument.tree()))
        self._tester = TestDevice(DevName, DevInstance)

    def __del__(self):
        del self._tester
        del self._instrument

    def _is_device_ready(self, test_device):
        if test_device is None:
            return False
        try:
            device_proxy = PyTango.DeviceProxy(test_device.name)
            self.log("Device is in {0} state".format(device_proxy.State()))
            return True
        except Exception as exc:
            self.log("Exception checking if the device is ready: {0}"
                     "".format(exc))
            return False

    def launch_test(self):
        while not self._is_device_ready(self._tester):
            self.log("Waiting the device", color=bcolors.WARNING)
            sleep(1)
        self.log("Start the test", color=bcolors.HEADER)
        device_proxy = PyTango.DeviceProxy(self._tester.name)
        # FIXME: once the scpilib supports it, the tests must be made with
        #  and without this flag raised.
        device_proxy['ReadAfterWrite'] = True
        self.log("Testing {0} a read after write"
                 "".format("with" if device_proxy['ReadAfterWrite'].value
                                            else "with out"))
        test_methods = [
            self.test_communications,
            self.test_readings,
            self.test_writes,
            self.test_glitch,
            self.test_waveform_switch,
            self.test_dyn_attr_injection,
            self.test_avoid_idn_and_specify_instructions_set,
        ]
        reports = []
        for i, test in enumerate(test_methods):
            result, report = test(device_proxy)
            if not result:
                return i+1
            if isinstance(report, list) and len(report) > 0 \
                    and isinstance(report[0], list):
                reports += report
            else:
                reports.append(report)
        self.log("All tests passed", color=bcolors.HEADER)
        try:
            for name, msg in reports:
                self.log("\t{0:30}:\t{1}".format(name, msg))
        except Exception as exc:
            self.log(reports)
        return 0

    def _check_test(self, names, values):
        nones = [value is None for value in values]
        if any(nones):
            msg = "{0}TEST FAILED{1}:\n".format(bcolors.FAIL. bcolors.ENDC)
            for i, name in enumerate(names):
                msg = ''.join("{0}\t{1} = {2!r}\n"
                              "".format(msg, name, values[i]))
            return False, msg
        else:
            return True, "{0}TEST PASSED{1}" \
                         "".format(bcolors.OKGREEN, bcolors.ENDC)

    ###########################################################################
    # Tests area
    def test_communications(self, device_proxy):
        test_title = "Communications"
        attr_names = ['QueryWindow', 'TimeStampsThreshold', 'ReadAfterWrite',
                      'State', 'Status']
        attrs = device_proxy.read_attributes(attr_names)
        values = [attr.value for attr in attrs]
        result, msg = self._check_test(attr_names, values)
        self.log("{0}:\t{1}".format(test_title, msg))
        return result, [test_title, msg]

    def test_readings(self, device_proxy):
        test_title = "Readings"
        exclude_name = ['Idn', 'QueryWindow', 'TimeStampsThreshold', 'Version',
                        'ReadAfterWrite', 'State', 'Status',
                        'RampeableStep', 'RampeableStepSpeed', 'Fallible']
        exclude_pattern = {'startswith': ['Waveform', 'wfState', 'wfChannels']}
        attr_names = []
        for attrName in device_proxy.get_attribute_list():
            if attrName in exclude_name:
                continue  # next step in the loop
            in_the_loop = False
            for start_str in exclude_pattern['startswith']:
                if attrName.startswith(start_str):
                    in_the_loop = True
            if not in_the_loop:
                attr_names.append(attrName)
            # TODO: special attributes like ramps descriptors or spectra
        self.log("attributes for the {0} test".format(test_title),
                 color=bcolors.OKBLUE)
        for attr_name in attr_names:
            self.log("\t{0}".format(attr_name))
        reports = []
        for i in range(1, len(attr_names)+1):
            device_proxy['QueryWindow'] = i
            attrs = device_proxy.read_attributes(attr_names)
            values = [attr.value for attr in attrs]
            nones = [value is None for value in values]
            result, msg = self._check_test(attr_names, values)
            self.log("Readings[{0}]\t{1}".format(i, msg))
            reports.append(["{0}[{1}]".format(test_title, i), msg])
            if not result:
                return False, reports
            sleep(1.1*device_proxy['TimeStampsThreshold'].value)
        return True, reports

    def test_writes(self, device_proxy):
        test_title = "Writes"
        attr_names = []
        values = []
        for attr_name in device_proxy.get_attribute_list():
            if attr_name.endswith('_rw'):
                r_value = device_proxy[attr_name].value
                if device_proxy[attr_name].type == PyTango.DevFloat:
                    w_value = int(r_value/1.1) + (r_value % 1)
                elif device_proxy[attr_name].type == PyTango.DevShort:
                    w_value = r_value+1
                elif device_proxy[attr_name].type == PyTango.DevBoolean:
                    w_value = not r_value
                self.log("*** {0} has {1} and going to write {2}"
                         "".format(attr_name, r_value, w_value))
                device_proxy[attr_name] = w_value
                # Time between those two reads must be below the
                # 'TimeStampsThreshold' to check that, even the time hasn't
                # passed, it has been change by the write.
                sleep(0.05)
                new_rvalue = device_proxy[attr_name].value
                self.log("*** {0}: had {1}, sent {2}, now {3}"
                         "".format(attr_name, r_value, w_value, new_rvalue))
                if new_rvalue == w_value:
                    values.append(w_value)
                else:
                    values.append(None)
        result, msg = self._check_test(attr_names, values)
        self.log("{0}:\t{1}".format(test_title, msg))
        return result, [test_title, msg]

    def test_glitch(self, device_proxy):
        test_title = "Glitch"
        if device_proxy['State'].value in [PyTango.DevState.ON,
                                           PyTango.DevState.RUNNING]:
            if device_proxy.Exec("self.skippy.watchdogObj") == 'None':
                msg = "Device doesn't have the watchdog feature!"
                self.log(msg, color=bcolors.WARNING)
                return False, [test_title, msg]
            reaction_time = device_proxy.Exec(
                "self.skippy.watchdogObj.checkPeriod")
            self.log("reactiontime: {0}".format(reaction_time))
            reaction_time = float(reaction_time)
            t_0 = datetime.now()
            self._instrument.close()
            self.log("Instrument closed", color=bcolors.OKBLUE)
            reacted = self._wait_until_reaction(
                device_proxy, reaction_time,
                [PyTango.DevState.FAULT, PyTango.DevState.DISABLE])
            if not reacted:
                msg = "No device reaction after {0}" \
                      "".format(datetime.now()-t_0)
                self.log(msg)
                fullmsg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                          "".format(bcolors.FAIL, bcolors.ENDC,
                                    bcolors.WARNING, msg)
                return False, [test_title, fullmsg]
            self.log("Device has reacted", color=bcolors.OKBLUE)
            t_1 = datetime.now()
            self._instrument.open()
            self.log("Instrument reopened", color=bcolors.OKBLUE)
            reacted = self._wait_until_reaction(
                device_proxy, reaction_time,
                [PyTango.DevState.ON, PyTango.DevState.RUNNING])
            if not reacted:
                msg = "No device recovery after {0}" \
                      "".format(datetime.now()-t_1)
                self.log(msg)
                full_msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                          "".format(bcolors.FAIL, bcolors.ENDC,
                                    bcolors.WARNING, msg)
                return False, [test_title, full_msg]
            self.log("Device has recovered", color=bcolors.OKBLUE)
            msg = "{0}TEST PASSED{1}".format(bcolors.OKGREEN, bcolors.ENDC)
            self.log("{0}:\t{1}".format(test_title, msg))
            return True, [test_title, msg]
        else:
            msg = "{0}TEST FAILED{1}:\n\t{2}Wrong device state {3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC,
                            bcolors.WARNING, device_proxy['State'].value)
            self.log("{0}:\t{1}".format(test_title, msg))
            return False, [test_title, msg]

    def test_waveform_switch(self, device_proxy):
        test_title = "Waveform Switch"
        self.log("attributes for the {0} test".format(test_title),
                 color=bcolors.OKBLUE)

        def check():
            if switch is False and quality != PyTango.AttrQuality.ATTR_INVALID:
                raise Exception("Attributes read when shouldn't")
            elif switch is True and quality != PyTango.AttrQuality.ATTR_VALID:
                raise Exception("Attributes not read when should")

        try:
            waveform_attr = 'Waveform'
            switch_attr = 'Waveform_switch'
            quality = device_proxy[waveform_attr].quality
            switch = device_proxy[switch_attr].value
            check()
            device_proxy[switch_attr] = not switch
            quality = device_proxy[waveform_attr].quality
            switch = device_proxy[switch_attr].value
            check()
            device_proxy[switch_attr] = not switch
            msg = "{0}TEST PASSED{1}".format(bcolors.OKGREEN, bcolors.ENDC)
            self.log("{0}:\t{1}".format(test_title, msg))
            return True, [test_title, msg]
        except Exception as exc:
            msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, exc)
            self.log("{0}:\t{1}".format(test_title, msg))
            return False, [test_title, msg]

    def test_dyn_attr_injection(self, device_proxy):
        test_title = "DynamicAttributes injection"
        try:
            property_name = "DynamicAttributes"
            property_value = dynAttr_sample_content
            self._tester.set_device_property(property_name, property_value)
            if not self._tester.device_update_dynamic_attributes_command():
                raise AssertionError("Device did NOT update the attributes")
            try:
                device_proxy['QueryWindow'] = 2
                attrs = device_proxy.read_attributes(['float_scalar_ro',
                                                      'float_scalar_ro_bis'])
                values = [attr.value for attr in attrs]
                nones = [value is None for value in values]
                if any(nones):
                    raise AssertionError("ReadOnly read failed")
            except AssertionError as exc:
                raise exc
            except Exception as exc:
                self.log(exc, color=bcolors.FAIL)
                raise AssertionError(
                    "ReadOnly attribute did NOT work as expected")
            try:
                wait_time = device_proxy['TimeStampsThreshold'].value
                attrs = device_proxy.read_attributes(['float_scalar_rw',
                                                      'float_scalar_rw_bis'])
                values = [attr.value for attr in attrs]
                if values[0] != values[1]:
                    raise AssertionError("ReadWrite read failed")
                r_value = values[0]
                w_value = int(r_value / 1.1)+(r_value % 1)
                device_proxy['float_scalar_rw'] = w_value
                sleep(wait_time)
                if device_proxy['float_scalar_rw_bis'].value != w_value:
                    raise AssertionError("ReadWrite write failed (1)")
                device_proxy['float_scalar_rw_bis'] = r_value
                sleep(wait_time)
                if device_proxy['float_scalar_rw'].value != r_value:
                    raise AssertionError("ReadWrite write failed (2)")
            except AssertionError as exc:
                raise exc
            except Exception as exc:
                self.log(exc, color=bcolors.FAIL)
                raise AssertionError(
                    "ReadWrite attribute did NOT work as expected")
            try:
                self._tester.remove_device_property(property_name)
                if not self._tester.device_init_command():
                    raise AssertionError(
                        "Device did NOT remove dynamic attributes")
            except Exception as exc:
                self.log(exc, color=bcolors.FAIL)
                raise AssertionError(
                    "Remove dynamic attributes did NOT work as excepted")
        except Exception as exc:
            msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, exc)
            self.log("{0}:\t{1}".format(test_title, msg))
            return False, [test_title, msg]
        else:
            msg = "{0}TEST PASSED{1}".format(bcolors.OKGREEN, bcolors.ENDC)
            self.log("{0}:\t{1}".format(test_title, msg))
            return True, [test_title, msg]

    def test_avoid_idn_and_specify_instructions_set(self, device_proxy):
        test_title = "Avoid IDN and specify instruction set"
        try:
            property_name = "AvoidIDN"
            property_value = 'True'
            self._tester.set_device_property(property_name, property_value)

            self.log("first part of the test: "
                     "device that doesn't use the IDN")
            if not self._tester.device_init_command():
                raise Exception("Prepare to avoid IDN failed")
            self.log("Second part of the test: "
                     "dynamic attributes for this device")
            property_name = "DynamicAttributes"
            property_value = dynAttr_sample_content
            self._tester.set_device_property(property_name, property_value)
            if not self._tester.device_update_dynamic_attributes_command():
                raise Exception("dynamic attributes failed")
            self.log("Third part of the test: "
                     "establish from where it should read the file with the "
                     "instrument definition")

            def _get_file_fullpath(filename):
                path = os.getcwd()
                full_path = os.path.join(path, filename)
                return full_path

            property_name = 'InstructionsFile'
            property_value = _get_file_fullpath(
                '../skippylib/instructions/fakeinstruments/tester.py')
            self._tester.set_device_property(property_name, property_value)
            if not self._tester.device_init_command():
                raise Exception("Prepare to specify instructions file failed")
            self.log("Device restored with the specified instruction set")

            result, report = self.test_readings(device_proxy)
            if result is False:
                raise AssertionError(report)
            result, report = self.test_writes(device_proxy)
            if result is False:
                raise AssertionError(report)
            self.log("clean test modifications")
            for property_name in ["AvoidIDN", "DynamicAttributes",
                                 "InstructionsFile"]:
                self._tester.remove_device_property(property_name)
            self._tester.device_init_command()
        except Exception as exc:
            msg = "{0}TEST FAILED{1}:\n\t{2}{3}{1}" \
                  "".format(bcolors.FAIL, bcolors.ENDC, bcolors.WARNING, exc)
            self.log("{0}:\t{1}".format(test_title, msg))
            return False, [test_title, msg]
        else:
            msg = bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC
            self.log("{0}:\t{1}".format(test_title, msg))
            return True, [test_title, msg]

    def _wait_until_reaction(self, device, reaction_period, states_lst):
        tries = 0
        state = device['State'].value
        while state not in states_lst:
            self.log("No device reaction yet... ({0})".format(state),
                     bcolors.WARNING)
            sleep(reaction_period)
            tries += 1
            if tries == 10:
                return False
            state = device['State'].value
        self.log("Found a device reaction, state {0}".format(state))
        return True


def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        print("\nCaptured a Ctrl+c: terminating the execution...")
    else:
        print("Unmanaged signal received ({0})".format(signum))


def main():
    global exitCode
    if argparse is not None:
        parser = argparse.ArgumentParser(description='Test the Skippy device '
                                         'server using a fake instrument.')
        parser.add_argument('--no-remove', dest='no_remove',
                            action="store_true",
                            # default=False,
                            help="don't destroy the test until the user say")
        args = parser.parse_args()
    else:
        class Object(object):
            no_remove = False
        args = Object()
    try:
        global manager
        manager = TestManager()
        sleep(3)
        manager.log("\n\tThe test is going to be launched",
                    color=bcolors.UNDERLINE)
        signal.signal(signal.SIGINT, signal_handler)
        sleep(3)
        exitCode = manager.launch_test()
        if args.no_remove:
            print("\n\tPress Ctrl+c to finish the fake device")
            signal.pause()
    except Exception as e:
        print("\nCannot complete the test: %s\n" % e)
        traceback.print_exc()
    finally:
        del manager
    sys.exit(exitCode)


if __name__ == '__main__':
    main()
