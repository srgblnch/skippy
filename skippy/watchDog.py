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


from PyTango import DevState
from threading import Thread, Event
from time import sleep

MINIMUM_RECOVERY_DELAY = 3.0


class WatchDog(object):

    _device = None
    _thread = None
    _work = None
    _finish = None
    _checkPeriod = None
    _recoverDelay = None

    # TODO: dynamic delay for reconnections to avoid too much retries when,
    #       for example the instrument has been shutdown. But recover asap
    #       it is back ON in a reasonable time.
    # TODO: collect information about when and why it had to act

    def __init__(self, device, checkPeriod=3.0,
                 recoverDelay=MINIMUM_RECOVERY_DELAY, *args, **kwargs):
        super(WatchDog, self).__init__(*args, **kwargs)
        self._device = device
        self._checkPeriod = float(checkPeriod)
        self._recoverDelay = float(recoverDelay)
        self.__prepareEvents()
        self.__prepareThread()
        self._debug("WatchDog prepared")

    def __prepareEvents(self):
        self._work = Event()
        self._work.clear()
        self._finish = Event()
        self._finish.clear()

    def __prepareThread(self):
        self._thread = Thread(target=self.__doWatch, name="WatchDog")
        self._thread.setDaemon(True)

    def __doWatch(self):
        self._debug("WatchDog launched")
        while not self._finish.isSet():
            if not self._work.isSet():
                self._work.wait()
            if not self.isInhibited() and not self._isInstrumentOk():
                self._reconnectProcedure()
            else:
                sleep(self._checkPeriod)
        self._debug("Watchdog ends")

    @property
    def _instrument(self):
        if self._device is not None:
            return self._device._instrument

    def isAlive(self):
        if self._thread is not None:
            return self._thread.isAlive()
        return False

    def start(self):
        if self._thread is not None and not self.isAlive():
            self._work.set()
            self._thread.start()
            return True
        return False

    def isInhibited(self):
        return self._deviceState() in [DevState.INIT, DevState.OFF]

    def standby(self):
        '''This method is to avoid the connectivity check when there are
           attributes being monitored by the device. Any communication fault
           will be discovered by the monitor.
        '''
        if self._work is not None:
            self._work.clear()
            return True
        return False

    def resume(self):
        if self._work is not None and not self._work.isSet():
            self._work.set()
            return True
        return False

    def finish(self):
        if self._finish is not None:
            self._finish.set()
            return True
        return False

    def _isInstrumentOk(self):
        if self._instrument is not None:
            try:
                idn = self._instrument.ask("*IDN?")
                if idn == self._device._idn:
                    # self._debug("Watchdog found the instrument ok")
                    return True
            except Exception as e:
                self._error("watchdog had an exception checking the "
                            "instrument: %r" % (e))
        self._warning("Watchdog couldn't talk with the instrument")
        return False

    def _reconnectProcedure(self):
        if self._instrument is not None:
            state = DevState.DISABLE
            status = "Communication with the instrument lost. "\
                     "Trying to reconnect"
            self._device.change_state_status(newState=state, newStatus=status)
            self._info("Watchdog sets a new status message: %s" % (status))
            try:
                self._instrument.disconnect()
            except Exception as e:
                state = DevState.FAULT
                status = "Failed to recover communications."
                self._device.change_state_status(newState=state,
                                                 newStatus=status)
                self._info("Watchdog sets a new status message: %s" % (status))
                return False
            if self._device._buildInstrumentObj():
                sleep(self._recoverDelay)
                if self._2Standby() and self._2On() and self._2Start():
                    pass
                self._info("Watchdog recovered the communications")
                return True
        self._error("Watchdog reconnect failed")
        return False

    def _deviceState(self):
        return self._device.get_state()

    def _2Standby(self):
        if self._device is not None and self._device.AutoStandby:
            self._device.Standby()
            return True
        return False

    def _2On(self):
        if self._device is not None and self._device.AutoOn:
            self._device.On()
            return True
        return False

    def _2Start(self):
        if self._device is not None and self._device.AutoStart:
            self._device.Start()
            return True
        return False

    def _debug(self, msg):
        if self._device is not None:
            self._device.debug_stream(msg)

    def _info(self, msg):
        if self._device is not None:
            self._device.info_stream(msg)

    def _warning(self, msg):
        if self._device is not None:
            self._device.warn_stream(msg)

    def _error(self, msg):
        if self._device is not None:
            self._device.error_stream(msg)
