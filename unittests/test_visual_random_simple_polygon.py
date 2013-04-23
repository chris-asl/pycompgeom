import sys
sys.path.append('..')

from pycompgeom import *

while True:
	poly = random_simple_polygon()

	i = poly.index(min(poly.vertices))
	p = VPolygon2(poly)
	pp = VPoint2(poly[i], color=RED)
	qq = VPoint2(poly[(i+1)%len(poly)], color=GREEN)
	rr = VPoint2(poly[(i+2)%len(poly)], color=BLUE)
	
	if p.orientation == 'clockwise':
		print "clockwise poly detected"
		print "hit any key to see the same polygon oriented counter clockwise"
	else:
		print "you've got a nice counter-clockwise polygon!"
	
	pause()
	
	poly.convert_to_ccw()
	p = VPolygon2(poly)
	
	i = poly.index(min(poly.vertices))
	p = VPolygon2(poly)
	pp = VPoint2(poly[i], color=RED)
	qq = VPoint2(poly[(i+1)%len(poly)], color=GREEN)
	rr = VPoint2(poly[(i+2)%len(poly)], color=BLUE)
	
	pause()
	
	del p, poly
