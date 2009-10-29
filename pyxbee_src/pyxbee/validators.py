import types

class InvalidValue(Exception):
    pass

class Range:
    range=None
    
    def __init__(self,low,high):
        self.range=(low,high)
        
    def valid(self,value):
        if value is None:
            return True
        return value.value >= self.range[0].value and value.value <=self.range[1].value
        
    def validate(self,value):
        if not self.valid(value):
            raise InvalidValue('%s out of range %s-%s'%(value,self.range[0],self.range[1]))
    
    def __str__(self):
        return "<Range: %s-%s>"%self.range

class Length(Range):
    
    def valid(self,value):
        if value is None:
            return True
        return len(value) >= self.range[0].value and len(value)<=self.range[1].value
    
    def validate(self,value):
        if not self.valid(value):
            raise InvalidValue('length of %s (%s) is out of range %s-%s'%(value,len(value),self.range[0],self.range[1]))
    
    def __str__(self):
        return "<Length: %s-%s>"%self.range
    
class Choice:
    choices=dict()
    
    def __init__(self,choices):
        self.choices=choices
    
    def add(self,name,value):
        if type(value) is not int:
            self.choices[name]=self.int(value)
        else:
            self.choices[name]=value
    
    def valid(self, value):
        if type(value) is str:
            return value in self.choices
        return value in self.choices.values()
        
    def validate(self, value):
        if not self.valid(value):
            raise InvalidValue('%s is an invalid choice'%value)
    
    def __str__(self):
        return '%s'%self.choices