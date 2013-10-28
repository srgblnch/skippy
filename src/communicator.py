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

class Communicator:
    def __init__(self):
        raise NotImplementedError("This class is pure abstract")

    def ask(self, commandList):
        """
            A combination of send(msg) and recv()
            @TODO: to make it work, you need to concatenate the request for 
            change and the query in the command.
        """
        self.mutex.acquire()
        command = self.prepareCommand(commandList)
        self._send(command)
        answer = self._recv()
        self.mutex.release()
        return answer
    
    def write(self,commandList):
        self.mutex.acquire()
        command = self.prepareCommand(commandList)
        self._send(command)
        self.mutex.release()
        
    def read(self):
        self.mutex.acquire()
        answer = self._recv()
        self.mutex.release()
        return answer

    def prepareCommand(self,commands):
        if isinstance(commands, str): 
            return commands+'\n'
        elif isinstance(commands, list): 
            return reduce(lambda x,y: x+';'+y+';',commands)[:-1]+'\n'
        else: 
            raise Exception('Exception: Wrong type! Command should be a str or list of commands')


class bySocket(Communicator):
    def __init__(self,hostName,port,parent):
        self.__hostName = hostName
        self.__port = port
        self.__parent = parent
        self.mutex = threading.Lock()
        self.__parent.debug_stream("building a communication to %s by socket "\
                                   "using port %d"%(self.__hostName,self.__port))
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.settimeout(1)
    def connect(self):
        self.__sock.connect((self.__hostName, self.__port))

    def _send(self,msg):
        self.__sock.send(msg)

    def _recv(self):
        msg = self.__sock.recv(1024)
        return msg

    def close(self):
        self.__sock.close()

    def ask_for_values(self, command):
        """
            Not sure about the difference between this and ask.
            This is only used in PyScope ds.
        """
        raise NotImplementedError("Not implemented")


class byVisa(Communicator):
    def __init__(self,devName,parent):
        self.__device = PyTango.DeviceProxy(devName)
        self.__parent = parent
        self.mutex = threading.Lock()
        self.__parent.debug_stream("building a communication to %s by PyVisa"
                                   %(devName))

    def connect(self):
        if not self.__device.State() == PyTango.DevState.ON:
            self.__device.Open()
    
    def _send(self,msg):
        self.__device.Write(array.array('B',msg).tolist())

    def _recv(self):
        return array.array('B',self.__device.ReadLine())

    def close(self):
        if self.__device.State() == PyTango.DevState.ON:
            self.__device.Close()

    def ask(self, commandList):
        return array.array('B',self.__device.Ask(array.array('B',commandList).tolist())).tostring()

    def ask_for_values(self, command):
        return self.__visaSc__deviceope.AskValues(array.array('B',commandList).tolist())

