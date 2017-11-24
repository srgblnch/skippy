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

import array

try:
    import serial
except:
    serial = None
import PyTango
import socket
import threading
from time import sleep
try:
    import visa
    import pyvisa
except:
    pyvisa = None

__author__ = "Sergi Blanch-Torne, Antonio Milan Otero"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

TIME_BETWEEN_SENDANDRECEIVE = 0.05


def buildCommunicator(instrumentName, port=None, parent=None, extra_args=None,
                      terminator=None, log=None):
    if parent is not None and hasattr(parent, "debug_stream"):
        log = parent.debug_stream
    if __isHostName(instrumentName):
        log("identified %r as host name" % instrumentName)
        return BySocket(instrumentName, port=port, parent=parent)
    elif __isVisaDevice(instrumentName):
        log("identified %r as visa device" % instrumentName)
        return ByVisa(instrumentName, parent=parent)
    elif __isVisaName(instrumentName):
        log("identified %r as visa name" % instrumentName)
        return ByVisaName(instrumentName, parent=parent)
    elif __isSerialDevice(instrumentName):
        log("identified %r as serial device" % instrumentName)
        return BySerialDevice(instumentName, parent=parent)
    elif __isSerialName(instrumentName):
        log("identified %r as serial name" % instrumentName)
        return BySerialName(instrumentName, parent=parent,
                            serial_args=extra_args, terminator=terminator)
    raise SyntaxError("Instrument name invalid or instrument unreachable")


def __isHostName(name):
    try:
        socket.gethostbyname(name)
        return True
    except:
        return False


def __isSerialDevice(name):
    try:
        devClass = PyTango.DeviceProxy(devName).info().dev_class
        if devClass in ('Serial', 'PySerial'):
            return True
        else:
            return False
    except:
        return False


def __isSerialName(name):
    try:
        if serial is not None:
            serial.Serial(name)
            return True
        return False
    except:
        return False


def __isVisaDevice(devName):
    try:
        devClass = PyTango.DeviceProxy(devName).info().dev_class
        if devClass == 'PyVisa':
            return True
        else:
            return False
    except:
        return False


def __isVisaName(name):
    try:
        if pyvisa is not None:
            pyvisa.visa.instrument(name)
            return True
        return False
    except:
        return False


class Communicator(object):
    _terminator = '\n'

    def __init__(self, parent=None, *args, **kwargs):
        super(Communicator, self).__init__(*args, **kwargs)
        self.mutex = threading.Lock()
        self._parent = parent

    def debug_stream(self, msg):
        if hasattr(self._parent, 'debug_stream'):
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: "+msg)

    def error_stream(self, msg):
        if hasattr(self._parent, 'error_stream'):
            self._parent.error_stream(msg)
        else:
            print("ERROR: "+msg)

    def ask(self, commandList, waittimefactor=1):
        '''Prepare the command list and do a combination of
           send(msg) and recv()
        '''
        waittime = TIME_BETWEEN_SENDANDRECEIVE * waittimefactor
        with self.mutex:
            command = self.prepareCommand(commandList)
            self._send(command)
            sleep(waittime)
            answer = self._recv()
            return answer

    def write(self, commandList):
        '''Do a write operation to the remote
        '''
        with self.mutex:
            command = self.prepareCommand(commandList)
            self._send(command)

    def read(self):
        '''Read if the remote have said something
        '''
        with self.mutex:
            answer = self._recv()
            return answer

    def prepareCommand(self, commands):
        '''Structure the command to the remote. If it's already an string, be
           sure it ends with a '\n'. If it's a list of strings concatenate them
           using ';' as a separator.
        '''
        if isinstance(commands, str) and not commands[-1:] == self.terminator:
            return "%s%s" % (commands, self.terminator)
        elif isinstance(commands, list):
            return reduce(lambda x, y: x+';'+y+';',
                          commands)[:-1]+self.terminator
        else:
            raise Exception('Exception: Wrong type! Command should be a str '
                            'or list of commands')

    @property
    def terminator(self):
        return self._terminator


SOCKET_TIMEOUT = 2
DEFAULT_PORT = 5025
DEFAULT_BUFFERSIZE = 10240


