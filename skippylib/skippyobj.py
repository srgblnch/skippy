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

__author__ = "Sergi Blanch-Torné"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2017, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"


class SkippyObj(object):
    def __init__(self, name, *args, **kwargs):
        super(SkippyObj, self).__init__()
        if name is None:
            raise AssertionError("Functionality must have a name")
        self._name = name

    @property
    def name(self):
        return self._name

    # TODO: python logging when there is no tango device above

    def debug_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: %s" % (msg))

    def info_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.info_stream(msg)
        else:
            print("INFO:  %s" % (msg))

    def warn_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.warn_stream(msg)
        else:
            print("WARN:  %s" % (msg))

    def error_stream(self, msg):
        if hasattr(self, '_parent') and self._parent:
            self._parent.error_stream(msg)
        else:
            print("ERROR: %s" % (msg))

    def _get_state(self):
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, 'get_state'):
            return self._parent.get_state()
        return PyTango.DevState.UNKNOWN

    def _change_state_status(self, *args, **kwargs):
        if hasattr(self, '_parent') and self._parent and \
                hasattr(self._parent, 'change_state_status'):
            self._parent.change_state_status(*args, **kwargs)
