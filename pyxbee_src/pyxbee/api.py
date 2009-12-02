import struct
import Queue
#TODO: Think about reworking most of this.  It might be better to work with strings 
#directly rather than breaking them up into lists only to turn them back into strings
#TODO: Investigate dealing with these in a byte by byte manner for encoding.  It may 
#be more efficient
#TODO: Think about moving the packet_ids and escaped chars into a modem specific class
#that can be swapped out when hardware changes.
#TODO:Redo maps so the are an ordered list of elements with a length and a type for easier mapping

ESCAPED_CHARS=[0x7e,0x7d,0x11,0x13]

PACKET_IDS={
            0x8a:ModemStatus,
            0x08:CallATCommand,
            0x09:QueueATCommand,
            0x88:ATResponse,
            0x00:TXRequest64,
            0x01:TXRequest16,
            0x89:TXStatus,
            0x80:RXPacket64,
            0x81:RXPacket16,
            }

class BadChecksum(Exception):
    data=None
    checksum=None
    def __init__(self,data=None, checksum=None):
        self.data=data
        self.checksum=checksum

class Packet:
    id=None
    map={}
    
    def __init_(self,data=None):
        self.unpack(data)
        
    def unpack(self,data):
        for name,map in self.map.iteritems():
            if len(map) == 1:
                self.__dict__[name]=data[map[0]]
            else:
                self.__dict__[name]=data[map[0]:map[1]]
    
    def pack(self):
        packed=[self.id]
        i_map=dict(zip(self.map.values(),self.map.keys()))
        locations=self.map.values()
        locations.sort()
        for l in locations:
            value=self.__dict__[i_map(l)]
            if type(value) is int:
                packed.append(value)
            else:
                packed.extend(value)
        return packed
    
    def __str__(self):
        return self.encode()

class ModemStatus(Packet):
    id=0x8a
    map={
         'status':(0,1)
         }
    status_map=[
                'hardware_reset',
                'watchdog_timer_reset',
                'associated',
                'disassociated',
                'synchronization_lost',
                'coordinator_realignment',
                'coordinator_started'
                ]
    
    def __init__(self,data=None):
        self.status=None
        self.unpack(data)
    
    def status(self):
        pass
    
class CallATCommand(Packet):
    id=0x08
    map={
         'frame_id':(0,1),
         'command':(1,3),
         'value':(3,None)
         }
    
    def __init__(self,data=None):
        self.frame_id=None
        self.command=None
        self.value=None
        self.unpack(data)
        
class QueueATCommand(CallATCommand):
    id=0x09
        
class ATResponse(Packet):
    id=0x88
    map={
         'frame_id':(0,1),
         'command':(1,3),
         'value':(3,None)
         }
    
    def __init__(self,data):
        self.frame_id=None
        self.command=None
        self.value=None
        self.unpack(data)
        
class TXRequest64(Packet):
    id=0x00
    map={
         'frame_id':(0,1),
         'destination':(1,9),
         'options':(9,10),
         'data':(10,None)
         }
    
    def __init__(self,data):
        self.frame_id=None
        self.destination=None
        self.options=None
        self.data=None
        self.unpack(data)
    
class TXRequest16(Packet):
    id=0x01
    map={
         'frame_id':(0,1),
         'destination':(1,3),
         'options':(3,4),
         'data':(4,None)
         }
    
    def __init__(self,data):
        self.frame_id=None
        self.destination=None
        self.options=None
        self.data=None
        self.unpack(data)
        
class TXStatus(Packet):
    id=0x89
    map={
         'frame_id':(0,1),
         'status':(1,2)
         }
    
    def __init__(self,data):
        self.frame_id=None
        self.status=None
        self.unpack(data)
     
class RXPacket64(Packet):
    id=0x80
    map={
         'source':(0,8),
         'rssi':(9,10),
         'options':(10,11),
         'data':(11,None)
         }
    
    def __init__(self,data):
        self.source=None
        self.rssi=None
        self.options=None
        self.data=None
        self.unpack(data)
    
class RXPacket16(Packet):
    id=0x81
    map={
         'source':(0,2),
         'rssi':(2,3),
         'options':(3,4),
         'data':(4,None)
         }
    
    def __init__(self,data):
        self.source=None
        self.rssi=None
        self.options=None
        self.data=None
        self.unpack(data)

def encode_frame(data, escape=False, delimiter=0x7e):
    length=len(data)
    length_msB=length>>8
    length_lsB=length&0xff
    checksum=checksum(data)
    data=[length_msB,length_lsB]+data+[checksum]
    if escape:
        data=escape(data)
    data=[delimiter]+data
    return ''.join([chr(b) for b in data])

def decode_frame(data, escaped=False, delimiter=0x7e):
    if type(data) is str:
        data=[ord(c) for c in data]
    if data[0] == delimiter:
        data.pop(0)
    if escaped:
        data=unescape(data)
    length_msB=data.pop(0)
    length_lsB=data.pop(0)
    length=(length_msB<<8)|length_lsB
    checksum=data[length]
    data=data[:length]
    if not checksum_ok(data, checksum):
        raise BadChecksum(data,checksum)
    return data
    
def escape(data):
    escaped=[]
    while data:
        byte=data.pop(0)
        if byte in ESCAPED_CHARS:
            escaped.append(0x7d)
            escaped.append(byte^0x20)
        else:
            escaped.append(byte)
    return escaped

def unescape(data):
    unescaped=[]
    while data:
        byte=data.pop(0)
        if byte==0x7d:
            byte=0x20^data.pop(0)
        unescaped.append(byte)
    return unescaped

def checksum(data):
    return 0xff-(sum(data)&0xff)

def checksum_ok(data, checksum=None):
    cs=sum(data)
    if checksum != None:
        cs=cs+checksum
    return cs==0xff

def serial_server(running,frames_in,frames_out):
    with open("../../pyxbee_src/data/9mm/decock.log") as f:
        while running.is_set():
            b=f.read(1)
            if ord(b) == 0x7e:
                length=stack.unpack('>H',f.read(2))[0]
                print('Length:%s'%length)
        
def serial_reader():
    pass

def main():
    packets=list()
    frame_data=list()
    packet_found=False
    with open("../../pyxbee_src/data/9mm/decock.log") as f:
        b=f.read(1)
        while b:
            if ord(b) == 0x7e:
                length=struct.unpack('>H',f.read(2))[0]
                print('Length:%s'%length)
                #payload=f.read(length)
                payload=[ord(chr) for chr in f.read(length)]
                #print('Payload:%s'%payload)
                checksum=f.read(1)
                check=sum(payload)+ord(checksum)
                if check&0xff==0xff:
                    print('Checksum OK')
                else:
                    print('Checksum BAD')

            b=f.read(1)
            print(hex(ord(b)))