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

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


from instrAttrs import ROinteger, RWinteger, ROfloat, RWfloat
from instrIdn import InstrumentIdentification, __version__
from psutil import process_iter, Process
import PyTango
import signal
import scpi
from select import select
from subprocess import Popen, PIPE
import sys
from time import sleep
import traceback

DevServer = 'Skippy'
DevInstance = 'FakeInstrument'
DevClass = 'Skippy'
DevName = 'fake/skyppy/instrument-01'


class FakeInstrument(object):

    _identity = None
    _scpiObj = None
    _attrObjs = {}

    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._buildFakeSCPI()

    def _buildFakeSCPI(self):
        self._identity = InstrumentIdentification('FakeInstruments. Inc',
                                                  'Tester', 0,
                                                  __version__)
        self._scpiObj = scpi.scpi(local=True, debug=True, log2File=True)
        self._buildSpecialCommands()
        self._buildNormalCommands()
        self.open()

    def open(self):
        self._scpiObj.open()

    def close(self):
        self._scpiObj.close()

    def _buildSpecialCommands(self):
        self._scpiObj.addSpecialCommand('IDN', self._identity.idn)

    def _buildNormalCommands(self):
        rointegerObj = ROinteger()
        self._scpiObj.addCommand('source:readable:short:value',
                                 readcb=rointegerObj.value, default=True)
        self._scpiObj.addCommand('source:readable:short:upper',
                                 readcb=rointegerObj.upperLimit,
                                 writecb=rointegerObj.upperLimit)
        self._scpiObj.addCommand('source:readable:short:lower',
                                 readcb=rointegerObj.lowerLimit,
                                 writecb=rointegerObj.lowerLimit)
        self._attrObjs['rointeger'] = rointegerObj
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
        self._attrObjs['rwinteger'] = rwinteger
        rofloat = ROfloat()
        self._scpiObj.addCommand('source:readable:float:value',
                                 readcb=rofloat.value, default=True)
        self._scpiObj.addCommand('source:readable:float:upper',
                                 readcb=rofloat.upperLimit,
                                 writecb=rofloat.upperLimit)
        self._scpiObj.addCommand('source:readable:float:lower',
                                 readcb=rofloat.lowerLimit,
                                 writecb=rofloat.lowerLimit)
        self._attrObjs['rofloat'] = rofloat
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
        self._attrObjs['rwfloat'] = rwfloat
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
        self._attrObjs['rampeable'] = rampeable
#         rointegerarray = ROintegerArray()
#         self._scpiObj.addCommand('source:readable:array:short:value',
#                                  readcb=rointegerarray.value, default=True)
#         self._scpiObj.addCommand('source:readable:array:short:upper',
#                                  readcb=rointegerarray.upperLimit,
#                                  writecb=rointegerarray.upperLimit)
#         self._scpiObj.addCommand('source:readable:array:short:lower',
#                                  readcb=rointegerarray.lowerLimit,
#                                  writecb=rointegerarray.lowerLimit)
#         self._scpiObj.addCommand('source:readable:array:short:samples',
#                                  readcb=rointegerarray.samples,
#                                  writecb=rointegerarray.samples)
#         self._attrObjs['rointegerarray'] = rointegerarray


global manager
manager = None


