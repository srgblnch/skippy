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

__author__ = "Manuel Broseta Sebastia"
__maintainer__ = "Antonio Milan Otero"
__email__ = "mbroseta@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


Attribute('Mac',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*MAC?",
           })

# IO Port functions ---
Attribute('IOCONFIG',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda mult, num: "%s%.2d:CONFI?" % (mult, num),
           'writeCmd': lambda mult, num: (lambda value: "%s%d:CONFI %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': 'IOPOrt', 'attrSuffix': 'Port'}
           })
Attribute('IO',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda mult, num: "%s%.2d:VALU?" % (mult, num),
           'writeCmd': lambda mult, num: (lambda value: "%s%.2d:VALU %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': 'IOPOrt', 'attrSuffix': 'Port'}
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

Attribute('NTrig',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "ACQU:NTRIggers?",
           'writeCmd': lambda value: "ACQU:NTRIggers %s" % (value),
           })

# Channels ---
Attribute('InstantCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:INSCurrent?" % (ch, num),
           'channels': True
           })
Attribute('Current',
          {'type': PyTango.CmdArgType.DevString,
           # FIXME: DevString? should it be an array of doubles?
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CURRent?" % (ch, num),
           'channels': True
           })
Attribute('AverageCurrent',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:AVGCurrent?" % (ch, num),
           'channels': True
           })
Attribute('CARange',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:RANGE?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:RANGE %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CAFilter',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:FILT?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:FILT %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CAPostFilter',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:POST?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:POST %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CAPreFilter',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:PREF?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:PREF %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CAInversion',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:INVE?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:INVE %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CATIGain',
          {'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:TIGA?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:TIGA %s"
                                        % (ch, num, value)),
           'channels': True
           })
Attribute('CAVGain',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:VGAI?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:CABO:VGAI %s"
                                        % (ch, num, value)),
           'channels': True
           })

Attribute('AOUT',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:AOUT?" % (ch, num),
           'writeCmd': lambda ch, num: (lambda value: "%s%.2d:AOUT %s"
                                        % (ch, num, value)),
           'channels': True
           })

Attribute('CATemp',
          {'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': lambda ch, num: "%s%.2d:CABO:TEMP?" % (ch, num),
           'channels': True
           })
