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


from instrIdn import InstrumentIdentification
import PyTango
import signal
import scpi
from select import select
import skippy
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

    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._buildFakeSCPI()

    def _buildFakeSCPI(self):
        self._identity = InstrumentIdentification('FakeInstruments. Inc',
                                                  'IDNonly', 0,
                                                  skippy.version())
        self._scpiObj = scpi.scpi(local=True)
        self._buildSpecialCommands()
        self._buildNormalCommands()
        self._scpiObj.open()

    def _buildSpecialCommands(self):
        self._scpiObj.addSpecialCommand('IDN', self._identity.idn)

    def _buildNormalCommands(self):
        pass


def createTestDevice():
    tangodb = PyTango.Database()
    print("\nCreating a %s device in %s:%s"
          % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
    devInfo = PyTango.DbDevInfo()
    devInfo.name = DevName
    devInfo._class = DevClass
    devInfo.server = DevServer+"/"+DevInstance
    tangodb.add_device(devInfo)
    print("Server %s added" % (DevServer+"/"+DevInstance))
    propertyName = 'Instrument'
    propertyValue = 'localhost'
    property = PyTango.DbDatum(propertyName)
    property.value_string.append(propertyValue)
    print("Set property %s: %s" % (propertyName, propertyValue))
    tangodb.put_device_property(DevName, property)


def startTestDevice():
    process = Popen([DevServer, DevInstance])
    print("Launched the device server has pid %d" % (process.pid))
    return process


def stopTestDevice():
    process.terminate()
    sleep(1)
    if process.poll() is not None:
        print("device server process %d terminated (signal %d)"
              % (process.pid, abs(process.returncode)))
    else:
        process.kill()
        print("device server process needed to be killed")


def deleteTestDevice():
    try:
        tangodb = PyTango.Database()
        print("\nRemove a %s device in %s:%s"
              % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
        tangodb.delete_device(DevName)
        tangodb.delete_server(DevServer+"/"+DevInstance)
    except Exception as e:
        print("\n* Deletion failed, please review manually for garbage *\n")


def signalHandler(signum, frame):
    if signum == signal.SIGINT:
        print("\nCaptured a Ctrl+c: terminating the execution...")
        stopTestDevice()
        deleteTestDevice()
        sys.exit(0)
    else:
        print("Unmanaged signal received (%d)" % (signum))


def main():
    instrument = FakeInstrument()
    try:
        createTestDevice()
        global process
        process = startTestDevice()
        signal.signal(signal.SIGINT, signalHandler)
        print("\n\tPress Ctrl+c to finish the fake device")
        signal.pause()
    except Exception as e:
        print("\nCannot complete the test: %s\n" % e)
        traceback.print_exc()
        stopTestDevice()
        deleteTestDevice()


if __name__ == '__main__':
    main()
