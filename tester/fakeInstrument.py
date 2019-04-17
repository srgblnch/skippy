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

import argparse
from datetime import datetime
from instrAttrs import (ROinteger, RWinteger, ROfloat, RWfloat,
                        ROIntegerFallible, Format, ROIntegerArray)
from instrIdn import InstrumentIdentification, __version__
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


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class FakeInstrument(object):

    _identity = None
    _scpiObj = None
    _attrObjs = {}

    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._buildFakeSCPI()

    def _buildFakeSCPI(self):
        version = "%s+scpilib_%s" % (__version__, scpilib.version.version())
        self._identity = InstrumentIdentification('FakeInstruments. Inc',
                                                  'Tester', 0, version)
        self._scpiObj = scpilib.scpi(local=True, debug=True, log2File=True)
        self._buildSpecialCommands()
        self._buildNormalCommands()
        self.open()

    def __str__(self):
        return "%s" % self._scpiObj

    def __repr__(self):
        return "%r" % self._scpiObj

    def tree(self):
        return "%r" % self._scpiObj._commandTree

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
        self._attrObjs['fallible'] = fallible
        formatarray = Format()
        self._scpiObj.addCommand('dataformat',
                                 readcb=formatarray.value,
                                 writecb=formatarray.value)
        self._attrObjs['formatarray'] = formatarray
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
        
        self._attrObjs['rointegerarray'] = rointegerarray


global manager
manager = None
global exitCode
exitCode = -1


