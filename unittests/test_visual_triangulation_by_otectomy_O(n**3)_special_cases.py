import sys
sys.path.append('..')

from pycompgeom import *

def diagonalie(i,j,P):
	n = len(P)
	for k in range(n):
		k1 = (k+1) % n
		if (k<>i) and (k1<>i) and (k<>j) and (k1<>j):
			if intersects(Segment2(P[i],P[j]),Segment2(P[k],P[k1])):
				return False
	return True
	
def incone(i,j,P):
	n = len(P)
	i1 = (i+1) % n
	in1 = (i+n-1) % n
	if ccwon(P[in1],P[i],P[i1]):
		return ccw(P[i],P[j],P[in1]) and ccw(P[j],P[i],P[i1])
	else:
		return cw(P[i],P[j],P[i1]) or cw(P[j],P[i],P[in1])
		
def diagonal(i,j,P):
	return incone(i,j,P) and diagonalie(i,j,P)
	
def triangulate(polygon):
	P = [x for x in polygon.vertices]
	diags = []
	while len(P)>3:
		n = len(P)
		for i in range(n):
			i1 = (i+1) % n;
			i2 = (i+2) % n;
			if diagonal(i,i2,P):
				diags.append(Segment2(P[i], P[i2]))
				pp = VPolygon2(Polygon2(P), color=BLUE)
				dd = VSegment2(Segment2(P[i], P[i2]), color=RED)
				pause()
				del(P[i1])
				break
	return diags

p = Point2

poly1 = [p(100,100),p(200,100),p(200,200),p(300,300),p(300,200),p(300,100),p(300,100),p(400,400),p(100,500)]
poly2 = [p(1,1),p(2,0),p(2,1),p(2,2),p(3,3),p(3,2),p(3,1),p(3,0),p(4,0),p(4,1),p(4,2),p(4,3),p(4,4),p(5,5),p(0,5)]
poly3 = [p(1,1),p(2,0),p(3,1),p(4,1),p(5,0),p(5,1),p(5,2),p(4,2),p(5,3),p(4,4),p(5,4),p(5,5),p(3,5),p(3,4),p(2,4),p(3,3),p(3,2),p(2,2),p(1,3),p(0,4),p(1,2),p(0,2),p(0,1)]
poly4 = [p(0,0),p(1,0),p(2,0),p(3,0),p(4,0),p(5,0),p(5,1),p(5,2),p(5,3),p(5,4),p(5,5),p(4,5),p(3,5),p(2,5),p(1,5),p(0,5),p(0,4),p(0,3),p(0,2),p(0,1)]

test_cases = [poly1, poly2, poly3, poly4]

def run_testcase(points):
	vp = VPolygon2(Polygon2(points))
	parameter = points[:]
	vdiags = []
	for s in triangulate(Polygon2(parameter)):
		vdiags.append(VSegment2(s, color=RED))
	pause()
			
for case in test_cases:
	run_testcase(case)
