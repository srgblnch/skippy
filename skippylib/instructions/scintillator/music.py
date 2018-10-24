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

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Pre-Alpha"


import PyTango

Attribute('MAC',
          {'description': 'MAC address',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*MAC?",
           })

Attribute('IP',
          {'description': 'IP address set by the DHCP',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*IP?",
           })

Attribute('MusicStatus',
          {'description': 'MUSIC status:\n'
                          '- idle\n- working:mode\n- error:mode',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "*STS?",
           })

Attribute('AcqMode',
          {'description': 'Acquisition Mode:\n1: Analog\n2: Digital',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "CONFigure:ACQUisition:MODE?",
           'writeCmd': lambda value: "CONFigure:ACQUisition:MODE %s" % (value),
           'writeValues': ['ANALOG', 'DIGITAL']
           })

Attribute('IntTime',
          {'description': 'Number of seconds to integrate counts',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': "CONFigure:COUNt:INTTime?",
           'writeCmd': lambda value: "CONFigure:COUNt:INTTime %s" % (value),
           })

Attribute('CountRate',
          {'description': 'Counts refreshment rate in s',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CONFigure:COUNt:RATE?",
           'writeCmd': lambda value: "CONFigure:COUNt:RATE %s" % (value),
           })

Attribute('Count',
          {'description': 'Actual count value for SiPM 1-8',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': lambda mult, num: "ACQUire:COUNt%s%.2d:VALUe?"
                                        % (mult, num),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           })

Attribute('CountInt',
          {'description': 'Integrated counts value for SiPM 1-8',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': lambda mult, num: "ACQUire:COUNt%s%.2d:INTEgrated?"
                                        % (mult, num),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           })

Attribute('EnableCh',
          {'description': 'Enable/Disable channel 1-8',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:CHANnel%s%.2d:ENABle?"
                                        % (mult, num),
           'writeCmd': lambda mult, num: (lambda value:
                                          "CONFigure:CHANnel%s%d:ENABle %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           })

Attribute('EnableSe',
          {'description': 'Enable/Disable single ended input for channel 1-8',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:CHANnel%s%.2d:SE?"
                                        % (mult, num),
           'writeCmd': lambda mult, num: (lambda value:
                                          "CONFigure:CHANnel%s%d:SE %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           })

Attribute('EnableSum',
          {'description': 'Enable/Disable summation for channel 1-8',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:CHANnel%s%.2d:SUMMation?"
                                        % (mult, num),
           'writeCmd': lambda mult, num: (lambda value:
                                          "CONFigure:CHANnel%s%d:SUMMation %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           })

Attribute('C_VThres',
          {'description': 'Voltage threshold. Possible values are [0, 511]',
           'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:CHANnel%s%.2d:VTHReshold?"
                                        % (mult, num),
           'writeCmd': lambda mult, num: (lambda value:
                                          "CONFigure:CHANnel%s%d:VTHReshold %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           # 'min': 0, 'max': 511
           })

Attribute('C_Voff',
          {'description': 'Voltage offset. Possible values are [0, 255]',
           'type': PyTango.CmdArgType.DevShort,
           'dim': [0],
           'readCmd': lambda mult, num: "CONFigure:CHANnel%s%.2d:VOFFset?"
                                        % (mult, num),
           'writeCmd': lambda mult, num: (lambda value:
                                          "CONFigure:CHANnel%s%d:VOFFset %s"
                                          % (mult, num, value)),
           'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
           # 'min': 0, 'max': 255
           })

Attribute('C_VBG',
          {'description': 'Coarse voltage reference. '
                          'Possible values are [0, 7]',
           'type': PyTango.CmdArgType.DevUChar,
           'dim': [0],
           'readCmd': "CONFigure:VBG?",
           'writeCmd': lambda value: "CONFigure:VBG %s" % (value),
           # 'min': 0, 'max': 7
           })

Attribute('PoleZeroEnable',
          {'description': 'Enable pole zero cancellation',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:ENABle?",
           'writeCmd': lambda value: "CONFigure:POLEzero:ENABle %s" % (value),
           })

Attribute('PoleZeroR',
          {'description': 'Pole zero resistance ladder. '
                          'Possible values are [0, 7]',
           'type': PyTango.CmdArgType.DevUChar,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:RESIstance?",
           'writeCmd': lambda value: "CONFigure:POLEzero:RESIstance %s"
                                     % (value),
           # 'min': 0, 'max': 7
           })

Attribute('PoleZeroC',
          {'description': 'Pole zero capacitance ladder. '
                          'Possible values are [0, 31]',
           'type': PyTango.CmdArgType.DevUChar,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:CAPAcitance?",
           'writeCmd': lambda value: "CONFigure:POLEzero:CAPAcitance %s"
                                     % (value),
           # 'min': 0, 'max': 31
           })

Attribute('PoleZeroAtt',
          {'description': 'Pole zero low atten ladder',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:POLEzero:ATTEn?",
           'writeCmd': lambda value: "CONFigure:POLEzero:ATTEn %s"
                                     % (value),
           })

Attribute('C_HighGain',
          {'description': 'Enable high gain transimpedance mode',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:HIGHgain:ENABle?",
           'writeCmd': lambda value: "CONFigure:HIGHgain:ENABle %s"
                                     % (value),
           })

Attribute('TS_ThresholdsBest',
          {'description': 'Fine tine of threshold per channel',
           'type': PyTango.CmdArgType.DevLong,
           'dim': [1, 8],
           'readCmd': "ACQUire:THREshold?",
           })

Attribute('TS_VBGBest',
          {'description': 'Global coarse tune of threshold',
           'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': "ACQUire:THREshold:VBG?",
           })

Attribute('TS_DutyWindow',
          {'description': 'Threshold Scan DutyWindow for actual count',
           'type': PyTango.CmdArgType.DevLong,
           'dim': [0],
           'readCmd': "CONFigure:THREshold:WINDow?",
           'writeCmd': lambda value: "CONFigure:THREshold:WINDow %s" % (value),
           })

Attribute('TOFtime',
          {'description': 'Acquisition time in milliseconds',
           'type': PyTango.CmdArgType.DevULong,
           'dim': [0],
           'readCmd': "CONFigure:TOF:TIME?",
           'writeCmd': lambda value: "CONFigure:TOF:TIME %s" % (value)
           })

Attribute('HVenable',
          {'description': 'High voltage font enable',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "CONFigure:HV:ENABle?",
           'writeCmd': lambda value: "CONFigure:HV:ENABle %s" % (value)
           })

Attribute('HVvoltageSetpoint',
          {'description': 'Voltage level [0..90]V',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "CONFigure:HV:VOLTage?",
           'writeCmd': lambda value: "CONFigure:HV:VOLTage %s" % (value)
           # 'min': 0, 'max': 90
           })

Attribute('HVvoltage',
          {'description': 'Output voltage',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "DIAGnostics:HV:VOLTage?",
           })

Attribute('HVCurrent',
          {'description': 'Output current in mA',
           'type': PyTango.CmdArgType.DevDouble,
           'dim': [0],
           'readCmd': "DIAGnostrics:HV:CURRent?",
           })

Attribute('HVoverCurrent',
          {'description': 'Current output beyond safe levels',
           'type': PyTango.CmdArgType.DevBoolean,
           'dim': [0],
           'readCmd': "DIAGnostics:HV:OVERcurrent",
           })
