def area2(p, q, r):
	return (r.y-p.y) * (q.x-p.x) - (q.y-p.y) * (r.x-p.x)

def ccw(p, q, r):
	return area2(p, q, r) > 0
	
def ccwon(p, q, r):
	return area2(p, q, r) >= 0
	
def cw(p, q, r):
	return area2(p, q, r) < 0
	
def cwon(p, q, r):
	return area2(p, q, r) <= 0
	
def collinear(p, q, r):
	return area2(p, q, r) == 0
	
def between(p, q, r):
	if not collinear(p, q, r):
		return False
	if p.x != q.x:
		return p.x <= r.x <= q.x or p.x >= r.x >= q.x
	else:
		return p.y <= r.y <= q.y or p.y >= r.y >= q.y

def intersects(s1, s2):
	a, b = s1.start, s1.end
	c, d = s2.start, s2.end
	return ccw(a,c,d) != ccw(b,c,d) and ccw(a,b,c) != ccw(a,b,d)

def volume6(a, b, c, d):
	return \
		a.x * (b.y*c.z - b.z*c.y) + \
		a.y * (b.z*c.x - b.x*c.z) + \
		a.z * (b.x*c.y - b.y*c.x)
		
def orientation(a, b, c, d):
	o = volume6(a, b, c, d)
	if o > 0:
		return 'positive'
	elif o < 0:
		return 'negative'
	else:
		return 'collinear'
		
