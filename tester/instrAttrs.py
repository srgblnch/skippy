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

from numpy.random import random, randint
#from numpy import random as nprandom


class FakeNumber(object):

    _value = None
    _upperLimit = None
    _lowerLimit = None

    def __init__(self, upperLimit=32768, lowerLimit=-32768, *args, **kwargs):
        super(FakeNumber, self).__init__(*args, **kwargs)
        self._upperLimit = upperLimit
        self._lowerLimit = lowerLimit

    def upperLimit(self, value=None):
        if value is None:
            return self._upperLimit
        self._upperLimit = int(value)

    def lowerLimit(self, value=None):
        if value is None:
            return self._lowerLimit
        self._lowerLimit = int(value)


# class FakeIntegerArray(FakeNumber):
# 
#     _samples = None
# 
#     def __init__(self, samples=10, *args, **kwargs):
#         super(FakeIntegerArray, self).__init__(*args, **kwargs)
#         self._samples = samples
# 
#     def samples(self, value=None):
#         if value is None:
#             return self._samples
#         self._samples = int(value)


class FakeInteger(FakeNumber):
    def __init__(self, *args, **kwargs):
        super(FakeInteger, self).__init__(*args, **kwargs)
        self._value = randint(self._lowerLimit, self._upperLimit)


class FakeFloat(FakeNumber):
    def __init__(self, *args, **kwargs):
        super(FakeFloat, self).__init__(*args, **kwargs)
        self._value = randint(self._lowerLimit, self._upperLimit)+random()


class ROinteger(FakeInteger):
    """ Read Only Integer """

    def __init__(self, *args, **kwargs):
        super(ROinteger, self).__init__(*args, **kwargs)

    def value(self):
        r = random()
        if r < 0.3:
            self._value += randint(self._lowerLimit/100, self._upperLimit/100)
        elif r < 0.6:
            self._value = randint(self._lowerLimit, self._upperLimit)
        return self._value


class RWinteger(FakeInteger):
    """ Read Write Integer """

    def __init__(self, *args, **kwargs):
        super(RWinteger, self).__init__(*args, **kwargs)

    def value(self, value=None):
        if value is None:
            return self._value
        value = int(value)
        if self._lowerLimit < value < self._upperLimit:
            self._value = value


class ROfloat(FakeFloat):
    """ Read Only floating point number """

    def __init__(self, *args, **kwargs):
        super(ROfloat, self).__init__(*args, **kwargs)

    def value(self):
        r = random()
        if r < 0.3:
            self._value += randint(self._lowerLimit/100,
                                   self._upperLimit/100)+random()
        elif r < 0.6:
            self._value = randint(self._lowerLimit,
                                  self._upperLimit)+random()
        return self._value


class RWfloat(FakeFloat):
    """ Read Write Integer """

    def __init__(self, *args, **kwargs):
        super(RWfloat, self).__init__(*args, **kwargs)

    def value(self, value=None):
        if value is None:
            return self._value
        value = float(value)
        if self._lowerLimit < value < self._upperLimit:
            self._value = value


# class ROintegerArray(FakeIntegerArray):
#     def __init__(self, *args, **kwargs):
#         super(ROintegerArray, self).__init__(*args, **kwargs)
#         self.value()
# 
#     def value(self):
#         self._value = randint(self._lowerLimit, self._upperLimit,
#                               size=self._samples)
#         return self._value
