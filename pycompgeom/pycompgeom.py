import weakref
import sys
import pygame
import random

BLACK   = pygame.Color(0, 0, 0)
WHITE   = pygame.Color(255, 255, 255)
RED     = pygame.Color(255, 0, 0)
GREEN   = pygame.Color(0, 255, 0)
BLUE    = pygame.Color(0, 0, 255)
YELLOW  = pygame.Color(255, 255, 0)
MAGENTA = pygame.Color(255, 0, 255)
CYAN    = pygame.Color(0, 255, 255)

BACKGROUDCOLOR = BLACK
FOREGROUNDCOLOR = WHITE

DEFAULTPOINTCOLOR = WHITE

WINSIZE = (680, 480)

LEFTBUTTON = 1
MIDDLEBUTTON = 2
RIGHTBUTTON = 3

CIRCLE = 'circle'
RECT = 'rectangle'

PICKSENSITIVITY = 5		

class Point2(object):
	
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	@classmethod
	def fromPoint2(cls, point2):
		return cls(point2.x, point2.y)
		
	@classmethod
	def fromTuple(cls, tup):
		return cls(tup[0], tup[1])
		
	@property
	def coordinates(self):
		return self.x, self.y
		
	def __repr__(self):
		return "Point2(%s,%s)" % (self.x, self.y)
		
	def __eq__(self, other):
		return (self.x, self.y) == (other.x, other.y)
		
	def __ne__(self, other):
		return (self.x, self.y) != (other.x, other.y)
	
	def __lt__(self, other):
		return (self.x, self.y) < (other.x, other.y)
	
	def __gt__(self, other):
		return (self.x, self.y) > (other.x, other.y)
	
	def __le__(self, other):
		return (self.x, self.y) <= (other.x, other.y)
	
	def __ge__(self, other):
		return (self.x, self.y) >= (other.x, other.y)
	
	def __getitem__(self, index):
		return (self.x, self.y)[index]
		
	def __setitem__(self, index, value):
		temp = [self.x, self.y]
		temp[index] = value
		self.x, self.y = temp
		
	def __iter__(self):
		yield self.x
		yield self.y	
	
	def __repr__(self):
		return "Point2(%s, %s)" % (self.x, self.y)

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


class Segment2(object):
	
	def __init__(self, start, end):
		self.start = start
		self.end = end
		
	@classmethod
	def fromSegment2(cls, segment2):
		return cls(segment2.start, segment2.end)
				
	def __repr__(self):
		return "Segment2(%s, %s)" % (self.start, self.end)
		
	def intersectsProperly(self, other):
		a, b = self.start, self.end
		c, d = other.start, other.end
		return intersectProperly(a, b, c, d)
		
class Polygon2(object):
	def __init__(self, vertices=[]):
		""" Here vertices is a list of Point2s or tuples
		"""
		self.__edges = []
		if vertices:
			self.vertices = vertices
			
	def __getitem__(self, index):
		return self.__vertices[index % len(self)]
		
	def __len__(self):
		return len(self.__vertices)
		
	def index(self, item):
		return self.__vertices.index(item)
			
	@property
	def vertices(self):
		for vertex in self.__vertices:
			yield vertex
	@vertices.setter
	def vertices(self, vertices):
		self.__vertices = [Point2.fromPoint2(x) for x in vertices]
		self.__edges = []
		lastvertex = None
		c = self.__vertices[0]
		for v in self.__vertices[1:]:
			s = Segment2(c, v)
			self.__edges.append(s)
			c = v
			lastvertex = v
		if lastvertex:
			# Close the polygon boundary
			self.__edges.append(Segment2(v, self.__vertices[0]))

	@property
	def edges(self):
		for edge in self.__edges:
			yield edge
	
	def bounding_box(self):
		minx,miny=WINSIZE
		maxx=maxy=0
		for v in self.vertices:
			if v.x < minx:
				minx=v.x
			if v.x > maxx:
				maxx=v.x
			if v.y < miny:
				miny=v.y
			if v.y > maxy:
				maxy=v.y
		return minx, maxy, maxx-minx, maxy-miny
	
	def isClockwiseOriented(self):
		if len(self) > 3:
			p = self.__vertices[0]
			q = self.__vertices[1]
			r = self.__vertices[2]
			return cw(p, q, r)
		return False
		
	def isConvex(self):
		for vertex in self.vertices:
			previousVertex = self[self.index(vertex)-1]
			nextVertex = self[self.index(vertex)+1]
			if cw(previousVertex, vertex, nextVertex):
				return False
		return True

