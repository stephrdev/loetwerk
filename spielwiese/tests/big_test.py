from calculon import sub, add, op

from unittest import TestCase

class LongTest(TestCase):
    
    def test_apocalypse(self):
        assert(False != True, "God forbid")
    
    def test_dawn(self):
        assert("something" != "something else", "Never!")
        
    def test_failfailfail(self):
        op*op
        
    def test_dumn(self):
        assert False, "Yeah, too easy?"