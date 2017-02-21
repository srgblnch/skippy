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

__author__ = "Manuel Broseta Sebastia"
__maintainer__ = "Antonio Milan Otero"
__email__ = "mbroseta@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


import PyTango

Attribute('Mac',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*MAC?",
           # 'writeCmd': lambda num: (lambda value: ":OUTPut%d:STATE %s"
           #                          %(num, value)),
           })

# IO Port functions ---
Attribute('IOCONFIG',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "IOPO%d:CONFI?",
           'writeCmd': lambda num: (lambda value: "IOPO%d:CONFI %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('IO',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "IOPO%d:VALU?",
           'writeCmd': lambda num: (lambda value: "IOPO%d:VALU %s"
                                    % (num, value)),
           'channels': True
           })

# Trigger Commands ---
Attribute('TriggerDelay',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:DELA?",
           'writeCmd': lambda value: "TRIG:DELA %s" % (value),
           })
Attribute('TriggerInput',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:INPU?",
           'writeCmd': lambda value: "TRIG:INPU %s" % (value),
           })
Attribute('TriggerMode',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:MODE?",
           'writeCmd': lambda value: "TRIG:MODE %s" % (value),
           })
Attribute('TriggerPolarity',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:POLA?",
           'writeCmd': lambda value: "TRIG:POLA %s" % (value),
           })
Attribute('SWTrigger',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "TRIG:SWSET?",
           'writeCmd': lambda value: "TRIG:SWSET %s" % (value),
           })

# Acquisition Commands ---
Attribute('AcqFilter',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:FILTER?",
           'writeCmd': lambda value: "ACQU:FILTER %s" % (value),
           })
Attribute('Meas',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:MEAS?",
           # 'writeCmd': lambda value: "ACQU:FILTER %s" % (value),
           })
Attribute('NData',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:NData?",
           # 'writeCmd': lambda value: "ACQU:FILTER %s" % (value),
           })
Attribute('AcqRange',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:RANGE?",
           'writeCmd': lambda value: "ACQU:RANGE %s" % (value),
           })
Attribute('AcqStart',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:START?",
           'writeCmd': lambda value: "ACQU:START %s" % (value),
           })
Attribute('AcqState',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:STATE?",
           # 'writeCmd': lambda value: "ACQU:FILTER %s" % (value),
           })
Attribute('AcqStop',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:STOP?",
           'writeCmd': lambda value: "ACQU:STOP %s" % (value),
           })
Attribute('AcqTime',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:TIME?",
           'writeCmd': lambda value: "ACQU:TIME %s" % (value),
           })

# Channels ---
Attribute('InstantCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:INSCurrent?",
           # 'writeCmd': lambda num: (lambda value: "DEBUg:ENABle %s"
           #                          % (value)),
           # FIXME: alert, this command doesn't use channel number
           'channels': True
           })
Attribute('Current',
          {'type': PyTango.CmdArgType.DevString,
           # FIXME: DevString? should it be an array of doubles?
           'dim': [0],
           'readCmd': "CHAN%d:CURRent?",
           # 'writeCmd': lambda num: (lambda value: "DEBUg:ENABle %s"
           #                          % (value)),
           # FIXME: alert, this command doesn't use channel number
           'channels': True
           })
Attribute('AverageCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:AVGCurrent?",
           # 'writeCmd': lambda num: (lambda value: "DEBUg:ENABle %s"
           #                          % (value)),
           # FIXME: alert, this command doesn't use channel number
           'channels': True
           })
Attribute('CARange',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:RANGE?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:RANGE %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CAFilter',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:FILT?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:FILT %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CAPostFilter',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:POST?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:POST %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CAPreFilter',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:PREF?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:PREF %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CAInversion',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:INVE?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:INVE %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CATIGain',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:TIGA?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:TIGA %s"
                                    % (num, value)),
           'channels': True
           })
Attribute('CAVGain',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CHAN%d:CABO:VGAI?",
           'writeCmd': lambda num: (lambda value: "CHAN%d:CABO:VGAI %s"
                                    % (num, value)),
           'channels': True
           })
