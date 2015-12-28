'''
Created on Dec 22, 2015

@author: jdasilva
'''

import unittest

from element import Element
from wire import Wire, ConditionalWire


class Register(Element):
    '''
    Register generation class
    '''
    
    __reg_count = 0;
    DEFAULT_REGISTER_WIDTH = 32
    DEFAULT_REGISTER_ADDRESS_WIDTH = 32

    def __init__(self, name=None, parent=None):
        '''
        Simple Constructor
        '''
        super(Register,self).__init__(parent)
        
        if name is not None:
            self.name = name
        
        self.width = None
        self.addrwidth = None
        self.readonly = False
        

    def __sanitize(self):
                
        if self.name is None:
            self.name = "reg" + str(Register.__reg_count)
            Register.__reg_count += 1
            
        if self.width is None:
            self.width = Register.DEFAULT_REGISTER_WIDTH
        
        if self.width <= 0:
            raise ValueError('register width less than or equal to 0 is not valid.')
        
        self._widthInBytes = self.width / 8
        if (self.width % 8 != 0):
            self._widthInBytes += 1
  
        if self.addrwidth is None:
            # ToDo: get this value from parent element if you have a parent
            self.addrwidth = Register.DEFAULT_REGISTER_ADDRESS_WIDTH


    def generate(self):                
        self.__sanitize()
        
        
    def generateHDL(self):
        
        self.__sanitize()
         
        self.hdlwriter.newline()
        self.hdlwriter.comment("********************************")
        self.hdlwriter.comment("Register: " + self.name)
        if self.address:
            self.hdlwriter.comment("Address: " + hex(self.address))        
                        
        read_data_wire = Wire(name=self.name, parent=self, width=self.width)
        read_data_wire.generateHDL()
        
        chip_select_wire = Wire(name=str(self.name + "_chip_select"), parent=self)
        if self.address:            
            # ToDo make this an input port
            address_wire = Wire(name="address", width=self.addrwidth, parent=self)
            condionalExpression = address_wire.name + " == " + self.hdlwriter.toHDLhex(self.address, self.addrwidth, signed=False)
            chip_select_wire.connectedTo = ConditionalWire(parent=self, condExpr=condionalExpression, connectToTrue="one", connectToFalse="zero") 
        else:
            chip_select_wire.connectedTo = "true"
        chip_select_wire.generateHDL()
                
        self.hdlwriter.newline()
        

        if (self._widthInBytes * 8) != self.width: 
            writedata_str = "{{(" + str(self._widthInBytes*8) + "-" + str(self.width) + ") {1'b0}}, writedata[" + str(self.width) + ":0]}"
        else:
            writedata_str = "writedata"
        
        self.hdlwriter.moduleInst("callie_reg", self.name + "_register", 
                                  parameters={
                                    "REGISTER_SIZE":str(self._widthInBytes*8)
                                    },
                                  ports={
                                    "clock":"clk",
                                    "resetn":"resetn",
                                    "write":"write",
                                    "chip_select":self.name + "_chip_select",
                                    "byteenable":"byteenable[" + str(self._widthInBytes-1) + ":0]",
                                    "writedata":writedata_str,
                                    "read_data":read_data_wire.name,
                                    }
                                  )
                
        self.hdlwriter.comment("********************************")
        self.hdlwriter.newline()



class TestRegister(unittest.TestCase):
    
    def testRegisterCreate(self):
        r = Register()
        self.assertNotEqual(r, None)
        self.assertEqual(r.name, None)
        
        r.name = "reg1"
        self.assertEqual(r.name, "reg1")
        self.assertEqual(r.width, None)
        
        namedReg = Register("noname")
        self.assertEqual(namedReg.name, "noname")
        
        pass
    
    def testRegisterWidthInBytes(self):
        
        r = Register()
        r.generate()
        self.assertEqual(r.width, 32)
        self.assertEqual(r._widthInBytes, 4)

        r.width = 31
        r.generate()
        self.assertEqual(r.width, 31)
        self.assertEqual(r._widthInBytes, 4)
        
        r.width = 1
        r.generate()
        self.assertEqual(r.width, 1)
        self.assertEqual(r._widthInBytes, 1)
        
        r.width = 8
        r.generate()
        self.assertEqual(r.width, 8)
        self.assertEqual(r._widthInBytes, 1)

    
    def testGenerateHDL(self):
        r = Register("command")
        r.address = 0x04
        self.assertEqual(r.width, None)
        self.assertEqual(r.addrwidth, None)
        r.generateHDL()
        self.assertEqual(r.width, 32)
        self.assertEqual(r.addrwidth, 32)
        
        r.width = 10
        r.addrwidth = 3
        r.generateHDL()
        self.assertEqual(r.addrwidth, 3)
        
        
    def testGenerateWideRegisterHDL(self):
        
        r = Register()
        r.name = "widereg"
        r.width = 256
        r.addrwidth = 10
        r.generateHDL()
        
        pass
    
    