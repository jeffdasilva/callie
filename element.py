'''
Created on Dec 22, 2015

@author: jdasilva
'''

import unittest
from hdlwrite import HDLWriter


class Element(object):
    '''
    This is the base element atom object for all Callie objects
    '''

    def __init__(self, parent=None):
        '''
        Element Constructor
        '''
        self.name = None
        self.address = None
        self.parent = parent
        self.__hdlwriter = None

    def __sanitize(self):
        raise NotImplementedError('__sanitize method not implemeneted')
        
    @property
    def hdlwriter(self):
                
        if self.__hdlwriter is None:
            
            if self.parent is not None:
                return self.parent.hdlwriter

            self.__hdlwriter = HDLWriter()
            
        return self.__hdlwriter
    
    @hdlwriter.setter
    def hdlwriter(self, writer):
        self.__hdlwriter = writer
    
class TestElement(unittest.TestCase):
    
    def testElementCreate(self):
        e = Element()
        self.assertNotEqual(e, None)
        self.assertEqual(e.name, None)
        pass