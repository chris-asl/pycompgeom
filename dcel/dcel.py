#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom.visuals import *
from dcel_gather_input import DcelInputData, similar_edges, is_segment_of_ch


class HalfEdge(Segment2):
    def __init__(self, origin, segment):
        """
        Construction of a HalfEdge. Next, previous and twin data members are set to None and must be set!
        :param origin: Vertex The origin of the HalfEdge
        :param segment: Segment2
        """
        if type(origin) is not Vertex:
            raise TypeError("HalfEdge - __init__: Expected type \"Vertex\" for origin, got \"" + str(type(origin)))
        if type(segment) is not Segment2:
            raise TypeError("HalfEdge - __init__: Expected type \"Segment2\" for superclass, got \"" +
                            str(type(segment)))
        self.origin = origin
        self.next = None
        self.previous = None
        self.twin = None
        other_point = segment.start if segment.start != origin else segment.end
        super(HalfEdge, self).__init__(origin, other_point)

    def __repr__(self):
        return "Half-Edge[Origin: (%s)]" % self.origin

    def set_next(self, he):
        """Sets the next HE of the current one.
        Also, sets the previous of the given one"""
        if self.next is not None:
            raise ValueError("HalfEdge - set_next: Next wasn't none - Possible attempt for erroneous overwrite")
        if type(he) is not HalfEdge:
            raise TypeError("HalfEdge - set_next: Expected type \"HalfEdge\", got \"" + str(type(he)) + "\"")
        self.next = he
        he.previous = self

    def set_previous(self, he):
        """Sets the previous HE of the current one.
        Also, sets the next of the given one"""
        if self.previous is not None:
            raise ValueError("HalfEdge - set_previous: Previous wasn't none - Possible attempt for erroneous overwrite")
        if type(he) is not HalfEdge:
            raise TypeError("HalfEdge - set_previous: Expected type \"HalfEdge\", got \"" + str(type(he)) + "\"")
        self.previous = he
        he.next = self

    def set_twin(self, twin):
        """Sets the twin relationship between two half-edges"""
        if type(twin) is not HalfEdge:
            raise TypeError("HalfEdge - set_next: Expected type \"HalfEdge\", got \"" + str(type(twin)) + "\"")
        self.twin = twin
        twin.twin = self


class Vertex(Point2):
    def __init__(self, point2):
        """

        :param point2: Point2 The point for the construction of the superclass
        """
        if type(point2) is not Point2:
            raise TypeError("Vertex - __init__: Expected type \"Point2\", got \"" + str(type(point2)) + "\"")
        self.incident_edges = []
        super(Vertex, self).__init__(point2.x, point2.y)

    def add_incident_edge(self, he):
        """
        Adds incident edges to the vertex
        :param he: HalfEdge The incident half-edge to be added
        """
        if type(he) is not HalfEdge:
            raise TypeError("Vertex - add_incident_edge: Expected type \"HalfEdge\", got \"" + str(type(he)) + "\"")
        self.incident_edges.append(he)

    def visit_incident_edges(self):
        """Generator for the incident edges of the vertice"""
        for edge in self.incident_edges:
            yield edge

    def __repr__(self):
        return "Vertex(%s, %s)" % (self.x, self.y)


class Face:
    def __init__(self, outer_component):
        """

        :param outer_component: HalfEdge The outer component of the face - an arbitrary HalfEdge
        """
        self.outer_component = outer_component
        self.inner_component = None

    def set_inner_component(self, he):
        """

        :param he: HalfEdge The inner half-edge of the face
        """
        if type(he) is not HalfEdge:
            raise TypeError("Face - set_inner_component: Expected type \"HalfEdge\", got \"" + type(he) + "\"")
        self.inner_component = he

    def __repr__(self):
        return "Face [OuterComponent: %s, InnerComponent: %s]" % (self.outer_component, self.inner_component)

    def walk_face(self):
        """Returns a list of HalfEdges that surround the face"""
        start_vertice = self.outer_component.origin
        idx_edge = self.outer_component
        half_edges = [self.outer_component]
        while True:
            idx_edge = idx_edge.next
            half_edges.append(idx_edge)
            if idx_edge.next.origin == start_vertice:
                break
        return half_edges


def point_key_repr(x, y):
    return str(x) + "," + str(y)


