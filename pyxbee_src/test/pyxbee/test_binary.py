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
        
    def testIter(self):
        for byte in self.bytes:
            self.assertTrue(isinstance(byte,binary.Bytes))
    
    def testBitCast(self):
        bits = self.bytes.bits()
        self.assertTrue(isinstance(bits, binary.Bits))

class BitsTestCase(unittest.TestCase):
    
    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()