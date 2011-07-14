import pyxbee.binary as binary

import unittest

class DatamapTestCase(unittest.TestCase):
    
    def setUp(self):
        self.data_string_1 = "add031255"
        self.data_string_2 = "sub132142"
        self.data_nested_string = "inst2"+self.data_string_1+self.data_string_2
    
    def testInit(self):
        dm = binary.Datamap('root')
        self.assertTrue(isinstance(dm,binary.Datamap))
    
    def testSimpleMap(self):
        operation = binary.Datamap('operation')
        operation[0:3] = binary.Datamap('type')
        operation[3:6] = binary.Datamap('num_1',int)
        operation[6:9] = binary.Datamap('num_2',int)
        self.assertEqual("operation:(0:None)\n num_1:(3:6)\n num_2:(6:9)\n type:(0:3)\n", operation.dump_string())
        operation.load(self.data_string_1)
        self.assertEqual('add',operation.type.value())
        self.assertEqual(31,operation.num_1.value())
        self.assertEqual(255,operation.num_2.value())
    
    #TODO:  Add complex map test

class BytesStringTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bytes = binary.Bytes('areth')
        
    def testInit(self):
        bytes = binary.Bytes('areth')
        self.assertEqual('areth',bytes.__repr__())

    def testSlice(self):
        self.assertTrue(isinstance(self.bytes[0:2],binary.Bytes))
        
    def testIter(self):
        for byte in self.bytes:
            self.assertTrue(isinstance(byte,binary.Bytes))
    
    def testBitCast(self):
        bits = self.bytes.bits()
        self.assertTrue(isinstance(bits, binary.Bits))

class BytesIntTestCase(unittest.TestCase):
    
    def setUp(self):
        self.bytes = binary.Bytes(256, int)
        
    def testStringInit(self):
        bytes = binary.Bytes(256)
        self.assertEqual('256',bytes.__repr__())

    def testSlice(self):
        self.assertTrue(isinstance(self.bytes[0:2],binary.Bytes))
        
    def testIteration(self):
        for byte in self.bytes:
            self.assertTrue(isinstance(byte,binary.Bytes))
    
    def testBitCast(self):
        bits = self.bytes.bits()
        self.assertTrue(isinstance(bits, binary.Bits))

class BitsTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def testBitInit(self):
        bits =  binary.Bits('a')
        self.assertEqual("01100001",str(bits))
        
        bits =  binary.Bits(u'a')
        self.assertEqual("01100001",str(bits))
        
        bits =  binary.Bits('areth')
        self.assertEqual("0110000101110010011001010111010001101000",str(bits))
        
        bits =  binary.Bits(u'areth')
        self.assertEqual("0110000101110010011001010111010001101000",str(bits))
        
        bits = binary.Bits(255)
        self.assertEqual("11111111",bits.bit_string)
    
    def testCasting(self):
        bits = binary.Bits('a')
        self.assertEqual(bits.bin(), bin(ord('a')))
        self.assertEqual(bits.hex(), hex(ord('a')))
        self.assertEqual(bits.int(), ord('a'))
        self.assertTrue(isinstance(bits.bytes(), binary.Bytes))
        #TODO::Fix this when bits and bytes have equality operators
        self.assertEqual(str(bits.bytes()), str(binary.Bytes("a")))
    
    def testSlices(self):
        bits =  binary.Bits('areth')
        self.assertEqual("01", str(bits[0:2]))
        bits =  binary.Bits(255)
        self.assertEqual("11111111", str(bits[0:8]))
        bits[0:2] = "00"
        self.assertEqual("00111111", str(bits))
        
    def testIteration(self):
        bits =  binary.Bits('areth')
        test = ""
        for b in bits:
            test += str(b)
        self.assertEqual(test, str(bits))
    
    def testLogic(self):
        bits = binary.Bits(0b10101010)
        self.assertEqual("10101010",str(bits.bitwise_and(binary.Bits(0b11111111))))
        self.assertEqual("11111111",str(bits.bitwise_or(binary.Bits(0b11111111))))
        self.assertEqual("01010101",str(bits.bitwise_xor(binary.Bits(0b11111111))))
        self.assertEqual("00010101",str(bits.bitwise_shift_right(3)))
        self.assertEqual("10101010000",str(bits.bitwise_shift_left(3)))
    
    def testConcatination(self):
        bits = binary.Bits(255)
        self.assertEqual("1111111110101010",str(bits.concatinate(binary.Bits(170))))
        self.assertEqual(65450,bits.concatinate(binary.Bits(170)).int())
                         
if __name__ == '__main__':
    unittest.main()