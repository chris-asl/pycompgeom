# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom import *
from math import sqrt
import pickle
from time import time
from datetime import datetime

def similar_vertices(v1, v2, epsilon=5.0):
    """
    Checks if two vertices are the same

    The vertices are defined as similar iff: d(v1, v2) < epsilon (max_distance)
    :param v1: (Point2)
    :param v2: (Point2)
    :param epsilon: The maximum distance that tells if two vertices are the same
    :return: True if vertices are the same, False otherwise
    """
    return sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2) <= epsilon


def similar_edges(e1, e2, epsilon):
    """
    Checks if the two given edges are the same

    The edges are define as similar iff:
    d(e1.start, e2.start) < epsilon and d(e1.end, e2.end) < epsilon
    OR
    d(e1.end, e2.start) < epsilon and d(e1.start, e2.end) < epsilon
    :param e1: (Segment2)
    :param e2: (Segment2)
    :param epsilon: The maximum distance (error)
    :return: True if edges are similar, False otherwise
    """
    if similar_vertices(e1.start, e2.start, epsilon) and similar_vertices(e1.end, e2.end, epsilon):
        return True
    elif similar_vertices(e1.end, e2.start, epsilon) and similar_vertices(e1.start, e2.end, epsilon):
        return True
    else:
        return False


def segment_double_key_repr(segment):
    """Returns a 2-tuple representation of a segment to be used as a key for a dictionary of the outer segments

    Format is as follows:
        1. "(start.x,start.y)-(end.x,end.y)"
        2. "(end.x,end.y)-(start.x,start.y)"
    """
    repr1 = str(segment.start.x) + "," + str(segment.start.y) + "-" + str(segment.end.x) + "," + str(segment.end.y)
    repr2 = str(segment.end.x) + "," + str(segment.end.y) + "-" + str(segment.start.x) + "," + str(segment.start.y)
    return repr1, repr2


def get_segments_of_convex_hull(points):
    """
    Builds the convex hull of the point set given, and returns the CH segments in a list

    Algorithm used for convex hull: Andrew (Already implemented in pycompgeom.algorithms module)
    N.B.: The points of the input MUST NOT include the BB points
    :param points: list of Point2 objects
    :return: List of segments of the convex_hull
    """
    ch_points = andrew(points)
    ch_segments_list = []
    for i in range(1, len(ch_points)):
        ch_segments_list.append(Segment2(ch_points[i - 1], ch_points[i]))
    # Add latest segment
    ch_segments_list.append(Segment2(ch_points[len(ch_points) - 1], ch_points[0]))
    return ch_segments_list


