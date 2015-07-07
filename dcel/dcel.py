#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom.visuals import *
from dcel_gather_input import DcelInputData, similar_edges, segment_double_key_repr, get_segments_of_convex_hull
import pickle

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
        # if self.next is not None:
        #     raise ValueError("HalfEdge - set_next: Next wasn't none - Possible attempt for erroneous overwrite")
        if type(he) is not HalfEdge:
            raise TypeError("HalfEdge - set_next: Expected type \"HalfEdge\", got \"" + str(type(he)) + "\"")
        self.next = he
        he.previous = self

    def set_previous(self, he):
        """Sets the previous HE of the current one.
        Also, sets the next of the given one"""
        # if self.previous is not None:
        #     raise ValueError("HalfEdge - set_previous: Previous wasn't none - Possible attempt for erroneous overwrite")
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
        return "Vertex[(%s, %s) - #Incident-Edges: %s]" % (self.x, self.y, len(self.incident_edges))


class Face:
    def __init__(self, outer_component):
        """

        :param outer_component: HalfEdge The outer component of the face - an arbitrary HalfEdge
        """
        if type(outer_component) is not HalfEdge:
            raise TypeError("Face - __init__: Expected type \"HalfEdge\", got \"" + str(type(outer_component)) + "\"")
        self.outer_component = outer_component
        self.inner_components = None

    def set_inner_component(self, he):
        """

        :param he: HalfEdge The inner half-edge of the face
        """
        if type(he) is not HalfEdge:
            raise TypeError("Face - set_inner_component: Expected type \"HalfEdge\", got \"" + type(he) + "\"")
        if self.inner_components is None:
            self.inner_components = []
        self.inner_components.append(he)

    def __repr__(self):
        return "Face [OuterComponent: %s, InnerComponent: %s]" % (self.outer_component, self.inner_components)

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

    def walk_inner_components(self):
        """Returns a list of lists of HalfEdges for each inner component"""
        if self.inner_components is None:
            return None
        else:
            result = []
            for ic in self.inner_components:
                start_vertice = ic.origin
                idx_edge = ic
                half_edges = [idx_edge]
                while True:
                    idx_edge = idx_edge.next
                    half_edges.append(idx_edge)
                    if idx_edge.next.origin == start_vertice:
                        break
                result.append(half_edges)
            return result


# #########################################
# Key representation of objects methods for dictionaries
# #########################################
def point_key_repr(*args):
    if len(args) == 2 and type(args) is tuple:
        return str(args[0]) + "," + str(args[1])
    elif len(args) == 1 and isinstance(args[0], Point2):
        return str(args[0].x) + "," + str(args[0].y)
    else:
        raise TypeError("point_key_repr: Expected type \"tuple\" or \"Point2\", got: " + str(type(args)))


def segment_key_repr(segment):
    if not isinstance(segment, Segment2):
    # if type(segment) is not Segment2:
        raise TypeError("segment_key_repr: Expected type \"Segment2\" or \"HalfEdge\", got: " + str(type(segment)))
    # if isinstance(segment, HalfEdge):
    #     return str(segment.origin.x) + "," + str(segment.origin.y) + "-" + \
    #            str(segment.twin.origin.x) + "," + str(segment.twin.origin.y)
    return str(segment.start.x) + "," + str(segment.start.y) + "-" + str(segment.end.x) + "," + str(segment.end.y)
# #########################################


class DCEL:
    def __init__(self, points, segments, is_connected_graph, min_max_coords_tuple, bb_dist, bb_segments_number,
                 v_points, v_segments, ch_segments_list, segments_dict):
        # Data members from input
        self.points = points
        # Convert to points to dictionary from "x-coord,y-coord" -> Point2
        self.points_dict = dict((k, v) for k, v in [(point_key_repr(p), p) for p in points])
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
        # This dictionary contains all the outer segments of the connected graph
        # (when the polygon is convex or non-convex)
        self.outer_segments_dict = {}
        self.segments_dict = segments_dict  # Used for getting a next segment as a starting point for a new face
        self.populate_outer_segments_dict(ch_segments_list, segments_dict)
        # The following dictionaries help for finding the next and previous HalfEdges that are on the ConvexHull
        self.outer_he_by_origin_dict = {}  # Origin (x,y) -> Polygon outer HalfEdge with that origin
        self.outer_he_by_dest_dict = {}  # Dest (x,y) -> Polygon outer HalfEdge with that destination
        # The following dictionaries help for finding if a vertex is already created
        self.vertices_dict = {}  # (x,y) -> Vertex
        self.half_edges_dict = {}  # Origin -> HalfEdge
        # Data members of DCEL
        self.vertices = []
        self.half_edges = []
        self.faces = []
        self.construct_dcel()

    def __del__(self):
        del self.points
        del self.points_dict
        del self.segments
        del self.v_points
        del self.v_segments
        del self.vertices
        del self.half_edges
        del self.faces

