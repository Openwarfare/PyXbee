'''
Created on Jan 18, 2010

@author: afosterw

Binary Map Example

1210255areth:test456

data_map=Map('payload')
data_map[0:]=StringData(('name','function'),':')

base_map=Map('packet')
base_map[0:2]=StringElement('id')
base_map[2:4]=IntElement('length')
base_map[4:'length']=data_map
base_map['length':'length+1']=ChecksumElement('checksum',base_map.element('payload'))
'''

#1234name:areth4
    
class Map:
    
    def __init__(self, name=None, start=None, end=None):
        self.ordered_elements = dict()
        self.named_elements = dict()
        self.name = name
        self.start_index = start
        self.end_index = end
        self.parent = None
        self.data = None
    
    def __setitem__(self,key,value):
        if issubclass(value.__class__, MapElement):
            self.setElement(key.start, key.stop, value)
    
    def _resolve(self,value):
        if callable(value):
            return value()
        if isinstance(value, str):
            return self.findElement(value).value()
            
        return value
    
    def findElement(self,name):
        if self.name==name:
            return self
        if self.named_elements.has_key(name):
            return self.named_elements[name]
            
    def setElement(self, start, end, element):
        element.start_index = start
        element.end_index = end
        self.named_elements[element.name]=element
        self.ordered_elements[(element.start_index,element.end_index)]=element
        
    def value(self):
        pass
    
    def start(self):
        return self.start_index
    
    def end(self):
        return self.end_index
    
    def length(self):
        return len(self.data)
    
    def string(self):
        pass
    
    def dump(self,tabs=0):
        print("%s%s[%s:%s]"%('\t'*tabs,self.name,self.start(),self.end()))
        for element in self.ordered_elements.itervalues():
            element.dump(tabs+1)
        
        
#TODO: Look into using lists instead of strings.
class Bytes:
    
    def __init__(self, bytes, default_repr=str):
        self.repr=default_repr
        self.bytes=bytes
    
    def __getitem__(self,key):
        return Bytes(self.bytes.__getitem__(key))
    
    def __setitem__(self,key,value):
        tmp_bytes=list(self.bytes)
        tmp_bytes.__setitem__(key,str(value))
        self.bytes=''.join(tmp_bytes)
    
    def __repr__(self):
        return self.repr(self.bytes)
    
    def __str__(self):
        return str(self.repr(self.bytes))
    
    def bits(self):
        return Bits(bytes=self.bytes)
    
class Bits:
    
    def __init__(self,bytes=None, byte_size=8, bits=None):
        self.bit_string=None
        self.byte_size=byte_size
        if bytes != None:
            self.fromBytes(bytes)
            
        if bits != None:
            self.fromBits(bits)
        
    def __getitem__(self,key):
        return Bits(bits=self.bit_string.__getitem__(key))
    
    def __setitem__(self,key,value):
        tmp_bit_string=list(self.bit_string)
        tmp_bit_string.__setitem__(key,str(value))
        self.bit_string=''.join(tmp_bit_string)
    
    def __len__(self):
        return len(self.bit_string)
    
    def __repr__(self):
        return self.bit_string
    
    def __str__(self):
        #print self.bits
        return self.bit_string
    
    def fromBits(self, bit_string):
        self.bit_string=bit_string
    
    #TODO:make this a function
    def fromBytes(self,bytes, zfill=True):
        self.bit_string=''
        for byte in bytes:
            if type(byte) is str:
                byte=ord(byte)
            byte=bin(byte)[2:]
            if zfill:
                byte=byte.zfill(self.byte_size)
            self.bit_string+=byte

    def bytes(self,left_to_right=True):
        #print('toBytes')
        offset = 0
        size=len(self.bit_string)/self.byte_size
        string=''
        while offset < size:
            #print('offset:%s:size:%s'%(offset,size))
            chunk=self.bit_string[offset*self.byte_size:((offset+1)*self.byte_size)]
            #print chunk
            string+=chr(int(chunk,2))
            offset+=1
        return Bytes(string)
    
    def int(self):
        return int(self.bit_string,2)

frame_data='~somedatahere'
frame=MapElement('frame',0,'length')
frame[0:]=MapElement('test')
frame.dump()