def shouldIQuit(event):
	if event.type == pygame.QUIT or \
		event.type == pygame.KEYDOWN \
		and event.key == pygame.K_ESCAPE:
			pygame.quit()
			sys.exit()
	return False
		
def getMouseClick(button=LEFTBUTTON):
	while True:
		event = pygame.event.poll()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == button:
				return event.pos
		elif not shouldIQuit(event):
			event = None

def waitForKeyPress():
	while True:
		event = pygame.event.poll()
		if not shouldIQuit(event):
			if event.type == pygame.KEYDOWN:
				return

def pause():
	pygame.display.set_caption('hit any key to continue ...')
	waitForKeyPress()
	pygame.display.set_caption('pyCompGeom window')

class VPoint2(Point2):
	def __init__(self, point2=None, color=(255,255,255)):
		if point2:
			self.x, self.y = point2.x, point2.y 
		else:
			self.get()
		
		self.color = color
		self.size = 3
		self.surface = pygame.Surface((2*self.size,2*self.size))
		pygame.draw.circle(self.surface, self.color, (self.size, self.size), self.size)
		
		self.surface.set_colorkey((0,0,0))
		self.surface = self.surface.convert_alpha()
		self.is_dirty = True
		catalogue.register(self)
	
	def blit(self, background):
		background.blit(self.surface, self.blitpos())
	
	@property
	def pos(self):
		return window.pygpos((self.x, self.y))
		
	def blitpos(self):
		return self.pos[0]-self.size, self.pos[1]-self.size
		
	#def __del__(self):
	#	screen.isDirty = True
			
	def get(self):
		pos = getMouseClick()
		self.x, self.y = window.cartesian(pos)

def random_points(num=15, color=RED, size=WINSIZE, visual=False):
	print "Generating %s random points ..." % num, 
	maxx, maxy = size
	points = []
	for i in range(num):
		x = int(random.random()*maxx)
		y = int(random.random()*maxy)
		point2 = Point2(x,y)
		if visual:
			points.append(VPoint2(point2,color=color))
		else:
			points.append(point2)
	print "Done"
	return points
		
class VSegment2(Segment2):
	def __init__(self, segment2=None, color=WHITE):
		if segment2:
			self.start, self.end = segment2.start, segment2.end
		else:
			self.get()
			
		self.color = color
		self.surface = pygame.Surface(self.bounding_box())
		sur_width = self.surface.get_width()
		sur_height = self.surface.get_height()
		if (self.start.x < self.end.x and self.start.y < self.end.y) or \
			(self.start.x > self.end.x and self.start.y > self.end.y):
			line_start = (0, sur_height-1)
			line_end = (sur_width-1, 0)
		else:
			line_start = (0,0)
			line_end = (sur_width-1, sur_height-1)
		pygame.draw.line(self.surface, self.color, line_start, line_end, 2)
		self.surface.set_colorkey((0,0,0))
		self.surface = self.surface.convert_alpha()
		self.is_dirty = True
		catalogue.register(self)
		
	def __del__(self):
		window.is_dirty=True
	
	@classmethod
	def fromEndPoints(cls, a, b, color=WHITE):
		return cls(Segment2(a, b), color=color)
	
	def blitpos(self):
		pyg_start = window.pygpos(self.start.coordinates)
		pyg_end = window.pygpos(self.end.coordinates)
		if self.start.x > self.end.x and self.start.y < self.end.y:
			blitx, blity = pyg_end
		elif self.start.x < self.end.x and self.start.y > self.end.y:
			blitx, blity = pyg_start
		elif self.start.x < self.end.x and self.start.y < self.end.y:
			blitx, blity = pyg_start[0], pyg_end[1]
		else:
			blitx, blity = pyg_end[0], pyg_start[1]
		
		return blitx, blity
		
	def blit(self, background):
		background.blit(self.surface, self.blitpos())
		
	def bounding_box(self):
		xsize = abs(self.start.x - self.end.x)
		ysize = abs(self.start.y - self.end.y)
		return xsize, ysize

def segments_from_points(points):
	if len(points) > 1:
		segments = []
		c = points[0]
		for point in points[1:]:
			segments.append(VSegment2.fromEndPoints(c, point))
			c = point
		return segments
	return []
	
