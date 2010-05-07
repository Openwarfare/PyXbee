import struct
import Queue
import copy
import logging as log
#TODO: Think about reworking most of this.  It might be better to work with strings 
#directly rather than breaking them up into lists only to turn them back into strings
#TODO: Investigate dealing with these in a byte by byte manner for encoding.  It may 
#be more efficient
#TODO: Think about moving the packet_ids and escaped chars into a modem specific class
#that can be swapped out when hardware changes.
#TODO:Redo maps so the are an ordered list of elements with a length and a type for easier mapping

ESCAPED_CHARS=[0x7e,0x7d,0x11,0x13]

class BadFrameLength(Exception):
    data=None
    length=None
    def __init__(self,data=None, length=None):
        self.data=data
        self.length=length
        
class BadFrameChecksum(Exception):
    checksum=None
    data=None
    def __init__(self,data=None, checksum=None):
        self.checksum=checksum
        self.data=data
    
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

class FrameIdPacket(Packet):
    current_id=0
    
    def generateFrameId(self):
        if FrameIdPacket.current_id == 255:
           FrameIdPacket.current_id=0
        else: 
            FrameIdPacket.current_id=FrameIdPacket.current_id+1
        return FrameIdPacket.current_id
    
class ModemStatus(Packet):
    id=0x8a
    map={
         'status':(0,1)
         }
    
    status_names=[
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
    
    def named_status(self):
        return self.status_names[self.status]
    
class CallATCommand(Packet):
    id=0x08
    map={
         'frame_id':(0,1),
         'command':(1,3),
         'value':(3,None)
         }
    
    def __init__(self,data=None,command=None,frame_id=None):
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
         'status':(4,5),
         'value':(5,None)
         }
    
    def __init__(self,data):
        self.frame_id=None
        self.command=None
        self.status=None
        self.value=None
        self.unpack(data)
    
    def ok(self):
        return not bool(self.status)
    
    def error(self):
        return bool(self.status)
        
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
        self.options=0x00
        self.data=None
        self.unpack(data)
    
    def disable_ack(self):
        self.options=self.options | 0x01
    
    def broadcast_pan_id(self):
        self.options=self.options | 0x04
        
class TXRequest16(TXRequest64):
    id=0x01
    map={
         'frame_id':(0,1),
         'destination':(1,3),
         'options':(3,4),
         'data':(4,None)
         }
        
class TXStatus(ModemStatus):
    id=0x89
    map={
         'frame_id':(0,1),
         'status':(1,2)
         }
    
    status_names=[
                  'success',
                  'no_ack',
                  'cca_failure',
                  'purged'
                  ]
    
    def __init__(self,data):
        self.frame_id=None
        self.status=None
        self.unpack(data)
     
class RXPacket64(Packet):
    id=0x80
    map={
         'source_address':(0,8),
         'rssi':(9,10),
         'options':(10,11),
         'data':(11,None)
         }
    
    io_map={
            'samples':(0,1),
            'channels':(1,3),
            'io_data':(4,None)
            }
    
    channel_map={
                'adc5':0x4000,
                'adc4':0x2000,
                'adc3':0x1000,
                'adc2':0x800,
                'adc1':0x400,
                'adc0':0x200,
                'dio8':0x100,
                'dio7':0x80,
                'dio6':0x40,
                'dio5':0x20,
                'dio4':0x10,
                'dio3':0x8,
                'dio2':0x4,
                'dio1':0x2,
                'dio0':0x1
                }
    
    option_names={
             'address_broadcast':0x40,
             'pan_broadcast':0x20
             }
    
    def __init__(self,data):
        self.source=None
        self.rssi=None
        self.options=0
        self.data=None
        self.unpack(data)
    
    def named_options(self):
        result=[]
        for name, value in self.option_names.iteritems():
            if self.options & value:
                result.append(name)
        return result
    
    def add_option(self,option):
        if isinstance(option,str):
            option=self.option_names(option)
        self.options=self.options | option
    
    def unpack_io(self):
        pass
    
class RXPacket16(RXPacket64):
    id=0x81
    map={
         'source_address':(0,2),
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

class RXIOPacket64(RXPacket64):
    id=0x82
    
class RXIOPacket16(RXPacket16):
    id=0x83
    
def ensure_chr(byte):
    if type(byte) is int:
        return chr(byte)
    return byte

def encode_frame(data, escape=False, delimiter=0x7e):
    length=len(data)
    length_msB=length>>8
    length_lsB=length&0xff
    checksum=checksum(data)
    data=[length_msB,length_lsB]+data+[checksum]
    if escape:
        data=escape(data)
    data=[delimiter]+data
    return ''.join([ensure_chr(b) for b in data])

def decode_frame(data, escaped=False, delimiter=0x7e, ignore_checksum=False):
    if type(data) is str:
        data=[ord(c) for c in data]
    if data[0] == delimiter:
        data.pop(0)
    if escaped:
        data=unescape(data)
    length_msB=data.pop(0)
    length_lsB=data.pop(0)
    length=(length_msB<<8)|length_lsB
    if length > len(data)-1:
        raise BadFrameLength(data=data, length=length)
    checksum=data[length]
    data=data[:length]
    if not checksum_ok(data, checksum) and not ignore_checksum:
        raise BadFrameChecksum(data,checksum)
    return data

def decode_packet(data):
    pass
    
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
            0x82:RXIOPacket64,
            0x83:RXIOPacket16
            }

def main():
    frame_out=None
    raw_frame=None
    with open("../../pyxbee_src/data/9mm/five_aimed_fc_5.log") as f:
        b=f.read(1)
        offset=1
        while b:
            if ord(b) == 0x7e:
                if raw_frame != None:
                    try:
                        #print(frame_out)
                        frame_out=decode_frame(raw_frame, ignore_checksum=False)
                    except BadFrameChecksum as cs:
                        print('Bad Checksum:%s at %s for %s'%(cs.checksum,offset,cs.data))
                    except BadFrameLength as ip:
                        print('Bad Frame Length:%s at %s for %s'%(ip.length,offset,ip.data))
                raw_frame=b
            else:
                if raw_frame != None:
                    raw_frame+=b
            b=f.read(1)
            offset+=1
        
if __name__ == '__main__':
    main()