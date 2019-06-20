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

import PyTango

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Development"


Attribute("boolean_scalar_ro",
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': 'source:readable:boolean:value?'})

Attribute("short_scalar_ro",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "source:readable:short:value?"})

Attribute("short_scalar_rw",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "source:writable:short:value?",
           'writeCmd': lambda value: "source:writable:short:value %s"
           % (value)})

Attribute("float_scalar_ro",
          {'type': PyTango.CmdArgType.DevFloat,
           'dim': [0],
           'readCmd': "source:readable:float:value?"})

Attribute("float_scalar_rw",
          {'type': PyTango.CmdArgType.DevFloat,
           'dim': [0],
           'readCmd': "source:writable:float:value?",
           'writeCmd': lambda value: "source:writable:float:value %s"
           % (value)})

# Test rampeable attributes ---
Attribute('Rampeable',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "rampeable?",
           'writeCmd': lambda value: "rampeable %s" % (str(value)),
           'rampeable': True,
           'memorized': True,
           })

Attribute("Fallible",
          {'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': "fallible?"})

# TODO: not yet implemented
# Attribute('boolean_spectrum_ro',
#           {'type': PyTango.CmdArgType.DevBoolean,
#            'dim': [1, 40000000],
#            'readCmd': "source:readable:array:boolean:value?",
#            })

# TODO: not yet implemented
# Attribute('short_spectrum_ro',
#           {'type': PyTango.CmdArgType.DevFloat,
#            'format': '%9.6f',
#            'dim': [1, 40000000],
#            'readCmd': "source:readable:array:short:value?",
#            })

# FIXME: generalise this attrName and specify in the spectrum attr
Attribute('WaveformDataFormat',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "dataformat?",
           'writeCmd': lambda value: "dataformat %s" % (str(value)),
           'writeValues': ['BYTE', 'BYT',
                           'WORD', 'WOR',
                           'ASCII', 'ASCI', 'ASC'],
           })
