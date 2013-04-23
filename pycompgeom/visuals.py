WINSIZE = (640, 480)
DEFAULTPOINTSIZE = 2

import pygame
import weakref
from colors import *
from events import *
from primitives import *

class VPoint2(Point2):
	def __init__(self, point2=None, color=WHITE, size=DEFAULTPOINTSIZE, update_window=True):
		"""Initializes a visual representaion of a Point2 object
		"""
		self.update_window = update_window # in case of multiple random points??!!
		if point2:
			self.x, self.y = point2.x, point2.y
		else:
			self.get()
		self.color = color
		self.size = size
		catalogue.register(self)
		
	def __del__(self):
		window.point_background_is_dirty = True
		
	def get(self):
		pygame_position = get_mouse_click()
		self.x, self.y = window.cartesian(pygame_position)
		self.update_window = True
		
	def pygame_position(self):
		return window.pygame_position(self.coordinates)
		
	def draw(self, background):
		try:
			pygame.draw.circle(background, self.color, self.pygame_position(), self.size)
		except TypeError: 
			# got float coordinates
			x, y = self.pygame_position()
			intcoords = int(x+.5), int(y+.5)
			pygame.draw.circle(background, self.color, intcoords, self.size)

class VSegment2(Segment2):
	def __init__(self, segment2=None, color=WHITE, update_window=True):
		self.update_window = update_window # same as VPoint2
		if segment2:
			self.start, self.end = segment2.start, segment2.end
		else:
			self.get()
		self.color = color
		catalogue.register(self)
		
	def get(self):
		start_pygame_position = get_mouse_click()
		end_pygame_position = get_mouse_click()
		self.start = Point2.from_tuple(window.cartesian(start_pygame_position))
		self.end = Point2.from_tuple(window.cartesian(end_pygame_position))
		self.update_window = True
		
	def __del__(self):
		window.segment_background_is_dirty = True
		
	@classmethod
	def from_endpoints(cls, start, end, color=WHITE):
		return cls(Segment2(start, end), color=color)
		
	@classmethod
	def from_tuple(cls, atuple, color=WHITE):
		return cls(Segment2(atuple[0], atuple[1]), color=color)

	@property
	def segment_start(self):
		return window.pygame_position(self.start.coordinates)
		
	@property
	def segment_end(self):
		return window.pygame_position(self.end.coordinates)
		
	def draw(self, background):
		pygame.draw.aaline(background, self.color, self.segment_start, self.segment_end, 2)
	
class VPolygon2(Polygon2):
	def __init__(self, polygon2=None, color=WHITE):
		if polygon2:
			self.vertices = polygon2.vertices
			self.__vertices = [window.pygame_position(point.coordinates) for point in polygon2.vertices]
			self.update_window = True
		self.color = color
		catalogue.register(self)
		
	def __del__(self):
		window.polygon_background_is_dirty = True
		
	def draw(self, background):
		pygame.draw.aalines(background, self.color, True, self.__vertices, 1)
		

