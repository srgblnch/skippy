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

####
# Example of attribute:
#
#   Attribute('name' -> name of the attribute
#             {'type' -> check the PyTango.CmdArgType
#              'dim'  -> can be: 0
#                               [1,X]
#                               [2,X,Y]
#              'channels' -> boolean to build attrs with a 'ch' suffix
#              'funtions' -> boolean to build attrs with a 'fn' suffix
#              'unit'     -> the unit of the tango attribute
#              'min','max'-> in writable attributes configure limits
#              'format'   -> in floats and integers the representation
#              'label'    -> attribute property
#              'description' -> attribute property
#              'memorized' -> attribute property
#              'writeValues' -> list of accepted values to write
#              'manager'  -> to flag if a channel is close to avoid reads there
#             }
#            )
#

Attribute('Center',
          {'type':PyTango.CmdArgType.DevDouble,
           'format':'%9.6f',
           'dim':[0],
           'readCmd':":FREQ:CENTER?"
         })

Attribute('Span',
          {'type':PyTango.CmdArgType.DevDouble,
           'format':'%9.6f',
           'dim':[0],
           'readCmd':":FREQ:SPAN?"
         })

Attribute('Bandwidth',
          {'type':PyTango.CmdArgType.DevDouble,
           'format':'%9.6f',
           'dim':[0],
           'readCmd':":BAND:RES?"
         })

Attribute('WaveformState',
          {'type':PyTango.CmdArgType.DevDouble,
           'format':'%9.6f',
           'dim':[0],
           'readCmd':":TRAC:IQ:?",
           'writeCmd':lambda value:":TRAC:IQ:STAT %s"%(str(value))
         })

Attribute('Waveform',
          {'type':PyTango.CmdArgType.DevDouble,
           'format':'%9.6f',
           'dim':[1,40000000],
           'readCmd':":TRAC:IQ:DATA?"
         })

