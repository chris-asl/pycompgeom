#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom.primitives import Segment2
from pycompgeom.pycompgeom import Point2


class HalfEdge(Segment2):
    def __init__(self, origin, next_half_edge, previous_half_edge, twin_half_edge):
        self.origin = origin
        self.next_half_edge = next_half_edge
        self.previous_half_edge = previous_half_edge
        self.twin = twin_half_edge
        if self.twin is None:
            raise ValueError("Twin half-edge is None")
        else:
            super(HalfEdge, self).__init__(origin, self.twin.origin)

    def __repr__(self):
        return "Half-Edge[(%s) -> (%s)]" % (self.origin, self.twin.origin)


class Vertex(Point2):
    def __init__(self, point2, incident_edges):
        self.incident_edges = incident_edges
        super(Vertex, self).__init__(point2.x, point2.y)

    def visit_incident_edges(self):
        """Prints incident edges (possibly in a CCW order)"""
        for edge in self.incident_edges:
            yield edge

    def __repr__(self):
        return "Vertex(%s, %s)" % (self.x, self.y)


class DCEL:
    def __init__(self, vertices, edges):
        pass


if __name__ == '__main__':
    p = Point2(1, 3)
    q = Point2(5, 2)
    s = [Segment2(p, q), Segment2(q, p)]
    v = Vertex(p, s)
    print v
