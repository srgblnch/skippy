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

import os
from skippylib import Builder
import traceback

__author__ = "Sergi Blanch-Torne"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"


def identifier(idn, deviceObj):
    '''This method has been designed to understand from the answer of an
       instrument to the '*IDN?' command, what is the correct object that
       contains the set of commands for this instrument.
    '''
    company, model = splitIDN(idn)
    file = {'agilent technologies': agilent,
            'tektronix': tektronix,
            'rohde&schwarz': rohdeschwarz,
            'arroyo': arroyo,
            'albasynchrotron': albasynchrotron,
            'keithley instruments inc.': keithley,
            'fakeinstruments. inc': fakeinstrument,
            }[company](model)
    builder = Builder(deviceObj)
    builder.parseFile(file)
    return builder


def splitIDN(idn):
    # Only company and model in use. Perhaps one day the firmware version
    # would be useful but not found the case by now.
    idn = idn.strip().lower()
    if idn.count(',') == 3:
        separator = ','
    elif idn.count(' ') == 3:
        separator = ' '
    else:
        raise SyntaxError("Could not identify the separator in %r" % (idn))
    try:
        company, model, rest = idn.split(separator, 2)
        company = company.strip()
        model = model.strip()
        return company, model
    except Exception as e:
        raise SyntaxError("Could not identify the manufacturer and model "
                          "in %r" % (idn))


def _getFilePath(filename):
    path = os.path.dirname(__file__)
    full_path = os.path.join(path, filename)
    return full_path


#################################
# supported companies methods ---
def agilent(model):
    if model.startswith('dso'):
        return _getFilePath("instructions/scope/agilentDSO.py")
    elif model.startswith('n5171'):
        return _getFilePath("instructions/radioFrequencyGenerator/"
                            "keysightSignalGenerator.py")
    raise EnvironmentError("Agilent %s model not supported" % (model))


def tektronix(model):
    if model.startswith('dpo'):
        return _getFilePath("instructions/scope/tektronixDPO.py")
    elif model.upper().startswith('AFG'):
        return _getFilePath("instructions/arbitraryFunctionGenerator/"
                            "tektronicsAFG.py")
    raise EnvironmentError("Tektronix %s model not supported" % (model))


def rohdeschwarz(model):
    if model == 'sma100a':
        return _getFilePath("instructions/radioFrequencyGenerator/"
                            "rohdeSchwarzRFG.py")
    elif model.lower() == 'fsp-3':
        return _getFilePath("instructions/spectrumAnalyser/rohdeSchwarzFSP.py")
    raise EnvironmentError("Rohde&Schwarz %s model not supported" % (model))


def arroyo(model):
    if model == '5300':
        return _getFilePath("instructions/temperatureController/arroyo5300.py")
    raise EnvironmentError("Arroyo %s model not supported" % (model))


def albasynchrotron(model):
    if model == 'electrometer2':
        return _getFilePath('instructions/albaEm/albaEm.py')
    raise EnvironmentError("Alba Synchrotron %s model not supported" % (model))


def keithley(model):
    if model == 'model 2000':
        return _getFilePath("instructions/multimeter/keithley2000.py")
    elif model in ['model 2635a', 'model 2611']:
        return _getFilePath("instructions/sourcemeter/keithley26XX.py")
    raise EnvironmentError("Keithley %s model not supported" % (model))


def fakeinstrument(model):
    if model == 'tester':
        return _getFilePath("instructions/fakeinstruments/tester.py")
    raise EnvironmentError("Fake Instrument %s model not supported" % (model))
# done supported companies methods
##################################


