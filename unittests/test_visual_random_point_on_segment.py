import sys
sys.path.append('..')

from pycompgeom import *

while True:
	s = VSegment2()
	p = VPoint2(random_point_on_segment(s))
	
