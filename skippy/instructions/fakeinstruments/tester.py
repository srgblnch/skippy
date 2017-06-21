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
__status__ = "Development"

import PyTango

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

# Attribute('short_spectrum_ro',
#           {'type': PyTango.CmdArgType.DevDouble,
#            'format': '%9.6f',
#            'dim': [1, 40000000],
#            'readCmd': "source:readable:array:short:value?",
#            })

# Attribute('WaveformDataFormat',
#           {'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': ":waveform:format?",
#            'writeCmd': lambda value: ":waveform:format %s" % (str(value)),
#            'writeValues': ['BYTE', 'BYT',
#                            'WORD', 'WOR',
#                            'ASCII', 'ASCI', 'ASC'],
#            })