# #########################################
# Algorithm methods
# #########################################
    def construct_dcel(self):
        if self.is_connected_graph:
            # Case of connected graph (not Voronoi)
            self.connected_graph_handle_bb_components()
            # Algorithm main loop
            # Main idea:    Creating faces by cycling around them (once you complete a circle, you have a new face)
            # Notes:        1. The starting point for each cycle is half-edge
            #               2. The cycle is done in a CCW manner
            starting_he_list = []
            starting_he = None
            while True:
                # The 1st half edge needs to be found manually as it isn't connected to the BB somehow
                if len(self.faces) == 1:
                    starting_he = self.connected_graph_get_starting_edge()
                new_he_list = self.new_face_handling(starting_he)
                if len(new_he_list) > 0:
                    starting_he_list += new_he_list
                    # Before adding, check if any of the new half-edges are already created
                    # for he in new_he_list:
                    #     s_repr = segment_key_repr(he)
                    #     if s_repr not in self.half_edges_dict:
                    #         starting_he_list.append(he)
                # Select next starting_he
                if len(starting_he_list) > 0:
                    starting_he = starting_he_list[0]
                    starting_he_list.remove(starting_he)
                else:
                    print "NO HALF_EDGES TO GO ON - Stopping algorithm"

                # Algorithm termination, #(half-edges) = 2 * #segments - 4 (4 segments of the BB have only 1 half-edge)
                if len(self.half_edges) == 2 * len(self.segments) - 4:
                    break
        else:
            # Disconnected graph case (Voronoi representation)
            pass
        # TODO
        # Delete construction helper data members
        self.test_half_edges_relationships()
        self.test_vertices_incident_edges()
        self.test_visual_he_relationships()
        print "DCEL construction completed"

    # ##################################################
    # Testing methods
    # ##################################################
    def test_half_edges_relationships(self):
        # Each half edge must have a next and a previous
        # All HEs except the 4 of the BB, must have a twin
        for i, e in enumerate(self.half_edges):
            if e.next is None:
                print e, " -> next is None"
                DCEL.draw_half_edge(e)
            if e.previous is None:
                print e, " -> previous is None"
                DCEL.draw_half_edge(e)
            if i > 4 and e.twin is None:
                print e, " -> twin is None"
                DCEL.draw_half_edge(e)

    @staticmethod
    def draw_half_edge(e):
        points = [VPoint2(e.origin, RED)]
        tmp = [VSegment2(e, RED)]
        if e.next is not None:
            tmp.append(VSegment2(e.next, MAGENTA))
            points.append(VPoint2(e.next.origin, MAGENTA))
        if e.previous is not None:
            tmp.append(VSegment2(e.previous, YELLOW))
            points.append(VPoint2(e.previous.origin, YELLOW))
        pause()

    def test_vertices_incident_edges(self):
        for v in self.vertices:
            test = VPoint2(v, MAGENTA)
            print v

    def test_visual_he_relationships(self):
        """Iterate through all the faces, iterating through their HEs, and drawing each one with its prev/next"""
        for i, f in enumerate(self.faces):
            if i == 0:
                print "Walking 1st face (BB)"
            face_he = f.walk_face()
            for he in face_he:
                DCEL.draw_half_edge(he)
            face_inner_he = f.walk_inner_components()
            if face_inner_he is not None:
                if i == 0:
                    print "Walking inner components of 1st face"
                for ic_pack in face_inner_he:
                    for he in ic_pack:
                        DCEL.draw_half_edge(he)
    # ##################################################

    def new_face_handling(self, starting_he):
        """
        Cycles around the segments of the face in a CCW manner

        :param starting_he: HalfEdge The starting HE must have its twin HE initialized and also their vertices!
        :return: List of candidates for new starting half-edges
        """
        starting_edges_candidates = []
        if self.is_connected_graph:
            # Keeping the starting point saved for termination, cycle through the edges of the face
            # Firstly, create a face
            self.faces.append(Face(starting_he))
            idx_vertex = starting_he.twin.origin
            idx_he = starting_he
            tmp_s = VSegment2(starting_he, RED)
            # print starting_he
            while idx_vertex != starting_he.origin:
                print "Walking on the face"
                # Find most CCW segment
                next_segment = self.min_angle_ccw_segment(idx_he, idx_vertex)
                if next_segment is None:
                    next_segment = self.max_angle_cw_segment(idx_he, idx_vertex)
                else:  # Testing
                    tmp_s = VSegment2(next_segment, GREEN)
                # Set up new step
                new_starting_segment, idx_he = self.new_half_edge_handling(next_segment, idx_vertex, idx_he)
                if new_starting_segment is not None:
                    starting_edges_candidates.append(new_starting_segment)
                # update idx_vertex from new half-edge (latest inner half-edge is ALWAYS latest in the list of HEs)
                idx_vertex = idx_he.twin.origin
                # DCEL.draw_half_edge(idx_he)
            # Set up relationship between latest and first half-edges
            starting_he.set_previous(idx_he)
            # DCEL.draw_half_edge(idx_he)
            # DCEL.draw_half_edge(starting_he)
        else:
            pass
        return starting_edges_candidates

    def new_half_edge_handling(self, new_segment, origin, prev_he):
        """
        Receives a segment and an Point2 origin that helps with the orientation of the inner half-edge

        :param new_segment: Segment2 The segment to be used for the two new twin HalfEdges
        :param origin: Point2 The point to be used as an origin for the inner half-edge (helps with the orientation)
        :param prev_he: HalfEdge The previous half-edge of the current cycle
        :return:    The 2-tuple <outer half-edge, inner half-edge)
                    1. Outer HE: can be used as a starting edge. Could be None if the HalfEdge belongs to
                    the Convex Hull of the connected graph
                    2. Inner half-edge is never None
        """
        # Create DCEL vertices and half-edges only if they don't already exist
        origin_v, did_create_origin = self.create_or_get_vertex(origin)
        twin_origin_v, did_create_twin_origin = self.create_or_get_vertex(new_segment.start if new_segment.start != origin else new_segment.end)
        inner_he, outer_he, did_create_he = self.create_or_get_half_edges(new_segment, origin_v, twin_origin_v)
        inner_he.set_previous(prev_he)

        next_starting_he = None
        # In case, new HEs have been created, we need to check the outer HE
        if did_create_he:
            # If outer HE doesn't belong to the CH, then it's a candidate for a next starting half-edge
            if not self.is_outer_segment(self.outer_segments_dict, outer_he):
                next_starting_he = outer_he
            else:
                # Outer HE is one of the outer polygon segments, update its next/previous, if available
                next_of_outer = self.outer_he_by_origin_dict.get(point_key_repr(outer_he.twin.origin))
                ##########
                # Testing
                if next_of_outer is not None:
                    t1 = VSegment2(next_of_outer, YELLOW)
                ##########
                if next_of_outer is not None:
                    outer_he.set_next(next_of_outer)
                prev_of_outer = self.outer_he_by_dest_dict.get(point_key_repr(outer_he.origin))
                ##########
                # Testing
                if prev_of_outer is not None:
                    t2 = VSegment2(prev_of_outer, MAGENTA)
                ##########
                if prev_of_outer is not None:
                    outer_he.set_previous(prev_of_outer)
                self.add_to_outer_half_edges_dicts(outer_he)
        if did_create_origin:
            self.vertices.append(origin)
        if did_create_twin_origin:
            self.vertices.append(twin_origin_v)
        if did_create_he:
            # Adding the inner half-edge to the end is IMPORTANT! As it's used for:
            # 1. Setting the previous of the next HE, above in this method
            # 2. Updating the current vertex in the current face cycle, for stopping the cycle
            self.half_edges += [outer_he, inner_he]

        return next_starting_he, inner_he

