'''
Created on Dec 22, 2015

@author: jdasilva
'''
import sys
import unittest


class HDLWriter():
    '''
    class to help with hdl code generation
    '''

    def __init__(self, stream=sys.stdout):
        self.stream = stream;
        return
    
    def write(self, text):
        self.stream.write(text)
    
    def newline(self):
        self.write("\n")
    
    def comment(self, comment, ):
        self.write("// " + comment + "\n")
        
    def tohex(self, val, nbits, signed=True):
        
        if signed:
            val = (val + (1 << nbits)) % (1 << nbits)
        val = val & ((1 << nbits)-1)
        return hex(val).rstrip("L").lstrip("0x")
    
    def toHDLhex(self, val, width, signed=True):
        return str(width) + "'h" + self.tohex(val, width)
    
    def wireDecl(self, name, width=1):
        
        if width <= 0:
            raise ValueError('wire width less than or equal to 0 is not valid.')
        
        self.write("wire ");
        if width > 1:
            self.write("[" + str(width-1) + ":0] " )
        self.write(name + ";\n");
    
    def wireAssign(self, wirename, wirevalue):

        self.write("assign " + wirename + " = " + wirevalue + ";\n")


    def moduleInst(self, moduleName, moduleInstName, ports={}, parameters={}):
        
        self.write(moduleName)
        if len (parameters) > 0:
            self.write(" #(\n")
            
            numOfParamsLeft = len(parameters)
            
            for p in parameters:
                self.write("      ." + p + "(" + parameters[p] + ")")
                numOfParamsLeft -= 1
                if numOfParamsLeft > 0:
                    self.write(",")
                self.write("\n")
    
            self.write("  )")
            
        self.write(" " + moduleInstName)
        self.write(" (")
        
        if len(ports) > 0:
            self.write("\n")

        numOfPortsLeft = len(ports)        
        for p in ports:
            self.write("      ." + p + " (" + ports[p] + ")")
            numOfPortsLeft -= 1
            if numOfPortsLeft > 0:
                self.write(",")
            self.write("\n")
            
        if len(ports) > 0:
            self.write("  ")
                   
        self.write(");\n")

        
    
       
class TestHDLWriter(unittest.TestCase):
    
    def testWireDecl(self):

        HDLWriter().wireDecl("foo", 1)
        HDLWriter().wireDecl("foobar", 100)

        try:
            HDLWriter().wireDecl("foobar", 0)
        except ValueError:
            pass
            return
        
        self.assertTrue(False, "Should not reach here")

    def testModuleInst(self):
        
        HDLWriter().moduleInst("mymodule", "mymodule_inst")

        HDLWriter().moduleInst("mymodule", "mymodule_inst", parameters={'FOO':'1','BAR':'0'})

        HDLWriter().moduleInst("mymodule", "mymodule_inst", ports={'clock':'clk','resetn':'rstn'}, parameters={'FOO':'1','BAR':'0','FOOBAR':'X'})

        
        pass