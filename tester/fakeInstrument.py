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
from instrIdn import InstrumentIdentification
import PyTango
import signal
import scpi
from select import select
from skippy import version as skippyVersion
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
                                                  skippyVersion())
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
        self._deviceProcess = Popen([DevServer, DevInstance, "-v4"])
        self.log("Launched the device server has pid %d"
                 % (self._deviceProcess.pid))

    def _stopTestDevice(self):
        if self._deviceProcess is None:
            return
        self._deviceProcess.terminate()
        sleep(1)
        if self._deviceProcess.poll() is not None:
            self.log("device server process %d terminated (signal %d)"
                     % (self._deviceProcess.pid,
                        abs(self._deviceProcess.returncode)))
        else:
            self._deviceProcess.kill()
            self.log("device server process needed to be killed")

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
        instrument = FakeInstrument()
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