class VPolygon2(Polygon2):
	def __init__(self, polygon2=None, color=WHITE):
		self.color = color
		self.vertices = polygon2.vertices
		bbox = polygon2.bounding_box()
		self.blitpos = window.pygpos((bbox[0],bbox[1]))
		self.width, self.height = bbox[2], bbox[3]
		self.surface = pygame.Surface((self.width, self.height))
		_vertices = []
		for v in polygon2.vertices:
			vpos = window.pygpos(v.coordinates)
			_vertices.append((vpos[0]-self.blitpos[0], vpos[1]-self.blitpos[1]))
		#pygame.draw.aalines(self.surface, self.color, True, _vertices, 0)
		pygame.draw.polygon(self.surface, self.color, _vertices, 0)
		self.surface.set_colorkey((0,0,0))
		self.surface = self.surface.convert_alpha()
		self.is_dirty = True
		catalogue.register(self)
		
	def __del__(self):
		window.is_dirty = True
		
	def blit(self, background):
		background.blit(self.surface, self.blitpos)

class GlobalCatalogue(object):
	def __init__(self):
		self.__objects = {\
			VPoint2:[],
			VSegment2:[],
			VPolygon2:[],
		}
		
	def clean(self):
		"""clean the global catalogue of None values
		that represent deleted referants
		"""
		for typ, objlist in self.__objects.iteritems():
			for obj in objlist:
				if not obj():
					del objlist[objlist.index(obj)]
		#for obj in self.__objects:
		#	if not obj():
		#		del self.__objects[self.__objects.index(obj)]
		
	def register(self, obj):
		"""register an object to the appropriate list
		keep a weak reference to the object to avoid circles
		that will cause problems to the garbarge collector
		"""
		self.clean()
		self.__objects[type(obj)].append(weakref.ref(obj))
		window.is_dirty = True
			
	@property
	def objects(self):
		for obj in self.__objects[VPolygon2]:
			yield obj
		for obj in self.__objects[VSegment2]:
			yield obj
		for obj in self.__objects[VPoint2]:
			yield obj
			
catalogue = GlobalCatalogue()

class PygameWindow(object):
	def __init__(self, size=WINSIZE, background_color=(0,0,0)):
		""" Initializes a pygame screen of size size 
		"""
		pygame.init()
		pygame.display.set_caption("pyCompGeom v.0")
		self.background_color = background_color
		self.canvas = pygame.display.set_mode(size, pygame.DOUBLEBUF)
		self.background = pygame.Surface(self.canvas.get_size()).convert()
		self.background.fill(background_color)
		
		self.__is_dirty = False
	
	@property
	def screen(self):
		return self.__screen
	
	@property
	def size(self):
		return self.canvas.get_width(), self.canvas.get_height()
		
	@property
	def height(self):
		return self.canvas.get_height()
		
	@property
	def aspect_ratio(self):
		return float(self.size[0]) / float(self.size[1])
	
	def cartesian(self, pos):
		x, y = pos[0], pos[1]
		return x, self.height - y
		
	def pygpos(self, pos):
		x, y = pos[0], pos[1]
		return x, abs (y - self.height)
	
	def pos2cartesian(self, pos):
		x, y = pos
		x_c, y_c = self.center
		xoffset = abs(x-x_c)
		yoffset = abs(y-y_c)
		width = self.__screen.get_width()
		height = self.__screen.get_height()
		
		X = 2 * xoffset * self.asize / width
		Y = 2* yoffset * self.asize / (height * self.aspect)
		
		if x == x_c:
			onXaxis = True
			Y = 0
		if y == y_c:
			onYaxis = True
			X = 0
		if x > x_c and y < y_c:
			onFirstQuad = True
			return X, Y
		if x < x_c and y < y_c:
			onSecondQuad = True
			return -X, Y
		if x < x_c and y > y_c:
			onThirdQuad = True
			return -X, -Y
		if x > x_c and y > y_c:
			onFourthQuad = True
			return X, -Y
		
	@property
	def is_dirty(self):
		return self.__is_dirty
	@is_dirty.setter
	def is_dirty(self, value):
		self.__is_dirty = value
		if self.__is_dirty:
			self.update()
			self.__is_dirty = False
			
	def clear(self):
		self.background.fill(self.background_color)
		#pygame.display.update()
		pygame.display.flip()
		self.canvas.blit(self.background,(0,0))
		
	def update(self):
		self.clear()
		catalogue.clean()
		for obj in catalogue.objects:
			#if obj().is_dirty:
				obj().blit(self.canvas)
				#obj().is_dirty = False
		pygame.display.flip()

window = PygameWindow()

### ALGORITHMS #########################################################

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
	return Polygon2(hull)

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

def andrew(points):
	upper = []
	lower = []
	for point in sorted(points):
		while len(upper) > 1 and cwon(upper[-2], upper[-1], point):
			upper.pop()
		while len(lower) > 1 and ccwon(lower[-2], lower[-1], point):
			lower.pop()
		upper.append(point)
		lower.append(point)
	hull = lower[:-1]+ [x for x in reversed(upper[1:])]
	return Polygon2(hull)
		
