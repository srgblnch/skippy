# -*- coding: utf-8 -*-
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

from .features import RampFeature, RawDataFeature, ArrayDataInterpreterFeature
import PyTango
from .abstracts import AbstractSkippyAttribute
from time import time
import traceback

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class SkippyAttribute(AbstractSkippyAttribute):
    def __init__(self, type, dim, parent=None, withRawData=False,
                 *args, **kwargs):
        super(SkippyAttribute, self).__init__(*args, **kwargs)
        self._type = type
        self._dim = dim
        self._parent = parent
        if withRawData:
            self._raw = RawDataFeature(name="rawdata", parent=self)
        else:
            self._raw = None
        if self.dim == 1:
            if not hasattr(self, '_raw') or not self._raw:
                self._raw = RawDataFeature(name="rawdata", parent=self)
            # FIXME: format, origin, increment
            format = 'WaveformDataFormat'
            origin = 'WaveformOrigin'
            increment = 'WaveformIncrement'
            self._interpreter = \
                ArrayDataInterpreterFeature(name="array", parent=self,
                                            rawObj=self._raw, format=format,
                                            origin=origin, increment=increment)

    @property
    def type(self):
        return self._type

    @property
    def dim(self):
        return self._dim

    def isWritable(self):
        return False

    def isRampeable(self):
        return False

    def hasWriteValues(self):
        return False

    def hasRawData(self):
        if self._raw is None:
            return False
        return True

# Those method are in the superclass AbstractSkippyObj
#     def get_state(self):
#         if self._parent is not None and\
#                 hasattr(self._parent, 'get_state'):
#             return self._parent.get_state()
# 
#     def change_state_status(self, *args, **kwargs):
#         if self._parent is not None and\
#                 hasattr(self._parent, 'change_state_status'):
#             self._parent.change_state_status(*args, **kwargs)

    def _buildrepr_(self, attributes):
        repr = "%s (%s):\n" % (self.name, self.__class__.__name__)
        for key in attributes:
            if hasattr(self, key):
                attr = getattr(self, key)
                if attr is None:
                    repr += "\t%s: None\n" % (key)
                elif isinstance(attr, list) and len(attr) == 0:
                    repr += "\t%s: []\n" % (key)
                elif isinstance(attr, str):
                    repr += "\t%s: %r\n" % (key, attr)
                elif hasattr(attr, '__call__'):
                    args = [0]*attr.__code__.co_argcount
                    repr += "\t%s: %r\n" % (key, attr(*args))
                else:
                    repr += "\t%s: %s\n" % (key, attr)
            else:
                self.debug_stream("In _buildrepr_() doesn't have %s" % (key))
        return repr

# FIXME: it doesn't work as expected
#     def _buildRawFunctionality(self):
#         self._raw = RawDataFeature("rawdata", self)
#         self._makeRawDataProperties()
#
#     def _makeRawDataProperties(self):
#         setattr(self, 'lastReadRaw', self._makeLastReadRawProperty())
#
#     def _makeLastReadRawProperty(self):
#         def getter(self):
#             return self._raw.lastReadRaw
#
#         def setter(self, value):
#             self._raw.lastReadRaw = value
#
#         return property(getter, setter)

    def interpretArray(self):
        if self._interpreter:
            return self._interpreter.interpretArray()


