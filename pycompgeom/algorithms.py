from primitives import *
from predicates import *
import random

def jarvis(points):
	r0 = min(points)
	hull = [r0]
	r = r0
	while True:
		u = random.choice(points)
		for t in points:
			if cw(r, u, t) or collinear(r, u, t) and between(r, t, u):
				u = t
		if u == r0: break
		else:
			r = u
			points.remove(r)
			hull.append(r)
	return hull

def find_bridge(poly1, poly2, upper=True):
	max1, min2 = max(poly1.vertices), min(poly2.vertices)
	i, j = poly1.index(max_p1), poly2.index(min_p2)
	
	bridge_found = False
	while not bridge_found:
		if upper:
			if not ccw(poly1[i], poly1[i+1], poly2[j]):
				i += 1; i_changed = True
			else: i_changed = False
			if not cw(poly2[j], poly2[j-1], poly1[i]):
				j -= 1; j_changed = True
			else: j_changed = False
		else:
			if not cw(poly1[i], poly1[i-1], poly2[j]):
				i -= 1; i_changed = True
			else: i_changed = False
			if not ccw(poly2[j], poly2[j+1], poly1[i]):
				j -= 1; j_changed = True
			else: j_changed = False
		bridge_found = not i_changed and not j_changed
	
	return Segment2(poly1[i], poly2[j])

def andrew(points, return_hull=True):
	upper = []
	lower = []
	for point in sorted(points):
		while len(upper) > 1 and ccwon(upper[-2], upper[-1], point):
			upper.pop()
		while len(lower) > 1 and cwon(lower[-2], lower[-1], point):
			lower.pop()
		upper.append(point)
		lower.append(point)
	if return_hull:
		return lower[:-1]+ [x for x in reversed(upper[1:])]
	else:
		return upper, lower

def andipodal_pairs(points):
	U, L = andrew(points, return_hull=False)
	i, j = 0, len(L)-1
	while i<len(U)-1 or j>0:
		yield U[i], L[j]
		if i == len(U)-1: j -= 1
		elif j == 0: i += 1
		elif (U[i+1].y-U[i].y) * (L[j].x-L[j-1].x) > \
				(L[j].y-L[j-1].y) * (U[i+1].x-U[i].x):
			i += 1
		else: j -= 1
			
def diameter(points):
	dlist = [((p.x-q.x)**2+(p.y-q.y)**2,(p,q)) \
		for p,q in antipodal_pairs(points)]  
	diam, pair = max(dlist)
	return pair