# #########################################
# Connected graph (similar to a triangulation subdivision) methods
# #########################################
    def populate_outer_segments_dict(self, ch_segments_list, segments_dict):
        """
        Populates a dictionary of the outer segments of the connected graph

        Note1:  Dictionary contains as values the outer segments and uses as keys the segment_double_key_representation
                method
        :param ch_segments_list: The list of the convex hull segments
        :param segments_dict: The dictionary of the segments of the input
        """
        for ch_s in ch_segments_list:
            s_repr = segment_double_key_repr(ch_s)
            ch_segment = VSegment2(ch_s, MAGENTA)
            # CH segment is one of input => Is outer segment
            if s_repr[0] in segments_dict or s_repr[1] in segments_dict:
                tmp_s = segments_dict.get(s_repr[0]) if s_repr[0] in segments_dict else segments_dict.get(s_repr[1])
                DCEL.add_segment_to_outer_segments_dict(self.outer_segments_dict, tmp_s, s_repr)
            else:
                # CH segment isn't part of input => Replace it with its connected components
                idx_point = ch_s.start if ch_s.start.y > ch_s.end.y else ch_s.end
                start_point = ch_s.start if idx_point != ch_s.start else ch_s.end
                next_segment = self.min_angle_ccw_segment(ch_s, idx_point)
                if next_segment is None:
                    tmp = idx_point
                    idx_point = start_point
                    start_point = tmp
                idx_segment = ch_s
                while idx_point != start_point:
                    visual_segment = None
                    next_segment = self.min_angle_ccw_segment(idx_segment, idx_point)
                    if next_segment is None:
                        next_segment = self.max_angle_cw_segment(idx_segment, idx_point)
                        visual_segment = VSegment2(next_segment, YELLOW)
                    else:  # Testing
                        visual_segment = VSegment2(next_segment, YELLOW)
                    self.add_segment_to_outer_segments_dict(self.outer_segments_dict, next_segment)
                    idx_point = next_segment.start if next_segment.start != idx_point else next_segment.end
                    idx_segment = next_segment

    def connected_graph_handle_bb_components(self):
        """Handle BB edges and vertices, by starting from lower left vertice and cycling in a CCW way"""
        # Create 4 vertices, 4 half-edges, and a face (the outer one)
        v_lower_left = \
            Vertex(self.points_dict.get(point_key_repr(self.min_x - self.bb_dist, self.min_y - self.bb_dist)))
        v_lower_right = \
            Vertex(self.points_dict.get(point_key_repr(self.max_x + self.bb_dist, self.min_y - self.bb_dist)))
        v_upper_right = \
            Vertex(self.points_dict.get(point_key_repr(self.max_x + self.bb_dist, self.max_y + self.bb_dist)))
        v_upper_left = \
            Vertex(self.points_dict.get(point_key_repr(self.min_x - self.bb_dist, self.max_y + self.bb_dist)))
        # The inner half-edges of the bounding box, don't have a twin
        # Create half-edges with their origins, then set their next (and thus, their previous) half-edges
        lower_he = HalfEdge(v_lower_left, self.segments[-4])
        right_he = HalfEdge(v_lower_right, self.segments[-3])
        upper_he = HalfEdge(v_upper_right, self.segments[-2])
        left_he = HalfEdge(v_upper_left, self.segments[-1])
        lower_he.set_next(right_he)
        right_he.set_next(upper_he)
        upper_he.set_next(left_he)
        left_he.set_next(lower_he)
        # Set incident edges for the vertices
        v_lower_left.add_incident_edge(left_he)
        v_lower_right.add_incident_edge(lower_he)
        v_upper_right.add_incident_edge(right_he)
        v_upper_left.add_incident_edge(upper_he)
        face = Face(lower_he)
        # Add already created DCEL components
        self.vertices += [v_lower_left, v_lower_right, v_upper_right, v_upper_left]
        self.half_edges += [lower_he, right_he, upper_he, left_he]
        self.faces.append(face)

    def connected_graph_get_starting_edge(self):
        """
        Finds the starting edge in the case of the connected graph

        :return: HalfEdge The starting half-edge
        """
        # Find starting point (minimum x point)
        min_x_point = None
        for p in self.points:
            if p.x == self.min_x:
                min_x_point = p
                break
        # Find starting edge for the algorithm, and the segments that have min_x_point as a vertex
        # If they are # > 2, filter them by keeping the two that define the max area
        #   N.B.:   We filter the two vectors that define the max area, as they are the ones, that are outer
        #           in the planar graph
        connected_segments = self.find_segments_with_point(min_x_point)
        # print connected_segments
        max_angle_segments = DCEL.find_segments_with_max_angle(connected_segments)
        # print max_angle_segments
        # Arbitrarily selecting one segment (the one with the min_y coordinate from the two points -
        # thus excluding their common point)
        common_point, segment_with_min_y = None, None
        s1, s2 = max_angle_segments
        if s1.start == s2.start:
            common_point = s1.start
            segment_with_min_y = s1 if s1.end.y < s2.end.y else s2
        elif s1.start == s2.end:
            common_point = s1.start
            segment_with_min_y = s1 if s1.end.y < s2.start.y else s2
        elif s1.end == s2.start:
            common_point = s1.end
            segment_with_min_y = s1 if s1.start.y < s2.end.y else s2
        elif s1.end == s2.end:
            common_point = s1.end
            segment_with_min_y = s1 if s1.start.y < s2.start.y else s2
        else:
            raise ValueError("DCEL Construction - Connected-graph case: Starting edges don't have a "
                             "common point")

        # TESTING
        # print common_point
        # print segment_with_min_y
        tmp_p = VPoint2(common_point, RED)
        tmp_s = VSegment2(segment_with_min_y, GREEN)

        # Create the 1st two vertices, the 1st Half-Edge and the 1st face of the connected-graph component
        min_x_vert, _ = self.create_or_get_vertex(min_x_point)
        other_point = segment_with_min_y.start if min_x_point != segment_with_min_y.start else segment_with_min_y.end
        other_vert, _ = self.create_or_get_vertex(other_point)
        # Create the two new half-edges with origin the two points
        # Setting next and previous doesn't apply in this case (first half-edge of the connected graph)
        inner_he, outer_he, _ = self.create_or_get_half_edges(segment_with_min_y, min_x_vert, other_vert)
        (self.faces[0]).set_inner_component(outer_he)
        # Updating the DCEL object catalogues
        self.vertices += [min_x_vert, other_vert]
        self.half_edges += [outer_he, inner_he]
        # Update the outer half-edges dictionaries
        self.add_to_outer_half_edges_dicts(outer_he)
        return inner_he

