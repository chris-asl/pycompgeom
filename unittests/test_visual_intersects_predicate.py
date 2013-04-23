import sys
sys.path.append('..')

from pycompgeom import *

while True:
	s1 = VSegment2()
	s2 = VSegment2()
	print intersects(s1, s2)
