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

    def debug_stream(self,msg):
        if hasattr(self._parent,'debug_stream'):
            self._parent.debug_stream(msg)
        else:
            print(msg)

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
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.settimeout(1)
    def connect(self):
        self.__sock.connect((self.__hostName, self.__port))

    def _send(self,msg):
        self.debug_stream("Sending to %s:%d %s"%(self.__hostName,self.__port,repr(msg)))
        self.__sock.send(msg)

    def _recv(self,bufsize=10240):
        completeMsg = ''
        buffer = self.__sock.recv(bufsize)
        completeMsg = ''.join([completeMsg,buffer])
        if completeMsg.startswith('#') or completeMsg.count(','):
            #This is when what was requested is an array of values from one attr
            #when binary mode starts with #, on ASCII mode the values are ',' separated
            while not len(buffer) == 0:
                try:
                    buffer = self.__sock.recv(bufsize)
                except Exception,e:
                    #print("reception break due to exception: %s"%(e))
                    break
                    #FIXME: there must be a better stopper than a timeout
                else:
                    completeMsg = ''.join([completeMsg,buffer])
        self.debug_stream("Received from %s:%d %s"
                          %(self.__hostName,self.__port,
                            repr(completeMsg)[:100]))
        return completeMsg

    def close(self):
        self.__sock.close()

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
    
    def _send(self,msg):
        self.debug_stream("Sending to %s %s"%(self.__device.get_name(),repr(msg)))
        self.__device.Write(array.array('B',msg).tolist())

    def _recv(self):
        msg = array.array('B',self.__device.ReadLine())
        self.debug_stream("Received from %s %s"%(self.__device.get_name(),
                                                 repr(msg)[:100]))
        return msg

    def close(self):
        if self.__device.State() == PyTango.DevState.ON:
            self.__device.Close()

    def ask(self, commandList):
        return array.array('B',self.__device.Ask(array.array('B',commandList).tolist())).tostring()

    def ask_for_values(self, commandList):
        self.mutex.acquire()
        answer = self.__device.AskValues(array.array('B',commandList).tolist())
        self.debug_stream("byVisa.ask_for_values(): %s"%answer)
        self.mutex.release()
        return answer

