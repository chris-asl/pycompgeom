from pycompgeom.primitives import *
from pycompgeom.predicates import *
from pycompgeom.algorithms import *

import pycompgeom.algorithms

import random
import unittest

def random_point():
	return Point2(random.random(), random.random())

points0 = [Point2(i/10, i%10) for i in range(100)]
result0 = [Point2(0,0), Point2(9,0), Point2(9, 9), Point2(0,9)]

points1 = [Point2(i, i) for i in range(100)] + [Point2(99,0)]
result1 = [Point2(0,0), Point2(99,0), Point2(99,99)]

points2 = [Point2(i, i) for i in range(100)] + [Point2(i+1, i) for i in range(100)]
result2 = [Point2(0,0), Point2(1,0), Point2(100, 99), Point2(99,99)]


class TestHullAlgorithms(unittest.TestCase):
	
	def test_jarvis(self):
		self.assertEqual(jarvis(points0[:]), result0)
		self.assertEqual(jarvis(points1[:]), result1)
		self.assertEqual(jarvis(points2[:]), result2)
		
	def test_andrew(self):
		self.assertEqual(andrew(points0[:]), result0)
		self.assertEqual(andrew(points1[:]), result1)
		self.assertEqual(andrew(points2[:]), result2)
		
	def test_andrew_equals_jarvis(self):
		self.assertEqual(andrew(points0[:]), jarvis(points0[:]))
		self.assertEqual(andrew(points1[:]), jarvis(points1[:]))
		self.assertEqual(andrew(points2[:]), jarvis(points2[:]))
		

if __name__ == '__main__':
	unittest.main(verbosity=2)
