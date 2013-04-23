import sys
sys.path.append("..")

from pycompgeom import *

p1 = getVPolygon(convex=True)
p2 = getVPolygon(convex=True)

def find_bridge(poly1, poly2, upper=True):
	max_p1, min_p2 = max(poly1.vertices), min(poly2.vertices)
	i, j = poly1.index(max_p1), poly2.index(min_p2)
	s = VSegment2.from_endpoints(p1[i], p2[j]); pause()
	
	bridge_found = False
	while not bridge_found:
		if upper:
			if not ccw(poly1[i], poly1[i+1], poly2[j]):
				i += 1
				i_changed = True
				s = VSegment2.from_endpoints(p1[i], p2[j]); pause()
			else:
				i_changed = False
			if not cw(poly2[j], poly2[j-1], poly1[i]):
				j -= 1
				j_changed = True
				s = VSegment2.from_endpoints(p1[i], p2[j]); pause()
			else:
				j_changed = False
		else:
			if not cw(poly1[i], poly1[i-1], poly2[j]):
				i -= 1
				i_changed = True
				s = VSegment2.from_endpoints(p1[i], p2[j]); pause()
			else:
				i_changed = False
			if not ccw(poly2[j], poly2[j+1], poly1[i]):
				j += 1
				j_changed = True
				s = VSegment2.from_endpoints(p1[i], p2[j]); pause()
			else:
				j_changed = False
		bridge_found = not i_changed and not j_changed
	
	return Segment2(poly1[i], poly2[j])
	
upper_bridge = VSegment2(find_bridge(p1, p2, True), color=BLUE)
lower_bridge = VSegment2(find_bridge(p1, p2, False), color=GREEN)
pause()