# #########################################
# DCEL class helper methods
# #########################################
    def add_to_outer_half_edges_dicts(self, he):
        """
        Adds the given half-edge to the two dictionaries of the outer half-edges

        The dictionaries are as follows:
            1. key: origin of HE - value: HE with that origin -- used for setting next outer HE
            2. key: destination of HE - value: HE with that destination -- used for setting previous outer HE
        :param he: The half edge to be added to the dicts
        """
        self.outer_he_by_origin_dict[point_key_repr(he.origin)] = he
        self.outer_he_by_dest_dict[point_key_repr(he.twin.origin)] = he

    def create_or_get_vertex(self, point):
        """
        Creates a new vertex if it doesn't exist, or returns the one that is represented by the given point

        :param point: Point2 The given point to act as a key or a base class for the Vertex
        :return: A 2-tuple <Vertex that's on the given point, True if it did create it (False otherwise)>
        """
        p_repr = point_key_repr(point)
        if p_repr not in self.vertices_dict:
            origin_v = Vertex(point)
            self.vertices_dict[p_repr] = origin_v
            return origin_v, True
        else:
            origin_v = self.vertices_dict.get(p_repr)
            return origin_v, False

    def create_or_get_half_edges(self, segment, origin_v, twin_origin_v):
        """
        Creates two new half-edges if they don't exist, or returns a tuple with the two that represented the segment

        :param segment: Segment2 The segment to be used as a key or base class for the two new half-edges
        :param origin_v: Vertex The point to be used as origin for the 1st half-edge
        :param twin_origin_v: Vertex The point to be used as origin for the 2nd half-edge
        :return: A 3-tuple of the two half-edges for the given segment (1st is the one with origin_v at its origin) and
                    a flag that is True if the HE have been created
        """
        s_repr = segment_key_repr(segment)
        if s_repr not in self.half_edges_dict:
            inner_he = HalfEdge(origin_v, segment)
            outer_he = HalfEdge(twin_origin_v, segment)

            inner_he.set_twin(outer_he)
            origin_v.add_incident_edge(outer_he)
            twin_origin_v.add_incident_edge(inner_he)

            self.half_edges_dict[s_repr] = inner_he
            return inner_he, outer_he, True
        else:
            he = self.half_edges_dict.get(s_repr)
            return (he, he.twin, False) if he.origin == origin_v else (he.twin, he, False)

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

    def min_angle_ccw_segment(self, segment, connection_point):
        """
        Returns a segment that defines the minimum angle with the given segment in a CCW manner

        :param segment: Segment2 The segment that will act as a base for the other segments to be found
        :param connection_point: Point2 The point of the segment that will be used for searching connected segments
        :return:    The segment that:
                        (i) is connected in CCW manner with the given one and
                        (ii) defines the minimum angle with the given segment
        """
        edges = self.find_connected_segments_with_segment(segment, connection_point)
        tmp_seg = VSegment2(segment, BLUE)
        min_angle = 2 * math.pi
        result = None
        for e in edges:
            tmp_s = VSegment2(e, RED)
            angle = vectors_angle(segment, e)
            e_point = e.end if e.end != connection_point else e.start
            s_point = segment.start if connection_point != segment.start else segment.end
            if ccw(s_point, connection_point, e_point) and angle < min_angle:
                min_angle = angle
                result = e
        return result

    def max_angle_cw_segment(self, segment, connection_point):
        """
        Returns a segment that defines the maximum angle with the given segment in a CW manner

        :param segment: Segment2 The segment that will act as a base for the other segments to be found
        :param connection_point: Point2 The point of the segment that will be used for searching connected segments
        :return:    The segment that:
                        (i) is connected in CW manner with the given one and
                        (ii) defines the maximum angle with the given segment
        """
        edges = self.find_connected_segments_with_segment(segment, connection_point)
        tmp_seg = VSegment2(segment, BLUE)
        max_angle = 0
        result = None
        for e in edges:
            tmp_s = VSegment2(e, RED)
            angle = vectors_angle(segment, e)
            e_point = e.end if e.end != connection_point else e.start
            s_point = segment.start if connection_point != segment.start else segment.end
            if cw(s_point, connection_point, e_point) and angle > max_angle:
                max_angle = angle
                result = e
        return result

    @staticmethod
    def add_segment_to_outer_segments_dict(outer_segments_dict, segment, s_repr=None):
        """
        Ads a segment to the dictionary of outer segments of the polygon

        :param p1: Point2 A point of the segment
        :param p2: Point2 The other point of the segment
        :param outer_segments_dict: Dictionary The dict that maps segment representation to Segment2 (Outer segments)
        """
        if s_repr is None:
            s_repr = segment_double_key_repr(segment)
        outer_segments_dict.update({s_repr[0]: segment, s_repr[1]: segment})

    @staticmethod
    def is_outer_segment(outer_segments_dict, segment):
        """
        Tests for membership of the segment in the outer segments of the polygon
        :param outer_segments_dict: The dictionary holding the outer segments of the polygon
        :param segment: The segment to be tested for membership
        :return: True, on membership, False otherwise
        """
        s_repr = segment_double_key_repr(segment)
        if s_repr[0] in outer_segments_dict or s_repr[1] in outer_segments_dict:
            return True
        else:
            return False


# #########################################
# General helper methods
# #########################################
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
    # print v1_v2_angle
    return v1_v2_angle


if __name__ == '__main__':
    if len(sys.argv) == 1:
        dcel_data = DcelInputData(20)
        dcel_data.get_visual_dcel_members()
        dcel_data.pickle_dcel_data()
    else:
        dcel_data = DcelInputData.unpickle_dcel_data(sys.argv[1])
    print "Done with DCELInputGather"
    min_max_coords_tuple = (dcel_data.min_x, dcel_data.min_y, dcel_data.max_x, dcel_data.max_y)
    dcel = DCEL(dcel_data.vertices, dcel_data.edges, dcel_data.is_connected_graph, min_max_coords_tuple,
                dcel_data.bb_dist,  dcel_data.bb_edges_number, dcel_data.v_vertices, dcel_data.v_edges,
                dcel_data.ch_segments_list, dcel_data.segments_dict)
    print dcel.faces
    print dcel.vertices
    print dcel.half_edges
    pause()
    del dcel_data