class TestManager(object):

    _deviceProcess = None

    def __init__(self, *args, **kwargs):
        super(TestManager, self).__init__(*args, **kwargs)
        self._instrument = FakeInstrument()
        self.log("FakeInstrument build: %r" % (self._instrument))
        self.log("\tCommand tree: %s" % (self._instrument.tree()))
        self._createTestDevice()
        self._startTestDevice()

    def __del__(self):
        self._stopTestDevice()
        self._deleteTestDevice()

    def log(self, msg, color=None):
        if color:
            print(color+"%s" % (msg)+bcolors.ENDC)
        else:
            print("%s" % (msg))

    def _createTestDevice(self):
        tangodb = PyTango.Database()
        self.log("Creating a %s device in %s:%s"
                 % (DevName, tangodb.get_db_host(), tangodb.get_db_port()),
                 color=bcolors.HEADER)
        devInfo = PyTango.DbDevInfo()
        devInfo.name = DevName
        devInfo._class = DevClass
        devInfo.server = DevServer+"/"+DevInstance
        tangodb.add_device(devInfo)
        self.log("Server %s added" % (DevServer+"/"+DevInstance),
                 color=bcolors.OKBLUE)
        propertyName = 'Instrument'
        propertyValue = 'localhost'
        property = PyTango.DbDatum(propertyName)
        property.value_string.append(propertyValue)
        self.log("Set property %s: %s" % (propertyName, propertyValue),
                 color=bcolors.OKBLUE)
        tangodb.put_device_property(DevName, property)

    def _startTestDevice(self):
        if not self._isAlreadyRunning():
            self._deviceProcess = Popen([DevServer, DevInstance, "-v4"])
            self.log("Launched the device server has pid %d"
                     % (self._deviceProcess.pid), color=bcolors.OKBLUE)
        else:
            self.log("Test device already running!", color=bcolors.WARNING)

    def _stopTestDevice(self):
        if self._deviceProcess is None:
            return
        process = Process(self._deviceProcess.pid)
        if not self.__stopProcess(process):
            self.log(" Process %d needs to be killed" % (process.pid),
                     color=bcolors.WARNING)
            self.__killProcess(process)
        self.log("Test device stopped")

    def __stopProcess(self, process):
        nChildren = len(process.children())
        if nChildren > 0:
            self.log("Process %d has %d children to be stopped"
                     % (process.pid, nChildren), color=bcolors.OKBLUE)
            for child in process.children():
                if not self.__stopProcess(child):
                    self.log("Process %d still running, proceed to kill"
                             % (child.pid), color=bcolors.WARNING)
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
                     % (DevName, tangodb.get_db_host(), tangodb.get_db_port()),
                     color=bcolors.OKBLUE)
            tangodb.delete_device(DevName)
            tangodb.delete_server(DevServer+"/"+DevInstance)
        except Exception as e:
            self.log("* Deletion failed, please review manually "
                     "for garbage *\n", color=bcolors.FAIL)

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
            self.log("ALERT: the device seems to be running more than once",
                     color=bcolors.FAIL)
        return True

    def _isDeviceReady(self):
        if self._deviceProcess is None:
            return False
        try:
            deviceProxy = PyTango.DeviceProxy(DevName)
            self.log("Device is in %s state" % deviceProxy.State())
            return True
        except:
            return False

    # Tests ---
    def launchTest(self):
        while not self._isDeviceReady():
            self.log("Waiting the device", color=bcolors.WARNING)
            sleep(1)
        self.log("Start the test", color=bcolors.HEADER)
        deviceProxy = PyTango.DeviceProxy(DevName)
        testMethods = [self.test_communications,
                       self.test_readings,
                       self.test_writes,
                       self.test_glitch]
        reports = []
        for i, test in enumerate(testMethods):
            result, report = test(deviceProxy)
            if not result:
                return i+1
            if isinstance(report[0], list):
                reports += report
            else:
                reports.append(report)
        self.log("All tests passed", color=bcolors.HEADER)
        for name, msg in reports:
            self.log("\t%s:\t%s" % (name, msg))
        return 0

    def _checkTest(self, names, values):
        nones = [value is None for value in values]
        if any(nones):
            msg = bcolors.FAIL+"TEST FAILED"+bcolors.ENDC+":\n"
            for i, name in enumerate(names):
                msg = ''.join("%s\t%s = %r\n" % (msg, name, values[i]))
            return (False, msg)
        else:
            return (True, bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC)

    def test_communications(self, device):
        testTitle = "Communications"
        attrNames = ['QueryWindow', 'TimeStampsThreshold', 'State', 'Status']
        attrs = device.read_attributes(attrNames)
        values = [attr.value for attr in attrs]
        result, msg = self._checkTest(attrNames, values)
        self.log("%s:\t%s" % (testTitle, msg))
        return result, [testTitle, msg]

    def test_readings(self, device):
        testTitle = "Readings"
        exclude = ['QueryWindow', 'TimeStampsThreshold', 'State', 'Status',
                   'RampeableStep', 'RampeableStepSpeed', 'Fallible']
        attrNames = []
        results = []
        for attrName in device.get_attribute_list():
            if attrName not in exclude:
                attrNames.append(attrName)
            # TODO: special attributes like ramps descriptors or spectra
        self.log("attributes for the %s test" % (testTitle),
                 color=bcolors.OKBLUE)
        for attrName in attrNames:
            self.log("\t{}".format(attrName))
        reports = []
        for i in range(1, len(attrNames)+1):
            device['QueryWindow'] = i
            attrs = device.read_attributes(attrNames)
            values = [attr.value for attr in attrs]
            nones = [value is None for value in values]
            result, msg = self._checkTest(attrNames, values)
            self.log("Readings[%d]\t%s" % (i, msg))
            reports.append(["%s[%d]" % (testTitle, i), msg])
            if not result:
                return False, reports
            sleep(1.1*device['TimeStampsThreshold'].value)
        return True, reports

    def test_writes(self, device):
        testTitle = "Writes"
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
                if device[attrName].value == rvalue:
                    self.log("for %s: %s == %s"
                             % (attrName, device[attrName].value, rvalue))
                    values.append(wvalue)
                else:
                    values.append(None)
        result, msg = self._checkTest(attrNames, values)
        self.log("%s:\t%s" % (testTitle, msg))
        return result, [testTitle, msg]

    def test_glitch(self, device):
        testTitle = "Glitch"
        if device['State'].value in [PyTango.DevState.ON,
                                     PyTango.DevState.RUNNING]:
            reactiontime = \
                float(device.Exec("self.skippy.watchdogObj.checkPeriod"))
            t_0 = datetime.now()
            self._instrument.close()
            self.log("Instrument closed", color=bcolors.OKBLUE)
            reacted = self._waitUntilReaction(device, reactiontime,
                                              [PyTango.DevState.FAULT,
                                               PyTango.DevState.DISABLE])
            if not reacted:
                msg = "No device reaction after %s" % (datetime.now()-t_0)
                self.log(msg)
                fullmsg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + msg + bcolors.ENDC
                return False, [testTitle, fullmsg]
            self.log("Device has reacted", color=bcolors.OKBLUE)
            t_1 = datetime.now()
            self._instrument.open()
            self.log("Instrument reopened", color=bcolors.OKBLUE)
            reacted = self._waitUntilReaction(device, reactiontime,
                                              [PyTango.DevState.ON,
                                               PyTango.DevState.RUNNING])
            if not reacted:
                msg = "No device recovery after %s" % (datetime.now()-t_1)
                self.log(msg)
                fullmsg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + msg + bcolors.ENDC
                return False, [testTitle, fullmsg]
            self.log("Device has recovered", color=bcolors.OKBLUE)
            msg = bcolors.OKGREEN+"TEST PASSED"+bcolors.ENDC
            self.log("%s:\t%s" % (testTitle, msg))
            return True, [testTitle, msg]
        else:
            msg = bcolors.FAIL + "TEST FAILED" + bcolors.ENDC + \
                    ":\n\t" + bcolors.WARNING + \
                    "Wrong device state %s" % (device['State'].value) \
                    + bcolors.ENDC
            self.log("%s:\t%s" % (testTitle, msg))
            return False, [testTitle, msg]

    def _waitUntilReaction(self, device, reactionPeriod, statesLst):
        tries = 0
        state = device['State'].value
        while state not in statesLst:
            self.log("No device reaction yet... (%s)" % state,
                     bcolors.WARNING)
            sleep(reactionPeriod)
            tries += 1
            if tries == 10:
                return False
            state = device['State'].value
        self.log("Found a device reaction, state %s" % state)
        return True


def signalHandler(signum, frame):
    if signum == signal.SIGINT:
        print("\nCaptured a Ctrl+c: terminating the execution...")
    else:
        print("Unmanaged signal received (%d)" % (signum))


def main():
    global exitCode
    parser = argparse.ArgumentParser(description='Test the Skippy device '
                                     'server using a fake instrument.')
    parser.add_argument('--no-remove', dest='no_remove',
                        action="store_true",
                        #default=False,
                        help="don't destroy the test until the user say")
    args = parser.parse_args()
    try:
        global manager
        manager = TestManager()
        sleep(3)
        manager.log("\n\tThe test is going to be launched",
                    color=bcolors.UNDERLINE)
        signal.signal(signal.SIGINT, signalHandler)
        sleep(3)
        exitCode = manager.launchTest()
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
