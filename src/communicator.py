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

__author__ = "Sergi Blanch-Torne, Antonio Milan Otero"
__maintainer__ = "Sergi Blanch-Torne"
__email__ = "sblanch@cells.es"
__copyright__ = "Copyright 2015, CELLS / ALBA Synchrotron"
__license__ = "GPLv3+"
__status__ = "Production"

import array
import PyTango
import serial

import socket
from time import sleep
import threading

TIME_BETWEEN_SENDANDRECEIVE = 0.05


def buildCommunicator(instrumentName, port=None, parent=None, extra_args=None):
    if __isHostName(instrumentName):
        return bySocket(instrumentName, port=port, parent=parent)
    elif __isVisaDevice(instrumentName):
        return byVisa(instrumentName, parent=parent)
    elif __isSerialDevice(instrumentName):
        return bySerialDevice(instumentName, parent=parent)
    elif __isSerial(instrumentName):
        return bySerial(instrumentName, parent=parent, serial_args=extra_args)
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


def __isSerial(name):
    try:
        serial.Serial(name)
        return True
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


class Communicator:
    def __init__(self):
        raise NotImplementedError("This class is pure abstract")

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

    def ask(self, commandList):
        '''Prepare the command list and do a combination of send(msg) and recv()
        '''
        with self.mutex:
            command = self.prepareCommand(commandList)
            self._send(command)
            sleep(TIME_BETWEEN_SENDANDRECEIVE)
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
        if isinstance(commands, str) and not commands[-1:] == '\n':
            return commands+'\n'
        elif isinstance(commands, list):
            return reduce(lambda x, y: x+';'+y+';', commands)[:-1]+'\n'
        else:
            raise Exception('Exception: Wrong type! Command should be a str '
                            'or list of commands')


SOCKET_TIMEOUT = 2
DEFAULT_PORT = 5025
DEFAULT_BUFFERSIZE = 10240


class bySocket(Communicator):
    def __init__(self, hostName, port=DEFAULT_PORT, parent=None):
        self.__hostName = hostName
        self.__port = port
        self._parent = parent
        self.mutex = threading.Lock()
        self.debug_stream("building a communication to %s by socket "
                          "using port %d" % (self.__hostName, self.__port))
        self._socket = None
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
        # self.debug_stream("Sending to %s:%d %s"
        #                   % (self.__hostName, self.__port, repr(msg)))
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

    def ask_for_values(self, commandList):
        '''
        '''
        with self.mutex:
            command = self.prepareCommand(commandList)
            self._send(command)
            answer = self._recv()
            return answer


class byVisa(Communicator):
    def __init__(self, devName, parent=None):
        self.__device = PyTango.DeviceProxy(devName)
        self._parent = parent
        self.mutex = threading.Lock()
        self.debug_stream("building a communication to %s by PyVisa"
                          % (devName))

    def connect(self):
        if not self.__device.State() == PyTango.DevState.ON:
            self.__device.Open()

    def disconnect(self):
        self.__device.Close()

    def _send(self, msg):
        # self.debug_stream("Sending to %s %s"
        #                   %(self.__device.get_name(),repr(msg)))
        self.__device.Write(array.array('B', msg).tolist())

    def _recv(self):
        msg = array.array('B', self.__device.ReadLine())
        # self.debug_stream("Received from %s %s"%(self.__device.get_name(),
        #                                          repr(msg)[:100]))
        return msg

    def close(self):
        if self.__device.State() == PyTango.DevState.ON:
            self.__device.Close()

    def ask(self, commandList):
        answer = self.__device.Ask(array.array('B', commandList).tolist())
        return array.array('B', answer).tostring()

    def ask_for_values(self, commandList):
        with self.mutex:
            answer = self.__device.AskValues(array.array('B',
                                                         commandList).tolist())
            # self.debug_stream("byVisa.ask_for_values(): %s"%answer)
            self.mutex.release()
            return answer


class bySerial(Communicator):
    def __init__(self, name, parent=None, serial_args=None):
        serial_args['port'] = name
        self.__device = serial.Serial(**serial_args)
        print self.__device
        self._parent = parent
        self.mutex = threading.Lock()
        self.debug_stream("building a communication to %s by direct serial "
                          "connection" % (name))

    def connect(self):
        self.__device.open()
        self.__device.readlines()
        self.__device.flush()

    def disconnect(self):
        self.__device.close()

    def _send(self, msg):
        self.__device.write(msg+'\n')

    def _recv(self):
        msg = self.__device.readline()
        return msg


class bySerialDevice(Communicator):
    pass
