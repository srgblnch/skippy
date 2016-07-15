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

Attribute('State',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:DISPlay?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: ":%s%d:DISPlay %s"
                                        % (ch, num, 'ON' if value else 'OFF')),
           'channels': True,
           'functions': True,
           'manager': True,
           })

Attribute('Impedance',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:INPut?" % (ch, num),
           'channels': True,
           })

Attribute('Amplitude',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VAMP? %s%d" % (ch, num),
           'channels': True,
           'functions': True,
           })

Attribute('Scale',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:SCALe?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: ":%s%d:SCALe %s"
                                        % (ch, num, value)),
           'channels': True,
           })

Attribute('Offset',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":%s%d:OFFS?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: ":%s%d:OFFS %s"
                                        % (ch, num, value)),
           'channels': True,
           })

Attribute('VPeakToPeak',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VPP? %s%d" % (ch, num),
           'channels': True,
           'functions': True,
           })

Attribute('VoltageMin',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VMIN? %s%d" % (ch, num),
           'channels': True,
           'functions': True,
           })

Attribute('VoltageMax',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VMAX? %s%d" % (ch, num),
           'channels': True,
           'functions': True,
           })

Attribute('VoltageUpper',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VUPPER? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('VoltageLower',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:VLOWER? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('Frequency',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:FREQ? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('Period',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:PERIOD? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('RiseTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:RISETIME? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('FallTime',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:FALLTIME? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('OverShoot',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:OVERSHOOT? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('PreShoot',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': lambda ch, num: ":MEAS:PRESHOOT? %s%d" % (ch, num),
           'channels': True,
           })

Attribute('Waveform',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [1, 40000000],
           'readCmd': lambda ch, num: ":WAVeform:SOURce %s%d;:WAVeform:DATA?"
                                      % (ch, num),
           'channels': True,
           'functions': True,
           })

Attribute('CurrentSampleRate',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":ACQuire:SRATe?",
           })

Attribute('ScaleH',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":TIMebase:SCALe?",
           'writeCmd': lambda value: ":TIMebase:SCALe %s" % (str(value)),
           })

Attribute('OffsetH',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":TIMebase:POS?",
           'writeCmd': lambda value: ":TIMebase:POS %s" % (str(value)),
           })

Attribute('TriggerType',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":TRIGger:MODE?",
           'writeCmd': lambda value: ":TRIGger:MODE %s" % (str(value)),
           })

Attribute('AcquisitionMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":ACQuire:MODE?",
           'writeCmd': lambda value: ":ACQuire:MODE %s" % (str(value)),
           })

Attribute('AcquisitonPoints',
          {'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': ":ACQuire:POINts?",
           'writeCmd': lambda value: ":ACQuire:POINts %s" % (str(value)),
           })

Attribute('WaveformDataFormat',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":waveform:format?",
           'writeCmd': lambda value: ":waveform:format %s" % (str(value)),
           'writeValues': ['BYTE', 'BYT',
                           'WORD', 'WOR',
                           'ASCII', 'ASCI', 'ASC'],
           })

Attribute('WaveformOrigin',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":WAVeform:YORigin?",
           })

Attribute('WaveformIncrement',
          {'type': PyTango.CmdArgType.DevDouble,
           'format': '%9.6f',
           'dim': [0],
           'readCmd': ":WAVeform:YINCrement?",
           })

Attribute('ByteOrder',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":WAVeform:BYTeorder?",
           'writeCmd': lambda value: ":WAVeform:BYTeorder %s" % (str(value)),
           'writeValues': ['LSBF', 'MSBF'],
           'memorized': True,
           })

Attribute('Error',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': ":SYSTem:ERRor?",
           })

Attribute('Lock',
          {'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "SYSTem:LOCK?",
           'writeCmd': lambda value: "SYSTem:LOCK %s" % (str(value)),
           'memorized': True,
           })