class DcelInputData:
    def __init__(self, bb_dist=20):
        self.vertices, self.edges, self.v_edges, self.v_vertices = [], [], [], []
        self.epsilon = 5.0
        self.is_connected_graph = True
        self.ch_segments_list = None
        self.segments_dict = {}
        # Bounding box related data members
        # bb_dist : Is the distance which is added to the main shape (min/max{x/y}) coordinates, so as to
        #           place the Bounding Box edges
        self.bb_dist, self.min_x, self.min_y, self.max_x, self.max_y = bb_dist, None, None, None, None
        # Counter for the number of edges that were created from the addition of the BB
        # Not always 4 (case of connected graph)
        self.bb_edges_number = 0

    def vertex_already_added(self, vertex):
        """Checks if the given vertex is an already added one"""
        is_similar = False
        similar_vertex = None
        for vert in self.vertices:
            if similar_vertices(vertex, vert, self.epsilon):
                is_similar = True
                similar_vertex = vert
        return is_similar, similar_vertex

    def edge_already_added(self, edge):
        """Checks if the given edge is an already added one"""
        is_similar = False
        if self.epsilon != 0:
            for e in self.edges:
                if similar_edges(edge, e, self.epsilon):
                    is_similar = True
            return is_similar
        else:
            s_repr = segment_double_key_repr(edge)
            if s_repr[0] in self.segments_dict or s_repr[1] in self.segments_dict:
                return True
            else:
                return False

    def update_bounding_box_members(self, vertex):
        """Updates the coordinates (min and max of x and y) to be used for the bounding box"""
        if vertex.x > self.max_x:
            self.max_x = vertex.x
        if vertex.y > self.max_y:
            self.max_y = vertex.y
        if vertex.x < self.min_x:
            self.min_x = vertex.x
        if vertex.y < self.min_y:
            self.min_y = vertex.y

    def add_bounding_box_elements(self):
        """Adds the new vertices and edges that were created from the addition of a bounding box"""
        d = self.bb_dist
        lower_left_v = Point2(self.min_x - d, self.min_y - d)
        lower_right_v = Point2(self.max_x + d, self.min_y - d)
        upper_right_v = Point2(self.max_x + d, self.max_y + d)
        upper_left_v = Point2(self.min_x - d, self.max_y + d)
        self.vertices += [upper_right_v, upper_left_v, lower_left_v, lower_right_v]
        self.v_vertices += [VPoint2(upper_right_v), VPoint2(upper_left_v),
                            VPoint2(lower_left_v), VPoint2(lower_right_v)]
        # CASES NEEDED (VORONOI OR TRIANGULATION)
        if self.is_connected_graph:
            # In the case that we don't have an edge whose endpoint is (inf) - (not a case of a Voronoi Diagram)
            # Create the four new segments
            self.bb_edges_number = 4
            tmp_segment = Segment2(lower_left_v, lower_right_v)
            self.edges.append(tmp_segment)
            self.v_edges.append(VSegment2(tmp_segment))
            tmp_segment = Segment2(lower_right_v, upper_right_v)
            self.edges.append(tmp_segment)
            self.v_edges.append(VSegment2(tmp_segment))
            tmp_segment = Segment2(upper_right_v, upper_left_v)
            self.edges.append(tmp_segment)
            self.v_edges.append(VSegment2(tmp_segment))
            tmp_segment = Segment2(upper_left_v, lower_left_v)
            self.edges.append(tmp_segment)
            self.v_edges.append(VSegment2(tmp_segment))
        else:
            pass

    def handle_input(self, vertex, previous_vertex, add_segment):
        """Handles the input and does the bookkeeping on adding the vertices and edges"""
        if len(self.vertices) > 0:
            # Don't add new vertex (already added before)
            vertex_result = self.vertex_already_added(vertex)
            if vertex_result[0]:
                # Create new edge if:
                #   1. It's not same with the ones already added
                #   2. The previous and current vertices aren't the same
                if not similar_vertices(previous_vertex, vertex_result[1]):
                    edge = Segment2(previous_vertex, vertex_result[1])
                    if self.edge_already_added(edge) is False:
                        self.edges.append(edge)
                        repr_tuple = segment_double_key_repr(edge)
                        self.segments_dict.update({repr_tuple[0]: edge, repr_tuple[1]: edge})
                        self.v_edges.append(VSegment2(self.edges[-1]))
                return vertex_result[1]
            else:
                self.update_bounding_box_members(vertex)
                self.vertices.append(vertex)
                self.v_vertices.append(VPoint2(self.vertices[-1]))
                if len(self.vertices) > 1 and add_segment:
                    edge = Segment2(previous_vertex, self. vertices[-1])
                    self.edges.append(edge)
                    repr_tuple = segment_double_key_repr(edge)
                    self.segments_dict.update({repr_tuple[0]: edge, repr_tuple[1]: edge})
                    self.v_edges.append(VSegment2(edge))
                return vertex
        else:
            self.update_bounding_box_members(vertex)
            self.vertices.append(vertex)
            self.v_vertices.append(VPoint2(self.vertices[-1]))
            return vertex

    def get_visual_dcel_members(self, button_in=LEFTBUTTON, button_new_segment=MIDDLEBUTTON, button_exit=RIGHTBUTTON):
        """
        Gathers all the necessary data (vertices, edges) for the Doubly Connected Edge List data structure
        :param button_in: The input button [default is LMB]
        :param button_new_segment: The new segment button (not in sequence with the previous one) [default is MMB]
        :param button_exit: The exit button [default is RMB]
        :return: Returns a tuple (vertices, edges, min_max_coords_tuple)
                1. vertices and edges, are tuples in this format (actual_object, visual_object)
                2. min_max_coords_tuple contains the min/max{x/y} coordinates and has this format:
                        (min_x, min_y, max_x, max_y)
        """
        # Boilerplate code for adding some descriptive text
        pygame.display.set_caption("Create a DCEL (no intersections with the edges)")
        my_font = pygame.font.SysFont(None, 22)
        label_1st = my_font.render("Enter segments in sequence with LMB (click for its points)", 1, (255, 255, 255))
        label_2nd = my_font.render("MMB creates new sequence of segments, right click ends input", 1, (255, 0, 0))
        window.canvas.blit(label_1st, (1, 1))
        window.canvas.blit(label_2nd, (1, 20))
        pygame.display.flip()

        previous_vertex = None
        while True:
            event = pygame.event.poll()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == button_in:
                    pos = window.cartesian(event.pos)
                    vertex = Point2.from_tuple(pos)
                    # First initialization of bounding box data members
                    if self.min_x is None and self.min_y is None and self.max_x is None and self.max_y is None:
                        self.min_x = self.max_x = vertex.x
                        self.min_y = self.max_y = vertex.y
                    previous_vertex = self.handle_input(vertex, previous_vertex, True)
                elif event.button == button_new_segment:
                    pos = window.cartesian(event.pos)
                    previous_vertex = vertex = Point2.from_tuple(pos)
                    self.handle_input(vertex, previous_vertex, False)
                elif event.button == button_exit:
                    if len(self.vertices) < 3:
                        raise ValueError("#vertices must be >= 3")
                    if len(self.edges) < 3:
                        raise ValueError("#edges must be >= 3")
                    self.ch_segments_list = get_segments_of_convex_hull(self.vertices)
                    self.add_bounding_box_elements()
                elif not should_i_quit(event):
                    event = None

    def pickle_dcel_data(self, filename=None):
        if filename is None:
            filename = "dcel_input_data-" + datetime.fromtimestamp(time()).strftime('%Y-%m-%d,%H:%M:%S') + ".bin"
        with open(filename, 'wb') as output_file:
            pickle.dump(self, output_file)

    @staticmethod
    def unpickle_dcel_data(filename):
        with file(filename, 'rb') as input_file:
            dcel_data_obj = pickle.load(input_file)
            # Re-"paint" all the visual objects
            dcel_data_obj.v_vertices = [VPoint2(v) for v in dcel_data_obj.vertices]
            dcel_data_obj.v_edges = [VSegment2(e) for e in dcel_data_obj.edges]
            return dcel_data_obj


    def __repr__(self):
        return "DCEL Data Members:\n\t[*] Segments: %s\n\t[*] Points: %s\n" \
               "\t[*] Min_x(%s),\tMax_x(%s)\n" \
               "\t[*] Min_y(%s),\tMax_y(%s)\n" % (self.edges, self.vertices, self.min_x, self.max_x, self.min_y,
                                                  self.max_y)


if __name__ == '__main__':
    dcel_data = DcelInputData(20)
    dcel_data.get_visual_dcel_members()
    print dcel_data
    dcel_data.pickle_dcel_data("test")
    dcel_test = DcelInputData.unpickle_dcel_data("test")
    print dcel_test
    pause()
    del dcel_data
