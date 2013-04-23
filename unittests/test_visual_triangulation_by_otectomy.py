import sys
sys.path.append('..')

from pycompgeom import *

def diagonalie(i,j,P):
	#P = [x for x in polygon.vertices]
	n = len(P)
	for k in range(n):
		k1 = (k+1) % n
		if (k<>i) and (k1<>i) and (k<>j) and (k1<>j):
			if intersects(Segment2(P[i],P[j]),Segment2(P[k],P[k1])):
				return False
	return True
	
def incone(i,j,P):
	#P = [x for x in polygon.vertices]
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
				pp= VSegment2(Segment2(P[i], P[i2]), color=YELLOW)
				pause()
				del(P[i1])
				break
	return diags
			
def earinit(P):
	eardict = {}
	n = len(P)
	for i in range(n):
		i1 = (i+1) % n
		i2 = (i+2) % n
		eardict[P[i1]] = diagonal(i,i2,P)
	return eardict
	
def triangulate2(polygon):
	P = [x for x in polygon.vertices]
	diags = []
	earity = earinit(P)
	while len(P) > 3:
		n = len(P)
		for i in range(n):
			if earity[P[i]]:
				im1 = i-1 
				im2 = i-2
				ip1 = (i+1) % n
				ip2 = (i+2) % n
				diags.append(Segment2(P[im1],P[ip1]))
				earity[P[im1]] = diagonal(im2,ip1,P)
				earity[P[ip1]] = diagonal(im1,ip2,P)
				del(P[i])
				break
	return diags


while True:
	poly = random_simple_polygon(20)
	if poly.is_clockwise_oriented():
		poly.convert_to_ccw()
	p = VPolygon2(poly)
	vdiags = []
	for s in triangulate(poly):
		vdiags.append(VSegment2(s, color=RED))
	pause()
	del poly, p, vdiags
	
