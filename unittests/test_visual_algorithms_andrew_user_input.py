import sys
sys.path.append('..')

from pycompgeom import *
import time

def andrew(points):
	upper = []
	lower = []
	vupper = []
	vlower =[]
	for point in sorted(points):
		while len(upper) > 1 and ccwon(upper[-2], upper[-1], point):
			upper.pop()
		while len(lower) > 1 and cwon(lower[-2], lower[-1], point):
			lower.pop()
		upper.append(point)
		lower.append(point)
		vupper = segments_from_points(upper, color=RED)
		vlower = segments_from_points(lower, color=BLUE)
		time.sleep(.1)
	return lower[:-1]+ [x for x in reversed(upper[1:])]

points = getVPoints()
hull = VPolygon2(Polygon2(andrew(points)))
pause()
