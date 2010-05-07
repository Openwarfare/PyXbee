import serial
import firmware
from datetime import datetime, timedelta
import time
import csv
import mxi
import logging

class XBeeSerialInterface(serial.Serial):
    
    def write(self,data):
        logging.debug('XBeeSerialInterface.write: %s'%data)
        serial.Serial.write(self, data)
        
    def response(self):
        responses=[]
        response=self.readline(eol='\r')
        logging.debug('XBeeSerialInterface.response: %s'%response)
        responses.append(response.strip('\r'))
        if self.inWaiting() != 0:
            responses=responses+self.response()
        return responses
    
    def connected(self):
        return self.isOpen()

class XBee:
    
    at_mode=True
    firmware=None
    config=None
    interface=None
    command_mode_char='+++'
    eol_char='\r'
    packet_start=0x7E
    command_mode_timeout=0
    last_at=0
    
    def __init__(self,interface=None, at_mode=True):
        self.interface=interface
        self.at_mode=at_mode
        self.firmware=None
        self.config=None
        self.command_mode_char='+++'
        self.packet_start=0x7E
        self.command_mode_timeout=0
        self.last_at=None
    
    
    def loadCommands(self, file_name, file_type=None):
        if not file_type:
            file_type=file_name.split('.')[-1]
        if file_type == 'csv':
            self.loadCommandsCsv(file_name)
        if file_type == 'mxi':
            self.loadCommandsMxi(file_name)
    
    def loadCommandsCsv(self,file_name):
        if self.firmware is None:
            self.firmware=firmware.Firmware()
        with open(file_name) as f:
            csv_file=csv.DictReader(f)
            for data in csv_file:
                self.firmware.setCommand(firmware.Command(
                                                            name=data['name'],
                                                            at=data['at'],
                                                            category=firmware.Category(name=data['category']),
                                                            input=None,
                                                            description=data['description'],
                                                            default=data['default']
                                                            ))
    
    def loadCommandsMxi(self,file_name):
        mxi.load(file_name, self.firmware)
    
    def loadConfig(self,config):
        pass
    
    def callCommands(self,name,value=None):
        #FIXME: change this to use lists instead of dicts as order might not be kept
        if not self.firmware.commands:
            #TODO: auto load commands here
            #TODO: custom exception
            raise Exception('Command set not loaded')
        calls=[]
        if isinstance(name, firmware.Command):
            calls=[Call(name,value)]
        elif type(name) is str:
            calls=[Call(self.firmware.getCommand(name),value)]
        elif type(name) is dict:
            call=[]
            for command,value in name.iteritems():
                calls.append(Call(self.firmware.getCommand(command),value))
        else:
            raise Exception('Must be string, dict or firmware.Command')
        
        if not self.interface.connected():
            raise Exception('Unable to connect using %s'%self.interface)
        
        if self.at_mode:
            response=self.callATCommands(calls)
        else:
            response=self.callApiCommands(calls)
            
        return response
    
    def callATCommands(self, calls):
        command_string='AT%s%s'%(self.buildATCommands(calls),self.eol_char)
        self.commandMode()
        self.interface.write(command_string)
        for index,result in enumerate(self.interface.response()):
            calls[index].result=result
        return calls
    
    def callApiCommands(self, commands):
        raise Exception('API mode not implemented yet')
    
    def commandMode(self): 
        if self.commandModeExpired():
            self.interface.write(self.command_mode_char)
            response=self.interface.response()
            if response[0] == 'OK':
                self.last_at=datetime.now()
                return True
            else:
                return False
        #if self.command_mode_timeout is None:
        #    self.command_mode_timeout=self.callATCommand('ct')
            
    def commandModeExpired(self):
        if self.command_mode_timeout is None or self.last_at is None:
            return True
        return datetime.now() > self.last_at+timedelta(microseconds=self.command_mode_timeout)
            
    def buildATCommands(self,calls):
        result=[]
        for call in calls:
            logging.debug('%s can write:%s'%(call.command.at,call.command.write))
            logging.debug(call.command)
            if call.value != None and call.command.write is True:
                call.command.input.value=call.value
                result.append('%s%s'%(call.command.at,call.command.input.value.serial()))
            else:
                result.append('%s'%call.command.at)
        return ','.join(result)
    
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

class Call:
    def __init__(self,command,value=None,result=None):
        self.command=command
        self.value=value
        self.result=result
    
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "%s:%s:%s"%(self.command.at,self.value,self.result)
    
def main():
    logging.basicConfig(level=logging.DEBUG)
    xbee=XBee(XBeeSerialInterface('/dev/ttyUSB0',9600,timeout=1))
    xbee.loadCommands('../firmware/xbee_defaults.csv')
    xbee.loadCommands('../firmware/XBP24_15_4_10C8.mxi')
    results=xbee.callCommands({'vr':None,'ct':255})
    print results
    
if __name__ == '__main__':
    main()