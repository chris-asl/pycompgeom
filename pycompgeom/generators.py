import random
from itertools import combinations

from primitives import *
from visuals import *
from colors import *
from predicates import *
from events import *

def random_points_in_window(num, window_size=WINSIZE, offset=20):
	maxx, maxy = window_size
	points = []
	i=0
	while i<=num:
		x = int(random.random()*maxx)
		y = int(random.random()*maxy)
		while not (offset < x < maxx - offset):
			x = int(random.random()*maxx)
		while not (offset < y < maxy - offset):
			y = int(random.random()*maxy)
		points.append(Point2(x,y))
		i += 1
	return points

def random_points(num=15, color=RED, visual=False):
	points = random_points_in_window(num)
	if visual:
		vpoints = []
		for p in points:
			vpoints.append(VPoint2(p, color=color, update_window=False))
		window.point_background_is_dirty = True
		return vpoints
	else:
		return points

def random_simple_polygon(num=20, color=WHITE, visual=False):
	pygame.display.set_caption("Generating random simple polygon. Please wait ...")
	points = random_points_in_window(num)
	poly = Polygon2(points)
	done = False
	while not done:
		for e, f in combinations(poly.edges,2):
			if intersects(e, f) and e.end <> f.start:
				a, b = points.index(e.start), points.index(e.end)
				c, d = points.index(f.start), points.index(f.end)
				points[b], points[c] = points[c], points[b]
				poly = Polygon2(points)
		done = True
		for e, f in combinations(poly.edges,2):
			if intersects(e,f) and e.end <> f.start:
				done = False
	# makes polygon counterclockwise	
	#if poly.is_clockwise_oriented():
	#	vv = reversed([x for x in poly.vertices])
	#	poly = Polygon2(vv)
	#	return poly
	if poly.is_clockwise_oriented():
		poly.convert_to_ccw()
	pygame.display.set_caption('pyCompGeom window')
	return poly


def segments_from_points(points, color=WHITE):
	n = len(points)
	if n > 1:
		starts = points[:-1]
		ends = points[1:]
		segments = [VSegment2.from_endpoints(start, end, color=color) for start,end in zip(starts, ends)]
		window.segment_background_is_dirty = True
		return segments
	return []

def random_segments(num=15, color=RED, size=WINSIZE, visual=False):
	print "Generating %s random segments ..." % num,
	p1, p2 = random_points(num), random_points(num)
	
	if visual:
		segments = [VSegment2(Segment2(x,y), color=color, update_window=False) for x,y in zip(p1,p2)]
	else:
		segments = [Segment2(x,y) for x,y in zip(p1,p2)]
	
	if visual:
		window.segment_background_is_dirty = True
	print "Done"
	return segments

def random_point_on_segment(segment):
	start, end = segment.start, segment.end
	l = random.random()
	x = l * (start.x - end.x)
	y = l * (start.y - end.y)
	return Point2(start.x - x, start.y - y)