class GlobalCatalogue(object):
	def __init__(self):
		"""Initializes the global catalogue of visual objects
		   Notice that self.__objects is indexed by class names!
		"""
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
		
	def register(self, obj):
		"""register an object to the appropriate list
		keep a weak reference to the object to avoid circles
		that will cause problems to the garbarge collector
		"""
		self.clean()
		self.__objects[type(obj)].append(weakref.ref(obj))
		if obj.update_window:
			if type(obj) == VPoint2:
				window.point_background_is_dirty = True
			if type(obj) == VSegment2:
				window.segment_background_is_dirty = True
			if type(obj) == VPolygon2:
				window.polygon_background_is_dirty = True
			
			
	@property
	def points(self):
		for obj in self.__objects[VPoint2]:
			yield obj
	
	@property
	def segments(self):
		for obj in self.__objects[VSegment2]:
			yield obj
	
	@property
	def polygons(self):
		for obj in self.__objects[VPolygon2]:
			yield obj
			
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
	def __init__(self, size=WINSIZE, background_color=BLACK):
		""" Initializes a pygame screen of size size 
		"""
		pygame.init()
		pygame.display.set_caption("pyCompGeom v.0")
		self.background_color = background_color
		self.canvas = pygame.display.set_mode(size)
		self.background = pygame.Surface(self.canvas.get_size()).convert()
		self.point_background = pygame.Surface(self.canvas.get_size())
		self.segment_background = pygame.Surface(self.canvas.get_size())
		self.polygon_background = pygame.Surface(self.canvas.get_size())
		self.point_background.set_colorkey(BLACK)
		self.segment_background.set_colorkey(BLACK)
		self.polygon_background.set_colorkey(BLACK)
		self.point_background.convert_alpha()
		self.segment_background.convert_alpha()
		self.polygon_background.convert_alpha()
		self.__is_dirty = False
		
	@property
	def size(self):
		return self.canvas.get_width(), self.canvas.get_height()
		
	@property
	def height(self):
		return self.canvas.get_height()
		
	@property
	def width(self):
		return self.canvas.get_height()
		
	@property
	def aspect_ratio(self):
		return float(self.width) / float(self.height)
		
	def cartesian(self, pygame_position):
		x, y = pygame_position[0], pygame_position[1]
		return x, abs(self.height - y)
		
	def pygame_position(self, cartesian_coordinates):
		x, y = cartesian_coordinates[0], cartesian_coordinates[1]
		return x, abs(y - self.height)
		
	@property
	def is_dirty(self):
		return self.__is_dirty
	@is_dirty.setter
	def is_dirty(self, value):
		self.__is_dirty = value
		if self.__is_dirty:
			self.update()
			self.__is_dirty = False
			
	@property
	def point_background_is_dirty(self):
		return self.__point_background_is_dirty
	@point_background_is_dirty.setter
	def point_background_is_dirty(self, is_dirty):
		if is_dirty:
			catalogue.clean()
			self.point_background.blit(self.background, (0,0))
			for point in catalogue.points:
				point().draw(self.point_background)
			self.blit_layers()
		else:
			self.__point_background_is_dirty = False
			
	@property
	def segment_background_is_dirty(self):
		return self.__segment_background_is_dirty
	@segment_background_is_dirty.setter
	def segment_background_is_dirty(self, is_dirty):
		if is_dirty:
			catalogue.clean()
			self.segment_background.blit(self.background, (0,0))
			for segment in catalogue.segments:
				segment().draw(self.segment_background)
			self.blit_layers()
		else:
			self.__segment_background_is_dirty = False
	
	@property
	def polygon_background_is_dirty(self):
		return self.__polygon_background_is_dirty
	@polygon_background_is_dirty.setter
	def polygon_background_is_dirty(self, is_dirty):
		if is_dirty:
			catalogue.clean()
			self.polygon_background.blit(self.background, (0,0))
			for polygon in catalogue.polygons:
				polygon().draw(self.polygon_background)
			self.blit_layers()
		else:
			self.__polygon_background_is_dirty = False
			
	def clear(self):
		self.background.fill(self.background_color)
		pygame.display.flip()
		self.point_background.blit(self.background, (0,0))
		self.segment_background.blit(self.background, (0,0))
		self.polygon_background.blit(self.background, (0,0))
		self.canvas.blit(self.background, (0,0))
		
	def update(self):
		self.clear()
		catalogue.clean()
		for polygon in catalogue.polygons:
			polygon().draw(self.polygon_background)
		for segment in catalogue.segments:
			segment().draw(self.segment_background)
		for point in catalogue.points:
			point().draw(self.point_background)
		
	def blit_layers(self):
		self.canvas.blit(self.background, (0,0))
		self.canvas.blit(self.polygon_background, (0,0))
		self.canvas.blit(self.segment_background, (0,0))
		self.canvas.blit(self.point_background, (0,0))
		pygame.display.flip()

window = PygameWindow()
