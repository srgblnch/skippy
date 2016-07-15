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
import scpi
import skippy


class FakeInstrument(object):
    def __init__(self, *args, **kwargs):
        super(FakeInstrument, self).__init__(*args, **kwargs)
        identity = InstrumentIdentification('ALBA', 'test', 0,
                                            skippy.version())
        self._scpiObj = scpi.scpi(local=True)
        self._scpiObj.addSpecialCommand('IDN', identity.idn)


def main():
    instrument = FakeInstrument()


if __name__ == '__main__':
    main()