class DCEL:
    def __init__(self, points, segments, is_connected_graph, min_max_coords_tuple, bb_dist, bb_segments_number,
                 v_points, v_segments, ch_segments_dict):
        # Data members from input
        self.points = points
        # Convert to points to dictionary from "x-coord,y-coord" -> Point2
        self.points_dict = dict((k, v) for k, v in [(str(p.x) + "," + str(p.y), p) for p in points])
        self.segments = segments
        self.is_connected_graph = is_connected_graph
        self.min_x = min_max_coords_tuple[0]
        self.min_y = min_max_coords_tuple[1]
        self.max_x = min_max_coords_tuple[2]
        self.max_y = min_max_coords_tuple[3]
        self.bb_dist = bb_dist
        self.bb_segments_number = bb_segments_number
        self.v_points = v_points
        self.v_segments = v_segments
        self.ch_segment_dict = ch_segments_dict
        # The following dictionaries help for finding the next and previous HalfEdges that are on the ConvexHull
        self.ch_he_by_origin_dict = {}
        self.ch_he_by_dest_dict = {}
        # Data members of DCEL
        self.vertices = []
        self.half_edges = []
        self.faces = []
        # Testing
        # self.most_ccw_edge(edges[0])
        # self.most_cw_edge(edges[0])

    def add_to_half_edges_dicts(self, he):
        """
        Adds the given half-edge to the two dictionaries of half-edges belonging to the CH

        The dictionaries are as follows:
            1. key: origin of HE - value: HE with that origin -- used for setting next HE on the CH
            2. key: destination of HE - value: HE with that destination -- used for setting previous HE on the CH
        :param he: The half edge to be added to the dicts
        """
        self.ch_he_by_origin_dict[point_key_repr(he.origin.x, he.origin.y)] = he
        self.ch_he_by_dest_dict[point_key_repr(he.twin.origin.x, he.twin.origin.y)] = he

    @staticmethod
    def find_segments_with_max_angle(segments):
        """
        Calculates the area between two segments, and returns the two which define the max area
        :param segments: A list of Segment2 objects
        :return: A tuple of two (2) Segment2 objects that define the max area from the given segments
        """
        if len(segments) <= 2:
            return tuple(segments)
        max_angle = 0
        result = ()
        for s_i in segments:
            for s_j in segments:
                if s_i == s_j:
                    continue
                angle = vectors_angle(s_i, s_j)
                if angle > max_angle:
                    max_angle = angle
                    result = (s_i, s_j)
        return result

    def find_segments_with_point(self, p):
        """Finds edges that have the given point p as a member (start or end)"""
        result = []
        for s in self.segments:
            if s.start == p or s.end == p:
                result.append(s)
        return result

    def find_connected_segments_with_segment(self, segment, connection_point):
        """Populates a list with the edges that have the Point2 connection_point as a start/end"""
        res = []
        for e in self.segments:
            if not similar_edges(e, segment, 0) and (e.start == connection_point or e.end == connection_point):
                res.append(e)
        return res

    def most_ccw_segment(self, segment, connection_point):
        """
        Returns a segment that defines the minimum angle with the given segment

        :param segment: Segment2 The segment that will act as a base for the other segments to be found
        :param connection_point: Point2 The point of the segment that will be used for searching connected segments
        :return:    The segment that:
                        (i) is connected in CCW manner with the given one and
                        (ii) defines the minimum angle with the given segment
        """
        edges = self.find_connected_segments_with_segment(segment, connection_point)
        min_angle = 2 * math.pi
        result = None
        for e in edges:
            angle = vectors_angle(segment, e)
            if ccw(segment.start, segment.end, e.end) and angle < min_angle:
                min_angle = angle
                result = e
        self.v_segments.append(VSegment2(result, RED))
        return result

    def most_cw_segment(self, segment):
        """Returns a segment that defines the minimum angle with the given segment
        The segments are also connected in a CW manner"""
        edges = self.find_connected_segments_with_segment(segment)
        min_angle = 2 * math.pi
        result = None
        for e in edges:
            angle = vectors_angle(segment, e)
            if cw(segment.start, segment.end, e.end) and angle < min_angle:
                min_angle = angle
                result = e
        self.v_segments.append(VSegment2(result, BLUE))
        return result

    def least_cw_segment(self, segment):
        """Returns a segment that defines the maximum angle with the given segment
        The segments are also connected in a CW manner"""
        edges = self.find_connected_segments_with_segment(segment)
        max_angle = 0
        result = None
        for e in edges:
            angle = vectors_angle(segment, e)
            if cw(segment.start, segment.end, e.end) and angle > max_angle:
                max_angle = angle
                result = e
        self.v_segments.append(VSegment2(result, BLUE))
        return result

    def __del__(self):
        del self.points
        del self.points_dict
        del self.segments
        del self.v_points
        del self.v_segments
        del self.vertices
        del self.half_edges
        del self.faces


def dot_product(v1, v2):
    """Calculates the dot product of 2D vectors v1 and v2"""
    return sum((a * b) for a, b in zip(v1, v2))


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
    vertices_pack, edges_pack, min_max_coords_tuple = dcel_data.get_visual_dcel_members()
    print dcel_data
    print "Done with DCELInputGather"
    dcel = DCEL(vertices_pack[0], edges_pack[0], dcel_data.is_connected_graph, min_max_coords_tuple, dcel_data.bb_dist,
                dcel_data.bb_edges_number, vertices_pack[1], edges_pack[1], dcel_data.ch_segments_dict)
    pause()
    del vertices_pack, edges_pack, dcel_data
