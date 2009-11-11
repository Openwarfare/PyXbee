from datatypes import *
from hashlib import md5

#FIXME: Move this into the command!
class Input:
    type=None
    info=None
    validator=None
    
    def __init__(self, value=None, type=Raw, validator=None, info=None):
        self.type=type
        self.validator=validator
        self.value=value
        self.info=info
    
    def __setattr__(self,name,value):
        if name is 'value' or name is 'default':
            if value is not None:
                value=self.type(value)
                if self.validator:
                    self.validator.validate(value)
        self.__dict__[name]=value
    
    def __str__(self):
        return "<Input:%s %s(%s) %s %s>"%(self.type,self.default,self.value,self.info,self.validator)

class Value:
    type=None
    value=None


class Command:
    name=None
    alias=None
    at=None
    input=None
    category=None
    default=None
    write=True
    read=True
    input_info=None
    description=None

    
    def __init__(self,name=None, at=None, category=None, input=None, description=None, default=None):
        self.name=name
        self.at=at
        self.category=category
        self.input=input
        self.description=description
        self.default=default
        
    def alias(self):
        return self.name.lower().replace(' ','_').replace('-','').replace('/','')
    
    def __repr__(self):
        return "<Command at:%s, alias:%s, name:%s, category:%s default:%s>"%(self.at,self.alias(), self.name, self.category.name, self.default)

    def __str__(self):
        return "<Command at:%s, alias:%s, name:%s, category:%s default:%s>"%(self.at,self.alias(), self.name, self.category.name, self.default)

class Status:
    is_written=False
    is_sent=False
    is_changed=False
    
    
class Category:
    header=None
    name=None
    description=None
    parent=None
    
    def __init__(self, name=None, description=None, header=None, parent=None):
        self.name=name
        self.description=description
        self.header=header
        self.parent=parent
    
    def __str__(self):
        if self.parent:
            parent=self.parent.name
        else:
            parent="None"
            
        return "<Category header:%s, name:%s, parent:%s>"%(self.header,self.name,parent)
 
class Firmware:
    version=None
    function_set=None
    product=None
    modem=None
    commands=None
    at_commands=None
    
    def __init__(self, product=None, modem=None, version=None, function_set=None):
        self.version=version
        self.function_set=function_set
        self.product=product
        self.modem=modem
        self.commands=dict()
        self.at_commands=dict()
        self.bootstrap()
    
    def bootstrap(self,data=None):
        pass
    
    def setCommand(self,command):
        self.commands[command.alias()]=command
        self.commands[command.at.lower()]=command
        #TODO:Think about removing the at dict all together
        self.at_commands[command.at]=command
    
    def getCommand(self,name):
        if isinstance(name, Command):
            name=name.name
        return self.commands[name.lower()]
        
    #def __getattr__(self,name):
    #    return self.getCommand(name)
    
    #def __setattr__(self,name,value):
    #    command=self.getCommand(name)
        
    
    def __str__(self):
        result="<Commands function_set:%s, product:%s, modem:%s, version:%s>\n"%(self.function_set, self.product, self.modem, self.version)
        for alias, command in self.commands.iteritems():
            result+="%s\n"%command
        return result
    
    def id(self,hash=True):
        id="function_set:%s, product:%s, modem:%s, version:%s"%(self.function_set, self.product, self.modem, self.version)
        if hash:
         id=md5(id).hexdigest()
        return i     