class TestManager(object):

    _deviceProcess = None

    def __init__(self, *args, **kwargs):
        super(TestManager, self).__init__(*args, **kwargs)
        self._instrument = FakeInstrument()
        self._createTestDevice()
        self._startTestDevice()

    def __del__(self):
        self._stopTestDevice()
        self._deleteTestDevice()

    def log(self, msg):
        print("%s" % (msg))

    def _createTestDevice(self):
        tangodb = PyTango.Database()
        self.log("Creating a %s device in %s:%s"
                 % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
        devInfo = PyTango.DbDevInfo()
        devInfo.name = DevName
        devInfo._class = DevClass
        devInfo.server = DevServer+"/"+DevInstance
        tangodb.add_device(devInfo)
        self.log("Server %s added" % (DevServer+"/"+DevInstance))
        propertyName = 'Instrument'
        propertyValue = 'localhost'
        property = PyTango.DbDatum(propertyName)
        property.value_string.append(propertyValue)
        self.log("Set property %s: %s" % (propertyName, propertyValue))
        tangodb.put_device_property(DevName, property)

    def _startTestDevice(self):
        if not self._isAlreadyRunning():
            self._deviceProcess = Popen([DevServer, DevInstance, "-v4"])
            self.log("Launched the device server has pid %d"
                     % (self._deviceProcess.pid))
        else:
            self.log("Test device already running!")

    def _stopTestDevice(self):
        if self._deviceProcess is None:
            return
        process = Process(self._deviceProcess.pid)
        if not self.__stopProcess(process):
            self.log(" Process %d needs to be killed" % (process.pid))
            self.__killProcess(process)
        self.log("Test device stopped")

    def __stopProcess(self, process):
        nChildren = len(process.children())
        if nChildren > 0:
            self.log("Process %d has %d children to be stopped"
                     % (process.pid, nChildren))
            for child in process.children():
                if not self.__stopProcess(child):
                    self.log("Process %d still running, proceed to kill"
                             % (child.pid))
                    self.__killProcess(child)
        process.terminate()
        for i in range(10):  # 1 second waiting
            if not process.is_running():
                return True
            print(".", end='')  # , flush=True) # it is not that future
            sys.stdout.flush()
            process.terminate()
            sleep(0.1)
        return False

    def __killProcess(self, process):
        try:
            process.kill()
        except:
            pass

    def _deleteTestDevice(self):
        try:
            tangodb = PyTango.Database()
            self.log("Remove a %s device in %s:%s"
                     % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
            tangodb.delete_device(DevName)
            tangodb.delete_server(DevServer+"/"+DevInstance)
        except Exception as e:
            self.log("* Deletion failed, please review manually "
                     "for garbage *\n")

    def _isAlreadyRunning(self):
        procs = []
        for proc in process_iter():
            if proc.name() == 'python':
                cmd = proc.cmdline()
                if cmd[1].lower().startswith(DevServer.lower()) and\
                        cmd[2].lower() == DevInstance.lower():
                    self.log("found process %d" % (proc.pid))
                    procs.append(proc)
        if len(procs) == 0:
            return False
        if len(procs) > 1:
            self.log("ALERT: the device seems to be running more than once")
        return True

    # Tests ---
    def launchTest(self):
        deviceProxy = PyTango.DeviceProxy(DevName)
        testMethods = [self.test_communications,
                       self.test_readings,
                       self.test_writes,
                       self.test_glitch]
        for i, test in enumerate(testMethods):
            if not test(deviceProxy):
                break

    def _checkTest(self, names, values):
        nones = [value is None for value in values]
        if any(nones):
            msg = "TEST FAILED:\n"
            for i, name in enumerate(names):
                msg = ''.join("%s\t%s = %r\n" % (msg, name, values[i]))
            return (False, msg)
        else:
            return (True, "TEST PASSED")

    def test_communications(self, device):
        attrNames = ['QueryWindow', 'TimeStampsThreshold', 'State', 'Status']
        attrs = device.read_attributes(attrNames)
        values = [attr.value for attr in attrs]
        result, msg = self._checkTest(attrNames, values)
        self.log("Communications:\t%s" % msg)
        return result

    def test_readings(self, device):
        exclude = ['QueryWindow', 'TimeStampsThreshold', 'State', 'Status']
        attrNames = []
        results = []
        for attrName in device.get_attribute_list():
            if attrName not in exclude:
                attrNames.append(attrName)
            # TODO: special attributes like ramps descriptors or spectra
        for i in range(1, len(attrNames)+1):
            device['QueryWindow'] = i
            attrs = device.read_attributes(attrNames)
            values = [attr.value for attr in attrs]
            nones = [value is None for value in values]
            result, msg = self._checkTest(attrNames, values)
            self.log("Readings[%d]\t%s" % (i, msg))
            if not result:
                return False
            sleep(1.1*device['TimeStampsThreshold'].value)
        return True

    def test_writes(self, device):
        attrNames = []
        values = []
        for attrName in device.get_attribute_list():
            if attrName.endswith('_rw'):
                rvalue = device[attrName].value
                if device[attrName].type == PyTango.DevFloat:
                    wvalue = rvalue/1.1
                elif device[attrName].type == PyTango.DevShort:
                    wvalue = rvalue+1
                device[attrName] = wvalue
                # Time between those two reads must be below the
                # 'TimeStampsThreshold' to check that, even the time hasn't
                # passed, it has been change by the write.
                if device[attrName].value == wvalue:
                    values.append(None)
                else:
                    values.append(wvalue)
        result, msg = self._checkTest(attrNames, values)
        self.log("Writes:\t%s" % msg)
        return result

    def test_glitch(self, device):
        if device['State'].value in [PyTango.DevState.ON]:
            self._instrument.close()
            sleep(1)  # FIXME: enough time to the device reaction
            if device['State'].value not in [PyTango.DevState.FAULT]:
                self.log("Glitch:\tTEST FAILED:\n\tNo device reaction")
                return False
            self._instrument.open()
            sleep(1)  # FIXME: enough time to the device reaction
            if device['State'].value not in [PyTango.DevState.ON]:
                self.log("Glitch:\tTEST FAILED:\n\tNo device recovery")
                return False
        self.log("Glitch:\tTEST PASSED")
        return True


def signalHandler(signum, frame):
    if signum == signal.SIGINT:
        print("\nCaptured a Ctrl+c: terminating the execution...")
        global manager
        del manager
        sys.exit(0)
    else:
        print("Unmanaged signal received (%d)" % (signum))


def main():
    try:
        global manager
        manager = TestManager()
        signal.signal(signal.SIGINT, signalHandler)
        print("\n\tPress Ctrl+c to finish the fake device")
        signal.pause()
    except Exception as e:
        print("\nCannot complete the test: %s\n" % e)
        traceback.print_exc()
        del manager


if __name__ == '__main__':
    main()
