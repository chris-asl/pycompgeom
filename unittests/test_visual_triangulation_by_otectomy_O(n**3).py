import sys
sys.path.append('..')

from pycompgeom import *

def diagonal(segment, polygon):
	for edge in polygon.edges:
		if segment.start <> edge.start and segment.start <> edge.end \
			and segment.end <> edge.start and segment.end <> edge.end:
			if intersects(edge, segment):
				return False
	return True

def is_internal(diagonal, polygon):
	i, j = polygon.index(diagonal.start), polygon.index(diagonal.end)
	n = len(polygon)
	i1, in1 = (i+1) % n, (i+n-1) % n
	if ccwon(polygon[in1], polygon[i], polygon[i1]):
		return ccw(polygon[i], polygon[j], polygon[in1]) and ccw(polygon[j], polygon[i], polygon[i1])
	else:
		return cw(polygon[i], polygon[j], polygon[i1]) or cw(polygon[j], polygon[i], polygon[in1])

def is_internal_diagonal(segment, polygon):
	return diagonal(segment, polygon) and is_internal(segment, polygon)

def triangulate2(polygon):
	vertices = [vertex for vertex in polygon.vertices]
	diagonals = []
	while len(vertices) > 3:
		n = len(vertices)
		for i in range(n):
			segment = Segment2(vertices[i], vertices[(i+2) % n])
			if is_internal_diagonal(segment, polygon):
				diagonals.append(segment)
				del (vertices[(i+1) % n])
				break
	return diagonals

poly = random_simple_polygon(25)
if poly.is_clockwise_oriented():
	poly.convert_to_ccw()
p = VPolygon2(poly,color=GREEN)
vdiags = []
for s in triangulate2(poly):
	vdiags.append(VSegment2(s, color=RED))
pause()
del vdiags, p
