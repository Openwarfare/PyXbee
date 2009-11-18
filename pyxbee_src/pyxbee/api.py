import struct
import Queue

class Frame:
    data=None

    def checksum(self):
        pass
    
    def length(self):
        pass

    
class Packet:
    type=None
    data=None

escaped_chars=[0x7e,0x7d,0x11,0x13]

def escape(data):
    escaped=[]
    while data:
        byte=data.pop(0)
        if byte in escaped_chars:
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

def serial_server(running,packets_out,packets_in):
    with open("../../pyxbee_src/data/9mm/decock.log") as f:
        while running.is_set():
            b=f.read(1)
            if ord(b) == 0x7e:
                length=stack.unpack('>H',f.read(2))[0]
                print('Length:%s'%length)
        

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
    
if __name__=='__main__':
    #main()
    
    print(hex(checksum([0x23,0x11])))