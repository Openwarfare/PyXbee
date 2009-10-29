import serial
import firmware
import datetime
import time
import csv

class XbeeSerialInterface(serial.Serial):
    
    def response(self,timeout=None):
        response=''
        if timeout is not None:
            started=datetime.time()
            
        while not self.inWaiting():
            if timeout is not None:
                if time.time()-started > timeout:
                    break
        while self.inWaiting():
            response+=self.read()
        return response
    
class XBee:
    at_mode=True
    firmware=None
    config=None
    interface=None
    command_mode_char='+++'
    packet_start=0x7E
    command_mode_timeout=0
    last_at=0
    

    
    def __init__(self,interface=None, at_mode=True):
        self.interface=interface
        self.mode=mode
    
    def loadCommands(self, file, type=None):
        
        if type is 'csv':
            pass
        if type is 'mxi':
            pass
    
    def loadCommandsCsv(self,file_name):
        data=csv.reader(open(file_name))
    
    def loadCommandsMxi(self,file_name):
        pass
    
    def loadConfig(self,config):
        pass
    
    def callCommand(self,name,value=None):
        command=None
        if not self.commands:
            #TODO: auto load commands here
            #TODO: custom exception
            raise Exception('Command set not loaded')
        
        if not self.interface.connected():
            raise Exception('Unable to connect using %s'%self.interface)
        
        if self.at_mode:
            self.callATCommand(command, value)
        else:
            self.callApiCommand(command, value)
    
    def callATCommand(self,command, value=None):
        command_string='AT%s'%self.buildATCommand(self.commands.getCommand(name), value)
        self.commandMode()
        self.interface.write(command_string)
        return self.interface.response()
    
    def callApiCommand(self, command, value=None):
        raise Exception('API mode not implemented yet')
    
    def commandMode(self): 
        if self.command_mode_expired():
            self.interface.write(self.command_mode_char)
            if self.interface.response() == 'OK':
                self.last_at=datetime.time.microsecond()
                return True
        if self.command_mode_timeout is None:
            self.command_mode_timeout=self.callATCommand('ct')
            
    def commandModeExpired(self):
        if self.command_mode_timeout is None:
            return True
        return self.last_at+(self.command_mode_timeout*10) > datetime.time.microsecond()
            
    def buildATCommand(self,command,value=None):
        if value and command.write:
            command.input.value=value
            return '%s%s'%(command.at,command.input.value.serial())
        return '%s'%command.at 

class ConfigElement:
    command=None
    value=None
    is_changed=False
    is_sent=False
    
    def __init__(self, command, value=None):
        self.command=command
        self.value=value
        self.is_changed=False
        self.is_sent=False
        
    def isDefault(self):
        return self.value is command.default
    
    def isChanged(self):
        return self.is_changed
    
    def isSent(self):
        return self.is_sent
    
    def __str__(self):
        return "%s=%s"%(self.command.name,self.value)
    
class Config:
    firmware=None
    is_written=False
    
    def __init__(self,firmware):
        self.elements={}
        self.firmware=firmware
        self.is_written=False
        
    def __getattr__(self,name):
        return self.getCommand(name)
    
    def __setattr__(self,name):
        return self.getCommand(name)
    
    
    def getElement(self,command):
        if not isinstance(command,firmware.Command):
            command=self.firmware.getCommand(command)
        return self.elements[command]
    
    def setValue(self,command,value):
        try:
            self.getElement(command, create)
        except KeyError, e:
            self.addElement(ConfigElement(command,value))
            
        self.elements[command].value=value
        self.elements[command].is_changed=True
    
    def addElement(self, element):
        self.elements[element.command]=element
    
    def dict(self):
        result={"firmware_id":self.firmware.id()}
        for element in self.elements:
            result[element.command.name]=element.value
        return result
    
    def json(self):
        #TODO: check for simplejson first so that simplejson is not a requirement
        return simplejson.dumps(self.asDict())
            