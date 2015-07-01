#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom.primitives import Segment2
from pycompgeom.pycompgeom import Point2
from pycompgeom.visuals import *
from dcel_gather_input import DcelInputData, similar_edges

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
    def __init__(self, vertices, edges, is_connected_graph, min_max_coords_tuple, bb_dist, v_vertices, v_edges):
        self.vertices = vertices
        self.edges = edges
        self.is_connected_graph = is_connected_graph
        self.min_x = min_max_coords_tuple[0]
        self.min_y = min_max_coords_tuple[1]
        self.max_x = min_max_coords_tuple[2]
        self.max_y = min_max_coords_tuple[3]
        self.bb_dist = bb_dist
        self.v_vertices = v_vertices
        self.v_edges = v_edges
        # Testing
        # self.most_ccw_edge(edges[0])
        # self.most_cw_edge(edges[0])

    def find_edges_with_vertice(self, edge):
        res = []
        for e in self.edges:
            if not similar_edges(e, edge, 0) and (e.start == edge.end or e.end == edge.end):
                res.append(e)
        return res

    def most_ccw_edge(self, edge):
        edges = self.find_edges_with_vertice(edge)
        min_angle = 2 * math.pi
        result = None
        for e in edges:
            angle = vectors_angle(edge, e)
            if ccw(edge.start, edge.end, e.end) and angle < min_angle:
                min_angle = angle
                result = e
        self.v_edges.append(VSegment2(result, RED))
        return result

    def most_cw_edge(self, edge):
        edges = self.find_edges_with_vertice(edge)
        min_angle = 2 * math.pi
        result = None
        for e in edges:
            angle = vectors_angle(edge, e)
            if cw(edge.start, edge.end, e.end) and angle < min_angle:
                min_angle = angle
                result = e
        self.v_edges.append(VSegment2(result, BLUE))
        return result

def dot_product(v1, v2):
    """Calculates the dot product of 2D vectors v1 and v2"""
    return sum((a*b) for a, b in zip(v1, v2))

def vectors_angle(v1, v2):
    """Calculates the angle of 2D vectors v1 and v2, after translating them to origin"""
    if v1.start == v2.start:
        vector1 = (v1.end.x - v1.start.x, v1.end.y - v1.start.y)
        vector2 = (v2.end.x - v2.start.x, v2.end.y - v2.start.y)
    elif v1.start == v2.end:
        vector1 = (v1.end.x - v1.start.x, v1.end.y - v1.start.y)
        vector2 = (v2.start.x - v2.end.x, v2.start.y - v2.end.y)
    elif v1.end == v2.start:
        vector1 = (v1.start.x - v1.end.x, v1.start.y - v1.end.y)
        vector2 = (v2.end.x - v2.start.x, v2.end.y - v2.start.y)
    elif v1.end == v2.end:
        vector1 = (v1.start.x - v1.end.x, v1.start.y - v1.end.y)
        vector2 = (v2.start.x - v2.end.x, v2.start.y - v2.end.y)
    else:
        raise ValueError("angle: vectors don't have a common point")
    v1_v2_angle = math.acos(dot_product(vector1, vector2) / ((dot_product(vector1, vector1) ** 0.5) *
                                                             (dot_product(vector2, vector2) ** 0.5)))
    print v1_v2_angle
    return v1_v2_angle


if __name__ == '__main__':
    dcel_data = DcelInputData()
    vertices_pack, edges_pack, min_max_coords_tuple, bb_dist = dcel_data.get_visual_dcel_members()
    print dcel_data
    print "Done with DCELInputGather"
    dcel = DCEL(vertices_pack[0], edges_pack[0], dcel_data.is_connected_graph, min_max_coords_tuple, bb_dist,
                vertices_pack[1], edges_pack[1])
    pause()
    del vertices_pack, edges_pack, dcel_data
