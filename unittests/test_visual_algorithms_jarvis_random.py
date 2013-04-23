import sys
sys.path.append('..')

from pycompgeom import *
import time

def wait():
	time.sleep(0.1)

def jarvis(points):
	r0 = min(points)
	hull = [r0]
	r = r0
	vhull = []
	while True:
		u = random.choice(points)
		curr_ru = VSegment2.from_endpoints(r,u,color=BLUE); wait()
		for t in points:
			curr_ut = VSegment2.from_endpoints(u,t,color=MAGENTA); wait()
			if cw(r, u, t) or collinear(r, u, t) and between(r, t, u):
				curr_ut = VSegment2.from_endpoints(u,t,color=GREEN); wait()
				u = t
				curr_ru = VSegment2.from_endpoints(r,u,color=BLUE); del curr_ut; wait()
			else:
				curr_ut = VSegment2.from_endpoints(u,t,color=RED); wait() 
		if u == r0: break
		else:
			vhull.append(VSegment2.from_endpoints(hull[-1], u, color=YELLOW))
			r = u
			curr_ru = VSegment2.from_endpoints(r,u,color=BLUE); wait()
			points.remove(r)
			hull.append(r)
	vhull.append(VSegment2.from_endpoints(hull[-1], u, color=YELLOW));
	return hull

points = random_points(40, visual=True)
p=VPolygon2(Polygon2(jarvis(points[:])), color=GREEN)
pause()
