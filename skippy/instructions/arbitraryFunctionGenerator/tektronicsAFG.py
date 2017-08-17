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

Attribute('State',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":OUTPut%d:STATE?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":OUTPut%d:STATE %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('ModulationAM',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:am:state?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":source%d:am:state %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('ModulationFM',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:fm:state?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":source%d:fm:state %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('ModulationFSK',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:fsk:state?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":source%d:fsk:state %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('ModulationPM',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":source%d:pm:state?" % (num),
           'writeCmd': lambda ch, num: (lambda value: ":source%d:pm:state %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('Function',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":SOURce%d:FUNCtion:SHAPe?" % (num),
           'writeCmd': lambda ch, num: (lambda value:
                                        ":SOURce%d:FUNCtion:SHAPe %s"
                                        % (num, value)),
           'channels': True
           })

Attribute('lock',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:KLOCk:STATe?",
           'writeCmd': lambda value: ":SYSTem:KLOCk:STATe %s" % (value)
           })

Attribute('click',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:KCLick:STATe?",
           'writeCmd': lambda value: ":SYSTem:KCLick:STATe %s" % (value)
           })

Attribute('beep',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': ":SYSTem:BEEPer:STATe?",
           'writeCmd': lambda value: ":SYSTem:BEEPer:STATe %s" % (value)
           })
