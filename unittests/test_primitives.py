from pycompgeom.primitives import Point2, Segment2, Polygon2

import random
import unittest

def random_point():
	return Point2(random.random(), random.random())

class TestPrimitiveInstantiations(unittest.TestCase):
	def setUp(self):
		pass
		
	def test_Point2(self):
		a = random_point()
		b = a.from_point2(a)
		c = a.from_tuple(b.coordinates)
		self.assertEqual(a, b)
		self.assertEqual(a, c)
		self.assertEqual(b, c)
		d = Point2(7.5435543, 8.234234)
		e = Point2(7.54356, 9.534525)
		self.assertTrue(d<e)
		
	def test_Segment2(self):
		a = random_point()
		b = random_point()
		s1 = Segment2(a, b)
		s2 = Segment2.from_segment2(s1)
		self.assertEqual(s1.start, s2.start)
		self.assertEqual(s1.end, s2.end)
		self.assertEqual(s1, s2)

if __name__ == '__main__':
	unittest.main(verbosity=2)
