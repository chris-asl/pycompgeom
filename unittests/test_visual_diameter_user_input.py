import sys
sys.path.append('..')

from pycompgeom import *

def my_andipodal_pairs(points):
	U, L = andrew(points, return_hull=False)
	print U, L
	i, j = 0, len(L)-1
	while i<len(U)-1 or j>0:
		curr_ij = VSegment2.from_endpoints(U[i], L[j]); pause()
		yield U[i], L[j]
		if i == len(U)-1: j -= 1
		elif j == 0: i += 1
		elif (U[i+1].y-U[i].y) * (L[j].x-L[j-1].x) > \
				(L[j].y-L[j-1].y) * (U[i+1].x-U[i].x):
			i += 1
		else: j -= 1

def diameter(points):
	dlist = [((p.x-q.x)**2+(p.y-q.y)**2,(p,q)) \
		for p,q in my_andipodal_pairs(points)]  
	diam, pair = max(dlist)
	return pair		

points = getVPoints()
d = VSegment2.from_tuple(diameter(points), color=RED)
pause()
