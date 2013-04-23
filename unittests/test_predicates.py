from pycompgeom.primitives import *
from pycompgeom.predicates import *

import random
import unittest

def random_point():
	return Point2(random.random(), random.random())

class TestPredicates(unittest.TestCase):
	def setUp(self):
		self.a = random_point()
		self.b = random_point()
		self.c = random_point()
		
	def test_cw_vs_ccw(self):
		self.assertFalse(cw(self.a,self.b,self.c) and ccw(self.a,self.b,self.c))
		self.assertFalse(cwon(self.a,self.b,self.c) and ccwon(self.a,self.b,self.c))

if __name__ == '__main__':
	unittest.main(verbosity=2)
