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
import scpi
import skippy
import traceback


DevName = 'fake/skyppy/instrument'
DevClass = 'Skippy'
DevServer = 'Skippy/FakeInstrument'


class FakeInstrument(object):
    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        self._identity = InstrumentIdentification('ALBA', 'FakeInstrument', 0,
                                                  skippy.version())
        self._scpiObj = scpi.scpi(local=True)
        self._scpiObj.addSpecialCommand('IDN', self._identity.idn)
        # Prepare ...
        self._scpiObj.open()


def createTestDevice():
    tangodb = PyTango.Database()
    print("\nCreating a %s device in %s:%s"
          % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
    devInfo = PyTango.DbDevInfo()
    devInfo.name = DevName
    devInfo._class = DevClass
    devInfo.server = DevServer
    tangodb.add_device(devInfo)
    print("Server %s added" % DevServer)
    propertyName = 'Instrument'
    propertyValue = 'localhost'
    property = PyTango.DbDatum(propertyName)
    property.value_string.append(propertyValue)
    print("Set property %s: %s" % (propertyName, propertyValue))
    tangodb.put_device_property(DevName, property)
    # TODO: run the device server to be tested


def deleteTestDevice():
    try:
        tangodb = PyTango.Database()
        print("\nRemove a %s device in %s:%s"
              % (DevName, tangodb.get_db_host(), tangodb.get_db_port()))
        tangodb.delete_device(DevName)
        tangodb.delete_server(DevServer)
    except Exception as e:
        print("\n* Deletion failed, please review manually for garbage *\n")


def main():
    instrument = FakeInstrument()
    try:
        createTestDevice()
    except Exception as e:
        print("Cannot complete the test: %s" % e)
        traceback.print_exc()
    finally:
        deleteTestDevice()


if __name__ == '__main__':
    main()
