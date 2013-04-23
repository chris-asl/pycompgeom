import pygame
from events import  *
from visuals import *

def getVPoints(withlabels=False, buttonin=LEFTBUTTON, buttonout=RIGHTBUTTON):
	pygame.display.set_caption("left click enters point, right click ends")
	points = []
	while True:
		event = pygame.event.poll()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == buttonin:
				pos = window.cartesian(event.pos)
				if withlabels:
					points.append(VPoint2(Point2.from_tuple(pos), \
						label=`len(points)+1`))
				else:
					points.append(VPoint2(Point2.from_tuple(pos)))
			elif event.button == buttonout:
				pygame.display.set_caption('pyCompGeom window')
				return points
			elif not shouldIQuit(event):
				event = None
				
def getVPolygon(convex=False, buttonin=LEFTBUTTON, buttonout=RIGHTBUTTON):
	pygame.display.set_caption("left click enters next ccw polygon vertex, right click ends")
	vertices, vvertices = [], []
	while True:
		event = pygame.event.poll()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == buttonin:
				pos = window.cartesian(event.pos)
				if convex == True:
					p = Polygon2(vertices + [Point2.from_tuple(pos)])
					if p.isConvex():
						vvertices.append(VPoint2(Point2.from_tuple(pos)))
						vertices.append(Point2.from_tuple(pos))
				else:
					vvertices.append(VPoint2(Point2.from_tuple(pos)))
					vertices.append(Point2.from_tuple(pos))
			elif event.button == buttonout:
				pygame.display.set_caption('pyCompGeom window')
				return VPolygon2(Polygon2(vertices))
			elif not shouldIQuit(event):
				event = None
