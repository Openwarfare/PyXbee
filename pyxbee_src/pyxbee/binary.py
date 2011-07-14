'''
Created on Jan 18, 2010
@author: afosterw
'''

class ElementExists(Exception):
    pass

class NotDatamapInstance(Exception):
    pass

class NoData(Exception):
    pass

class Datamap:
    
    def __init__(self, name,  map_type=str, start_index = 0, end_index = None):
        self.name = name
        self._data = None
        self.start_index = start_index
        self.end_index = end_index
        self.parent = None
        self.children = dict()
        self.children_names = dict()
        self.map_type = map_type
    
    def __setslice__(self,i,j,datamap):
        if not isinstance(datamap,Datamap) :
            raise NotDatamapInstance
        datamap.start_index = i
        datamap.end_index = j
        self.add_child(datamap)
    
    def __setitem__(self,key,value):
        if type(key) is slice:
            if not isinstance(value,Datamap) :
                raise NotDatamapInstance
            value.start_index = key.start
            value.end_index = key.stop
            self.add_child(value)
        
    def load(self,data):
        self._data=data
    
    def add_child(self, map):
        map.parent = self
        self.children_names[map.name] = map
        end = map.end()
        if map.end_index is None:
            end = self.length()
            
        for i in range(map.start(),end):
            self.children[(map.span())]=map
            
    def start(self):
        if self.parent is not None:
            return self.start_index + self.parent.start()
        return self.start_index
    
    def end(self):
        if self.end_index is None:
            return None
        if self.parent is not None:
            return self.parent.start() + self.end_index
        return self.end_index
    
    def length(self):
        if self._data is None:
            return 0
        return len(self._data)
    
    def root(self):
        if self.parent is None:
            return self
        return self.parent.root()
    
    def data(self):
        try:
            return self.root()._data[self.start():self.end()]
        except TypeError:
            raise NoData('There is no data in this map')
    
    def value(self):
        return self.map_type(self.data())
    
    def span(self):
        return (self.start(),self.end())
    
    def __getattr__(self,name):
        return self.children_names[name]
    
    def __repr__(self):
        return str(self.value())
    
    def dump_string(self,depth=0):
        dump=' '*depth+'%s:(%s:%s)\n'%(self.name,self.start(),self.end())
        for child in self.children_names.itervalues():
            dump+=child.dump_string(depth+1)
        return dump

    def __str__(self):
        return self.dump_string()
    
    def __unicode__(self):
        return self.dump_string()


class Bytes:
    
    def __init__(self, bytes, default_repr=str):
        self.repr_type=default_repr
        #TODO:Think about not always representing bytes as a string...
        self.bytes=str(bytes)
    
    def __getitem__(self,key):
        return Bytes(self.bytes.__getitem__(key),self.repr_type)
    
    def __setitem__(self,key,value):
        tmp_bytes=list(self.bytes)
        tmp_bytes.__setitem__(key,str(value))
        self.bytes=''.join(tmp_bytes)
    
    def __repr__(self):
        return self.repr_type(self.bytes)
    
    def __str__(self):
        return str(self.repr_type(self.bytes))
    
    def bits(self):
        return Bits(bytes=self.bytes)
    
class Bits:
    
    def __init__(self, bytes=None, bits=None, byte_size=8, zfill = True):
        self.bit_string=None
        self.byte_size=byte_size
        if bytes != None:
            self.fromBytes(bytes, zfill)
            
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
    
    #TODO:handle nested structures
    def fromBytes(self, bytes, zfill=True):
        self.bit_string=''
        if type(bytes) is int:
            self.bit_string = intToBinString(bytes)
            
        if type(bytes) is str or type(bytes) is unicode or hasattr(bytes,"__iter__"):
            for byte in bytes:
                if type(byte) is str or type(byte) is unicode:
                    byte=ord(byte)
                self.bit_string+=intToBinString(byte, zfill)
    
    def zfill_byte(self, byte):
        return zfill_byte(byte,self.byte_size)
    
    def bytes(self,left_to_right=True, unicode = False):
        #print('toBytes')
        offset = 0
        size=len(self.bit_string)/self.byte_size
        string=''
        while offset < size:
            #print('offset:%s:size:%s'%(offset,size))
            chunk=self.bit_string[offset*self.byte_size:((offset+1)*self.byte_size)]
            #print chunk
            if unicode:
                string+=unichr(int(chunk,2))
            else :
                string+=chr(int(chunk,2))
            offset+=1
        return Bytes(string)
    
    def int(self):
        return int(self.bit_string,2)
    
    def hex(self):
        return hex(self.int())
    
    def bin(self):
        return bin(self.int())
    
    def concatinate(self, bits):
        return Bits(bits = self.bit_string + bits.bit_string)
        
    def bitwise_and(self,bits, zfill = True):
        result = self.int() & bits.int()
        return Bits(bytes = result, zfill = zfill)
    
    def bitwise_or(self, bits, zfill = True):
        result = self.int() | bits.int()
        return Bits(bytes = result, zfill = zfill)
    
    def bitwise_xor(self, bits, zfill = True):
        result = self.int() ^ bits.int()
        return Bits(bytes = result, zfill = zfill)
    
    def bitwise_shift_left(self, num_bits):
        return Bits(self.int() << num_bits)
    
    def bitwise_shift_right(self, num_bits):
        return Bits(self.int() >> num_bits)
    
def intToBinString(integer, zfill = True, byte_size = 8):
    result=bin(integer)[2:]
    if zfill:
        result = result.zfill(byte_size)
    return result

def zfill_byte(self, byte, byte_size = 8):
    return byte.zfill(byte_size)