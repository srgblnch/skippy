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
#  along with this program; If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

from __future__ import print_function
try:
    import __builtin__
except ValueError:
    # Python 3
    import builtins as __builtin__
from PyTango import DevState

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


def trace(method):
    def _compact_args(lst_args, dct_args):
        lst_str = "*args: {0}".format(lst_args) if len(lst_args) > 0 else ""
        dct_str = "**kwargs: {0}".format(dct_args) if len(dct_args) > 0 else ""
        if len(lst_str) > 0 and len(dct_args) > 0:
            return "{0}, {1}".format(lst_str, dct_str)
        elif len(lst_str) > 0:
            return "{0}".format(lst_str)
        elif len(dct_str) > 0:
            return "{0}".format(dct_str)
        return ""

    def _get_printer(obj):
        if hasattr(obj, "debug_stream"):
            return obj.debug_stream
        return __builtin__.print

    def _compact_answer(answer):
        if isinstance(answer, str) and len(answer) > 100:
            return "{0}...{1}".format(answer[:25], answer[-25:])
        return "{0}".format(answer)

    def logging(*args, **kwargs):
        self = args[0]
        klass = self.__class__.__name__
        method_name = method.__name__
        args_str = _compact_args(args[1:], kwargs)
        printer = _get_printer(self)
        printer("> {0}.{1}({2})"
                "".format(klass, method_name, args_str))
        answer = method(*args, **kwargs)
        answer_str = _compact_answer(answer)
        printer("< {0}.{1}: {2}"
                "".format(klass, method_name, answer_str))
        return answer
    return logging


class AbstractSkippyObj(object):
    def __init__(self, name, parent=None, *args, **kwargs):
        super(AbstractSkippyObj, self).__init__()
        if name is None:
            raise AssertionError("SkippyObj must have a name")
        self._name = name
        self._parent = parent

    @property
    def name(self):
        return self._name

    # TODO: python logging when there is no tango device above

    def debug_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: {0}".format(msg))

    def info_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.info_stream(msg)
        else:
            print("INFO:  {0}".format(msg))

    def warn_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.warn_stream(msg)
        else:
            print("WARN:  {0}".format(msg))

    def error_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.error_stream(msg)
        else:
            print("ERROR: {0}".format(msg))

    def _get_state(self):
        if hasattr(self, '_statemachine') and self._statemachine:
            return self._statemachine.state
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, 'get_state'):
            return self._parent.get_state()
        return DevState.UNKNOWN

    def _change_state_status(self, newState=None, newLine=None,
                             important=False):
        if hasattr(self, '_statemachine') and self._statemachine:
            if newState is not None:
                self._statemachine.state = newState
            if newLine is not None:
                self._statemachine.addStatusMessage(newLine, important)
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, '_change_state_status'):
            self._parent._change_state_status(newState, newLine, important)


class AbstractSkippyAttribute(AbstractSkippyObj):
    def __init__(self, *args, **kwargs):
        super(AbstractSkippyAttribute, self).__init__(*args, **kwargs)


class AbstractSkippyFeature(AbstractSkippyObj):
    def __init__(self, *args, **kwargs):
        super(AbstractSkippyFeature, self).__init__(*args, **kwargs)