class SkippyReadAttribute(SkippyAttribute):
    def __init__(self, readCmd, readFormula=None,
                 *args, **kwargs):
        super(SkippyReadAttribute, self).__init__(*args, **kwargs)
        self._readCmd = readCmd
        self._readFormula = readFormula
        self._lastReadValue = None
        self._timestamp = None
        self._quality = PyTango.AttrQuality.ATTR_INVALID

    def __str__(self):
        return "%s (%s) [%s, %s, %s]" % (self.name, self.__class__.__name__,
                                         self.rvalue, self.timestamp,
                                         self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'timestamp', 'quality', 'dim',
                                 'readCmd', 'readFormula'])

    @property
    def readCmd(self):
        return self._readCmd

    def _doHardwareRead(self, query):
        if self._parent is not None and hasattr(self._parent,
                                                'doHardwareRead'):
            return self._parent.doHardwareRead(query)

    @property
    def readFormula(self):
        return self._readFormula

    @property
    def rvalue(self):
        # TODO: check if has to be read from cache
        newReadValue = self._doHardwareRead(self.readCmd)
        t = time()
        if self._readFormula:
            self.debug_stream("Evaluating %r with VALUE=%r"
                              % (self._readFormula, newReadValue))
            try:
                formula = self._readFormula.replace("VALUE", "%r"
                                                    % newReadValue)
                self.debug_stream("eval(%r)" % (formula))
                return eval(formula)
            except Exception as e:
                self.warn_stream("Exception evaluating formula: %s" % (e))
        else:
            try:
                if self.type in [PyTango.DevDouble, PyTango.DevFloat]:
                    if self.dim == 0:
                        self._lastReadValue = float(newReadValue)
                    elif self.dim == 1:
                        self._raw.lastReadRaw = newReadValue
                        self._lastReadValue = self.interpretArray()
                    else:
                        raise BufferError("Unsuported multidimensional data")
                elif self.type in [PyTango.DevShort, PyTango.DevUShort,
                                   PyTango.DevInt, PyTango.DevLong,
                                   PyTango.DevULong, PyTango.DevLong64,
                                   PyTango.DevULong64]:
                    self._lastReadValue = int(newReadValue)
                elif self.type in [PyTango.DevBoolean]:
                    self._lastReadValue = bool(newReadValue)
            except Exception as e:
                self.error_stream("Exception converting string to "
                                  "type %s (dim %s): %s"
                                  % (self.type, self.dim, e))
                traceback.print_exc()
                return None
        self.timestamp = t
        if self._lastReadValue is not None:
            self.quality = PyTango.AttrQuality.ATTR_VALID
            return self._lastReadValue
        self.quality = PyTango.AttrQuality.ATTR_INVALID

    @property
    def lastReadValue(self):
        return self._lastReadValue

    @lastReadValue.setter
    def lastReadValue(self, value):
        self._lastReadValue = value

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        self._quality = value


class SkippyReadWriteAttribute(SkippyReadAttribute):
    # FIXME: this class is getting dirty due to the ramp: too many specific
    #        methods when the ramp should be encapsulated apart.
    def __init__(self, writeCmd=None, writeFormula=None, rampeable=False,
                 writeValues=None, *args, **kwargs):
        super(SkippyReadWriteAttribute, self).__init__(*args, **kwargs)
        self._writeCmd = writeCmd
        self._writeFormula = writeFormula
        self._lastWriteValue = None
        self._ramp = None
        if rampeable:
            self.makeRampeable()
        self._writeValues = writeValues

    def __str__(self):
        return "%s (%s) [(%s, %s), %s, %s]" % (self.name,
                                               self.__class__.__name__,
                                               self.rvalue, self.wvalue,
                                               self.timestamp, self.quality)

    def __repr__(self):
        return self._buildrepr_(['rvalue', 'wvalue', 'timestamp', 'quality',
                                 'dim', 'readCmd', 'readFormula', 'writeCmd',
                                 # 'writeFormula'
                                 ])

    def isWritable(self):
        return True

    def hasWriteValues(self):
        return self._writeValues is not None

    @property
    def writeCmd(self):
        return self._writeCmd

    def _doHardwareWrite(self, cmd):
        if self._parent is not None and\
                hasattr(self._parent, 'doHardwareWrite'):
            self._parent.doHardwareWrite(cmd)

    @property
    def writeFormula(self):
        return self._writeFormula

    @property
    def wvalue(self):
        return self._lastWriteValue

    @property
    def lastWriteValue(self):
        return self._lastWriteValue

    @lastWriteValue.setter
    def lastWriteValue(self, value):
        self._lastWriteValue = value

    def isRampeable(self):
        if self._ramp is None:
            return False
        return True

    def makeRampeable(self):
        if self._ramp is None:
            self._ramp = RampFeature(name="ramp", parent=self)

    def getRampObj(self):
        return self._ramp

    @property
    def writeValues(self):
        return self._writeValues

    def setWriteValues(self, writeValues):
        self._writeValues = writeValues
