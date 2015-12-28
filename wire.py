'''
Created on Dec 22, 2015

@author: jdasilva
'''


import unittest

from element import Element
from __builtin__ import isinstance


class Wire(Element):
    '''
    Wire generation class
    '''
    
    __wire_count = 0
    DEFAULT_WIRE_WIDTH = 1
    
    def __init__(self, name=None, parent=None, width=None, connectTo=None):
        '''
        Wire Constructor
        '''
        super(Wire,self).__init__(parent)
        
        if name is not None:
            self.name = name
        
        self.width = width;
        
        self.connectedTo = connectTo
        
    def __sanitize(self):
        
        if self.name is None:
            self.name = "wire" + str(Wire.__wire_count)
            Wire.__wire_count += 1
            
        if self.width is None:
            self.width = Wire.DEFAULT_WIRE_WIDTH
            
        if self.width <= 0:
            raise ValueError('wire width less than or equal to 0 is not valid.')
        
        
    def __normalizeWidth(self, name, destWidth, srcWidth):
        
            if destWidth is None:
                return name
        
            if srcWidth is None:
                srcWidth = destWidth
        
            minwidth = min(destWidth,srcWidth)
            
            if minwidth == 1:
                index = "[0]"
            else:
                index = "[" + str(minwidth-1) + ":0]"
                            
            name = name + index 
            
            if minwidth < destWidth:
                # ToDo: should consider sign extending here rather than assigning all high order bits to zero
                name = "{{(" + str(destWidth) + "-" + str(minwidth) + "){1'b0}}, " + name + "}" 
            
            return name
    
    
    def nameOrValue(self,width=None):
        
        if self.name is not None:
            return self.__normalizeWidth(self.name,width,self.width)
        else:
            return self.value(width)
    
    def value(self,width=None):
        
        if width is None:
            width = self.width
                    
        if self.connectedTo is None:
            raise ValueError('attempting to get value of a wire with no value')
        
        if isinstance(self.connectedTo, basestring):
                        
            all_ones_list = ["allones", "ones", "one", "allhigh", "high", "true", "~0"]
            all_zeros_list = ["allzeros", "zeros", "zero", "alllow", "low", "false", "0"]
                        
            if self.connectedTo.lower() in all_ones_list:
                if width is None:
                    return "~0"
                elif width == 1:
                    return "1'b1"
                else:
                    return "{(" + str(width) + "){1'b1}}"
                   
            if self.connectedTo.lower() in all_zeros_list:
                if width is None:
                    return "0"
                elif width == 1:
                    return "1'b0"
                else:
                    return "{(" + str(width) + "){1'b0}}"
                
            return self.connectedTo
        
        if isinstance(self.connectedTo, int):
            if width is None:
                return str(self.connectedTo)
            else:
                return self.hdlwriter.toHDLhex(self.connectedTo, width)
        
        
        if isinstance(self.connectedTo, Wire):

            minwidth = width
            if self.connectedTo.width is not None:
                minwidth = min(width, self.connectedTo.width)            
            
            if self.connectedTo.name is None:
                if self.connectedTo.isConnected():
                    val = self.connectedTo.value(minwidth)
                else:
                    raise ValueError('Dangling Wire...')
            else:
                val = self.connectedTo.name
            
            return self.__normalizeWidth(val,width,minwidth)
        
        raise ValueError('wire value has an unknown type')
    
    def isConnected(self):
        return self.connectedTo is not None
    
    def __generateHDLAssignement(self):
        if self.isConnected():
            self.hdlwriter.wireAssign(self.name, self.value())
            
    def generateHDL(self):
        self.__sanitize()        
        self.hdlwriter.wireDecl(self.name,self.width)
        self.__generateHDLAssignement()   
    

class ConditionalWire(Wire):

    def __init__(self, name=None, parent=None, width=None, condExpr=None, connectToTrue=None, connectToFalse=None):
        '''
        Conditional Wire Constructor
        '''
        super(ConditionalWire,self).__init__(name=name, parent=parent, width=width, connectTo=None)

        self.condExpr = condExpr        
        self.connectedToTrue = connectToTrue
        self.connectedToFalse = connectToFalse

    def isConnected(self):
        return True
    
    def value(self,width=None):
                
        if width is None:
            width = self.width
                    
        if self.condExpr is None:
            raise ValueError('attempting to get value of a conditional wire with no conditional expression')

        if self.connectedToTrue is None:
            raise ValueError('attempting to get value of a conditional wire with nothing connected if expression is true')

        if self.connectedToFalse is None:
            raise ValueError('attempting to get value of a conditional wire with nothing connected if expression is false')
        
        if not isinstance(self.condExpr, Wire):
            self.condExpr = Wire(parent=self, width=1,connectTo=self.condExpr)
        
        if not isinstance(self.connectedToTrue, Wire):
            self.connectedToTrue = Wire(parent=self, connectTo=self.connectedToTrue)

        if not isinstance(self.connectedToFalse, Wire):
            self.connectedToFalse = Wire(parent=self, connectTo=self.connectedToFalse)

        return "(" + self.condExpr.value() + ") ? " + self.connectedToTrue.nameOrValue(width=width) + " : " + self.connectedToFalse.nameOrValue(width=width)
    

class TestWire(unittest.TestCase):
    
    def testWireCreate(self):
        w = Wire()
        self.assertNotEqual(w, None)
        pass
    
    def testWireGenerate(self):
        w = Wire()
        w.generateHDL()
        
        w.width = 101
        w.generateHDL()
        
        w.name = "my_wire"
        w.generateHDL()

        pass

    def testWireEqualsGenerate(self):
        
        w1 = Wire(name="gretzky", width=99, connectTo="allones")
        w1.generateHDL()

        w2 = Wire(name="nowidth", connectTo="ones")
        self.assertEquals(w2.value(), "~0")

        w3 = Wire(width=40, connectTo=-1)
        self.assertEquals(w3.value(), "40'hffffffffff")
        w3.generateHDL()

        w4 = Wire(width=2, connectTo=7)
        self.assertEquals(w4.value(), "2'h3")
        w4.generateHDL()

        w5 = Wire(width=257, connectTo=-2)
        self.assertEquals(w5.value(), "257'h1fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe")
        w5.generateHDL()

        w6 = Wire(width=4, connectTo=w5)
        w6.generateHDL()

        w7 = Wire(name="truncate", width=6, connectTo=w6)
        w7.generateHDL()

        pass


class TestConditionalWire(unittest.TestCase):
    
    def testCondWireCreate(self):
        w = ConditionalWire(condExpr="a==b",connectToTrue="allones",connectToFalse="allzeros")
        w.name = "conditional_wire"
        w.width = 10;
        w.generateHDL()
        
        w.connectedToTrue = Wire(name="foo",width=8)
        w.generateHDL()
        
        w.connectedToFalse = Wire(name="bar",width=4)
        w.generateHDL()
        
        w2 = ConditionalWire(width=8, condExpr="b==c",connectToTrue=w,connectToFalse="allzeros")
        w2.generateHDL()
        w2.width = 100
        w2.generateHDL()
        
        w.name = None
        w2.generateHDL()
        
        w2.width = 5
        w2.connectedToFalse = 0xfa
        w2.generateHDL()
        
        
        pass
    
        