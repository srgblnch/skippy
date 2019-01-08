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

Attribute('AcqMode',
          {'description': 'Acquisition Mode:\n'
                          '0: CountMode\n'
                          '1: TOFMode\n'
                          '2: AnalogSingleEnded\n'
                          '3: AnalogSummation',
           'type': PyTango.CmdArgType.DevString,
           'dim': [0],
           'readCmd': "CONFigure:ACQUisition:MODE?",
           'writeCmd': lambda value: "CONFigure:ACQUisition:MODE %s" % (value),
           # TODO: improve this set of valid values
           'writeValues': ['CountMode', 'TOFMode',
                           'AnalogSingleEnded', 'AnalogSummation']
           })

# Attribute('IntTime',
#           {'description': 'Number of seconds to integrate counts',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': "CONFigure:COUNt:INTTime?",
#            'writeCmd': lambda value: "CONFigure:COUNt:INTTime %s" % (value),
#            })

# Attribute('CountRate',
#           {'description': 'Counts refreshment rate in seconds',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': "CONFigure:COUNt:RATE?",
#            'writeCmd': lambda value: "CONFigure:COUNt:RATE %s" % (value),
#            })

# Attribute('Count',
#           {'description': 'Actual count value for SiPM 1-4',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': lambda mult, num: "ACQUire:COUNt:CHANnel%s%.2d:VALUe?"
#                                         % (mult, num),
#            'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
#            })

# Attribute('CountInt',
#           {'description': 'Integrated counts value for SiPM 1-8',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': lambda mult, num:
#            "ACQUire:COUNt:CHANnel%s%.2d:INTEgrated?" % (mult, num),
#            'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
#            })

# Attribute('C_EnablePM',
#           {'description': 'Enable/Disable SiPM 1-4',
#            'type': PyTango.CmdArgType.DevBoolean,
#            'dim': [0],
#            'readCmd': lambda mult, num:
#            # "CONFigure:ENABle:SIPM%s%.2d:VALUe?" % (mult, num),
#            "CONFigure:CHANnel%sa%.2d:ENABle?",
#            'writeCmd': lambda mult, num:
#            (lambda value:
#             # "CONFigure:ENABle:SIPM%s%.2d:VALUe %s" % (mult, num, value)),
#             "CONFigure:CHANnel%sa%.2d:ENABle %s" % (mult, num, value)),
#            'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
#            })

# # FIXME: merge those to multiple
# Attribute('TOF1Mode',
#           {'description': 'Configuration of SiPM for TOF measurements:\n'
#                           '0: Ch1-Ch2\n1: Ch1-Ch3\n2: Ch1-Ch4\n'
#                           '3: Ch2-Ch1\n4: Ch3-Ch1\n5: Ch4-Ch1\n'
#                           '6: Ch1-Ch3\n7: Ch2-Ch4\n8: Ch3-Ch2\n'
#                           '9: Ch4-Ch2\n10: Ch3-Ch4\n11: Ch4-Ch3',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': "CONFigure:TOF1:MODE?",
#            'writeCmd': lambda value: "CONFigure:TOF1:MODE %s" % (value)
#            })
#
# Attribute('TOF2Mode',
#           {'description': 'Configuration of SiPM for TOF measurements:\n'
#                           '0: Ch1-Ch2\n1: Ch1-Ch3\n2: Ch1-Ch4\n'
#                           '3: Ch2-Ch1\n4: Ch3-Ch1\n5: Ch4-Ch1\n'
#                           '6: Ch1-Ch3\n7: Ch2-Ch4\n8: Ch3-Ch2\n'
#                           '9: Ch4-Ch2\n10: Ch3-Ch4\n11: Ch4-Ch3',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': "CONFigure:TOF2:MODE?",
#            'writeCmd': lambda value: "CONFigure:TOF2:MODE %s" % (value)
#            })

# Attribute('ToF',
#           {'description': 'Time-of-Flight value',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': lambda mult, num:
#            "ACQUire:TOF%s%.2d:VALUe?" % (mult, num),
#            'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
#            })

# Attribute('C_SumSiPM',
#           {'description': 'Use SiPM for sumation',
#            'type': PyTango.CmdArgType.DevBoolean,
#            'dim': [0],
#            'readCmd': lambda mult, num:
#            "CONFigure:SUMMation%s%.2d:VALUe?" % (mult, num),
#            'writeCmd': lambda mult, num:
#            (lambda value:
#             "CONFigure:SUMMation%s%.2d:VALUe %s" % (mult, num, value)),
#            'multiple': {'scpiPrefix': '', 'attrSuffix': ''}
#            })

# Attribute('C_Threshold',
#           {'description': 'Voltage threshold at comparator for SiPM',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': lambda mult, num:
#            "CONFigure:VOLTage:THREs%s%.2d:VALUe?" % (mult, num),
#            'writeCmd': lambda mult, num:
#            (lambda value:
#             "CONFigure:VOLTage:THREs%s%.2d:VALUe %s" % (mult, num, value)),
#            })

# Attribute('DCRwindow',
#           {'description': 'DRC analisys window (sec)',
#            'type': PyTango.CmdArgType.DevULong,
#            'dim': [0],
#            'readCmd': "CONFigure:DCR:WINDow?",
#            'writeCmd': lambda value: "CONFigure:DCR:WINDow %s" % (value)
#            })

# Attribute('DCRThLow',
#           {'description': 'DCR sweep lower Vth level',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': "CONFigure:DCR:THREshold:LOW?",
#            'writeCmd': lambda value:
#            "CONFigure:DCR:THREshold:LOW %s" % (value),
#            })

# Attribute('DCRThHigh',
#           {'description': 'DCR sweep higher Vth level',
#            'type': PyTango.CmdArgType.DevString,
#            'dim': [0],
#            'readCmd': "CONFigure:DCR:THREshold:HIGH?",
#            'writeCmd': lambda value:
#            "CONFigure:DCR:THREshold:HIGH %s" % (value),
#            })




# Attribute('',
#           {'description': '',
#            'type': PyTango.CmdArgType,
#            'dim': [0],
#            'readCmd': "",
#            })
