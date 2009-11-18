#TODO:These types need to be reworked so they make more sense and are easier to use.
#the current implementation is clumsy and need to be refined.  Think about moving
#the validators into the type and only storing the value in the type.  Right now the
#value is stored in the type and or the InputField value which is weird
#TODO: Get rid of these types altogether perhaps.  The only two types are numbers
#and strings.

class Type:
    validator=None
    
class Raw:
    value=None
    
    def __init__(self,value=None):
        self.value=value
 
    def __str__(self):
        return '%s'%self.value
    
    def serial(self):
        return '%s'%self.value

class String(Raw):
    
    def __setattr__(self,name,value):  
        if name is 'value':
            if value is None:
                pass
            else:
                value=str(value)
        
        self.__dict__[name]=value
        
    def __len__(self):
        return len(self.value)

class HexString(String):
    
    def __setattr__(self,name,value):  
        if name is 'value':
            if value is None:
                pass
            else:
                value=str(value)
                value=value[2:]
        
        self.__dict__[name]=value
        
class Hex(Raw):
    
    def __setattr__(self,name,value):
        if name is 'value':
            if value is None:
                pass
            elif type(value) is str:
                value=int(value.strip(),16)
            else:
                value=int(value)
        
        self.__dict__[name]=value
    
    def __str__(self):
        if self.value:
            return hex(self.value)
        else:
            return '%s'%self.value
    
    def serial(self):
        if self.value:
            return hex(self.value)[2:]
        return ''
    
class Int(Hex):
    
    def __setattr__(self,name,value):
        if name is 'value':
            if value is None:
                pass
            elif type(value) is str:
                value=int(value.strip())
            else:
                value=int(value)
        
        self.__dict__[name]=value
    
    def __str__(self):
        return '%s'%self.value
    
class Binary(Hex):

    def __setattr__(self,name,value):
        if name is 'value':
            if value is None:
                self.__dict__['value']=None
            elif type(value) is str:
                self.__dict__['value']=int(value,2)
            else:
                self.__dict__['value']=int(value)
        else:
            self.__dict__[name]=value
            
    def __str__(self):
        if self.value:
            return bin(self.value)
        else:
            return '%s'%self.value

class Choice(Int):
    choice_type=int
    choices=None
    value=None
    
    def __init__(self,value=None,choices=None):
        self.choices=dict()
        if choices:
            self.choices=choices
        if value:
            self.value=self.choice_type(value)
    
    def add(self,name,value):
        self.choices[name]=self.choice_type(value)
    
    def name(self,choice):
        return self.choices.keys()[self.choices.values().index(choice)]
    
    def __setattr__(self,name,value):
        self.__dict__[name]=value
        
    def __str__(self):
        return "<Choice:%s(%s)>"%(self.value,self.name(self.value))