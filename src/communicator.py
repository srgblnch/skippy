#!/usr/bin/env python
# -*- coding:utf-8 -*- 


##############################################################################
## license :
##============================================================================
##
## File :        communicator.py
## 
## Project :     SCPI
##
## $Author :      sblanch&amilan$
##
## $Revision :    $
##
## $Date :        $
##
## $HeadUrl :     $
##============================================================================
##        (c) - Controls Software Section - ALBA/CELLS
##############################################################################

import PyTango
import socket
import array
import threading

def buildCommunicator(instrumentName,port=None,parent=None):
    if __isHostName(instrumentName):
        return bySocket(instrumentName,port=port,parent=parent)
    elif __isTangoName(instrumentName):
        if __isVisaDevice(instrumentName):
            return byVisa(instrumentName,parent=parent)
        raise SyntaxError("Instrument device type not identified")
    raise SyntaxError("Instrument name not identified")

def __isHostName(name):
    try:
        socket.gethostbyname(name)
        return True
    except:
        return False

def __isTangoName(name):
    try:
        PyTango.DeviceProxy(name)
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

    def debug_stream(self,msg):
        if hasattr(self._parent,'debug_stream'):
            self._parent.debug_stream(msg)
        else:
            print("DEBUG: "+msg)

    def error_stream(self,msg):
        if hasattr(self._parent,'error_stream'):
            self._parent.error_stream(msg)
        else:
            print("ERROR: "+msg)

    def ask(self, commandList):
        '''Prepare the command list and do a combination of send(msg) and recv()
        '''
        self.mutex.acquire()
        command = self.prepareCommand(commandList)
        self._send(command)
        answer = self._recv()
        self.mutex.release()
        return answer
    
    def write(self,commandList):
        '''Do a write operation to the remote
        '''
        self.mutex.acquire()
        command = self.prepareCommand(commandList)
        self._send(command)
        self.mutex.release()
        
    def read(self):
        '''Read if the remote have said something
        '''
        self.mutex.acquire()
        answer = self._recv()
        self.mutex.release()
        return answer

    def prepareCommand(self,commands):
        '''Structure the command to the remote. If it's already an string, be
           sure it ends with a '\n'. If it's a list of strings concatenate them
           using ';' as a separator.
        '''
        if isinstance(commands, str) and not commands[-1:] == '\n':
            return commands+'\n'
        elif isinstance(commands, list): 
            return reduce(lambda x,y: x+';'+y+';',commands)[:-1]+'\n'
        else: 
            raise Exception('Exception: Wrong type! Command should be a str or list of commands')


class bySocket(Communicator):
    def __init__(self,hostName,port=5025,parent=None):
        self.__hostName = hostName
        self.__port = port
        self._parent = parent
        self.mutex = threading.Lock()
        self.debug_stream("building a communication to %s by socket "\
                          "using port %d"%(self.__hostName,self.__port))
        self._socket = None
        self.build()

    def build(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        if self._socket == None:
            self.build()
        self._socket.settimeout(1)
        self._socket.connect((self.__hostName, self.__port))

    def disconnect(self):
        self._socket = None
        if not self.mutex.acquire(False):
            self.debug_stream("Disconnecting: forcing to release mutex")
            self.mutex.release()

    def close(self):
        self.disconnect()#self._socket.close()

    def isConnected(self):
        return hasattr(self,'_socket') and not self._socket == None

    def _send(self,msg):
        #self.debug_stream("Sending to %s:%d %s"%(self.__hostName,self.__port,repr(msg)))
        if self.isConnected():
            self._socket.send(msg)

    def _recv(self,bufsize=10240):
        if not self.isConnected():
            return ''
        completeMsg = ''
        buffer = self._socket.recv(bufsize)
        completeMsg = ''.join([completeMsg,buffer])
        if completeMsg.startswith('#'):
            try:
                nBytesHeaderLength = int(completeMsg[1])
                nBytesWaveElement = int(completeMsg[2:nBytesHeaderLength+2])
                #self.debug_stream("From the beginning %s, understood a %d "\
                #                  "characters header with further %d "\
                #                  "elements to be read."
                #                  %(repr(completeMsg[:10]),
                #                    nBytesHeaderLength,nBytesWaveElement))
                while len(completeMsg) < nBytesWaveElement:
                    buffer = self._socket.recv(bufsize)
                    completeMsg = ''.join([completeMsg,buffer])
            except Exception,e:
                self.error_stream("Exception in %s:%d array data "\
                                  "interpretation: %s"
                                  %(self.__hostName,self.__port,e))
        else:
            try:
                while not completeMsg[len(completeMsg)-1] == '\n':
                    buffer = self._socket.recv(bufsize)
                    completeMsg = ''.join([completeMsg,buffer])
            except Exception,e:
                self.error_stream("Exception in %s:%d string data "\
                                  "interpretation: %s"
                                  %(self.__hostName,self.__port,e))
        if len(completeMsg) > 50:
            pass#self.debug_stream("Received from %s:%d %s(...)%s (len %d)"
            #                  %(self.__hostName,self.__port,
            #                    repr(completeMsg[:25]),
            #                    repr(completeMsg[len(completeMsg)-25:]),
            #                    len(completeMsg)))
        else:
            pass#self.debug_stream("Received from %s:%d %s"
            #                  %(self.__hostName,self.__port,
            #                    repr(completeMsg)))
        return completeMsg



    def ask_for_values(self, commandList):
        '''
        '''
        self.mutex.acquire()
        command = self.prepareCommand(commandList)
        self._send(command)
        answer = self._recv()
        self.mutex.release()
        return answer


class byVisa(Communicator):
    def __init__(self,devName,parent=None):
        self.__device = PyTango.DeviceProxy(devName)
        self._parent = parent
        self.mutex = threading.Lock()
        self.debug_stream("building a communication to %s by PyVisa"%(devName))

    def connect(self):
        if not self.__device.State() == PyTango.DevState.ON:
            self.__device.Open()
    def disconnect(self):
        self.__device.Close()
    
    def _send(self,msg):
        #self.debug_stream("Sending to %s %s"%(self.__device.get_name(),repr(msg)))
        self.__device.Write(array.array('B',msg).tolist())

    def _recv(self):
        msg = array.array('B',self.__device.ReadLine())
        #self.debug_stream("Received from %s %s"%(self.__device.get_name(),
        #                                         repr(msg)[:100]))
        return msg

    def close(self):
        if self.__device.State() == PyTango.DevState.ON:
            self.__device.Close()

    def ask(self, commandList):
        return array.array('B',self.__device.Ask(array.array('B',commandList).tolist())).tostring()

    def ask_for_values(self, commandList):
        self.mutex.acquire()
        answer = self.__device.AskValues(array.array('B',commandList).tolist())
        #self.debug_stream("byVisa.ask_for_values(): %s"%answer)
        self.mutex.release()
        return answer