class BySocket(Communicator):
    def __init__(self, hostName, port=DEFAULT_PORT, *args, **kwargs):
        super(BySocket, self).__init__(*args, **kwargs)
        self.__hostName = hostName
        self.__port = port
        self._socket = None
        self.debug_stream("building a communication to %s by socket "
                          "using port %d" % (self.__hostName, self.__port))
        self.build()

    def build(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        if self._socket is None:
            self.build()
        self._socket.settimeout(SOCKET_TIMEOUT)
        self._socket.connect((self.__hostName, self.__port))

    def disconnect(self):
        self._socket = None
        if not self.mutex.acquire(False):
            self.debug_stream("Disconnecting: forcing to release mutex")
            self.mutex.release()

    def close(self):
        self.disconnect()  # self._socket.close()

    def isConnected(self):
        return hasattr(self, '_socket') and self._socket is not None

    def _send(self, msg):
        if self.isConnected():
            self._socket.send(msg)

    def _recv(self, bufsize=DEFAULT_BUFFERSIZE):
        if not self.isConnected():
            return ''
        completeMsg = ''
        try:
            buffer = self._socket.recv(bufsize)
        except socket.timeout:
            self.error_stream("Exception in %s: time out!" % (self.__hostName))
            return ''
        completeMsg = ''.join([completeMsg, buffer])
        if completeMsg.startswith('#'):
            try:
                nBytesHeaderLength = int(completeMsg[1])
                nBytesWaveElement = int(completeMsg[2:nBytesHeaderLength+2])
                # self.debug_stream("From the beginning %s, understood a %d "
                #                   "characters header with further %d "
                #                   "elements to be read."
                #                   %(repr(completeMsg[:10]),
                #                     nBytesHeaderLength,nBytesWaveElement))
                while len(completeMsg) < nBytesWaveElement:
                    buffer = self._socket.recv(bufsize)
                    completeMsg = ''.join([completeMsg, buffer])
            except Exception as e:
                self.error_stream("Exception in %s:%d array data "
                                  "interpretation: %s"
                                  % (self.__hostName, self.__port, e))
        else:
            try:
                while not completeMsg[len(completeMsg)-1] == '\n':
                    buffer = self._socket.recv(bufsize)
                    completeMsg = ''.join([completeMsg, buffer])
            except Exception as e:
                self.error_stream("Exception in %s:%d string data "
                                  "interpretation: %s"
                                  % (self.__hostName, self.__port, e))
        if len(completeMsg) > 50:
            pass
            # self.debug_stream("Received from %s:%d %s(...)%s (len %d)"
            #                   %(self.__hostName,self.__port,
            #                     repr(completeMsg[:25]),
            #                     repr(completeMsg[len(completeMsg)-25:]),
            #                     len(completeMsg)))
        else:
            pass
            # self.debug_stream("Received from %s:%d %s"
            #                   %(self.__hostName,self.__port,
            #                     repr(completeMsg)))
        return completeMsg

    def ask_for_values(self, commandList, waittimefactor=1):
        '''
        '''
        waittime = TIME_BETWEEN_SENDANDRECEIVE * waittimefactor
        with self.mutex:
            command = self.prepareCommand(commandList)
            self._send(command)
            sleep(waittime)
            answer = self._recv()
            return answer


class ByVisa(Communicator):
    def __init__(self, devName, *args, **kwargs):
        super(ByVisa, self).__init__(*args, **kwargs)
        self.__device = PyTango.DeviceProxy(devName)
        self.debug_stream("building a communication to %s by PyVisa"
                          % (devName))

    def connect(self):
        if not self.__device.State() == PyTango.DevState.ON:
            self.__device.Open()

    def disconnect(self):
        self.__device.Close()

    def _send(self, msg):
        self.__device.Write(array.array('B', msg).tolist())

    def _recv(self):
        msg = array.array('B', self.__device.ReadLine())
        return msg

    def close(self):
        if self.__device.State() == PyTango.DevState.ON:
            self.__device.Close()

    def ask(self, commandList, waittimefactor=None):
        with self.mutex:
            if waittimefactor is not None:
                self.warning_stream("No wait time available for "
                                    "PyVisa intermediary, ignored")
            answer = self.__device.Ask(array.array('B', commandList).tolist())
            return array.array('B', answer).tostring()

    def ask_for_values(self, commandList, waittimefactor=None):
        with self.mutex:
            if waittimefactor is not None:
                self.warning_stream("No wait time available for "
                                    "PyVisa intermediary, ignored")
            with self.mutex:
                answer = self.__device.\
                    AskValues(array.array('B', commandList).tolist())
                self.mutex.release()
                return answer


class ByVisaName(Communicator):
    def __init__(self, name, *args, **kwargs):
        super(ByVisaName, self).__init__(*args, **kwargs)
        if pyvisa is None:
            raise ImportError("soft dependency to Visa python package "
                              "unsatisfied")
        self.__name = name
        self.__visa = None

    def connect(self):
        if self.__visa is None:
            self.__visa = pyvisa.visa.instrument(self.__name)
            self.debug_stream("build VISA connection with %r" % (self.__name))
            self.__visa.timeout = SOCKET_TIMEOUT

    def disconnect(self):
        if self.__visa:
            self.__visa.close()
            self.__visa = None
            self.debug_stream("disconnected from VISA %r" % (self.__name))

    def close(self):
        self.disconnect()

    def isConnected(self):
        return self.__visa is not None

    def ask(self, commandList, waittimefactor=None):
        with self.mutex:
            if self.__visa:
                self.debug_stream("ask %r to %r" % (commandList, self.__name))
                answer = self.__visa.ask(commandList)
                self.debug_stream("received %r from %r"
                                  % (answer, self.__name))
                return answer

    def ask_for_values(self, commandList, waittimefactor=None):
        with self.mutex:
            if self.__visa:
                self.debug_stream("ask_for_values %r to %r"
                                  % (commandList, self.__name))
                answer = self.__visa.ask_for_values(commandList)
                self.debug_stream("received %r from %r"
                                  % (answer, self.__name))
                return answer

    def write(self, commandList):
        with self.mutex:
            if self.__visa:
                self.debug_stream("write %r to %r"
                                  % (commandList, self.__name))
                self.__visa.write(commandList)

    def read(self):
        with self.mutex:
            if self.__visa:
                answer = self.__visa.read()
                self.debug_stream("read %r from %r" % (answer, self.__name))
                return answer


class BySerialName(Communicator):
    def __init__(self, name, serial_args=None, terminator=None,
                 *args, **kwargs):
        super(BySocket, self).__init__(*args, **kwargs)
        if serial is None:
            raise ImportError("soft dependency to Serial python package "
                              "unsatisfied")
        serial_args['port'] = name
        self.__serialName = name
        self.__serial = serial.Serial(**serial_args)
        self._terminator = terminator or '\n'
        self.debug_stream("building a communication to %s by direct serial "
                          "connection" % (name))

    def connect(self):
        if not self.__serial.isOpen():
            self.__serial.open()
        self.__serial.flush()

    def disconnect(self):
        self.__serial.close()

    def close(self):
        self.disconnect()

    def _send(self, msg):
        self.__serial.write(msg)
        self.__serial.flush()

    def _recv(self):
        msg = self.__serial.readline(eol=self.terminator)
        return msg


class BySerialDevice(Communicator):
    pass
