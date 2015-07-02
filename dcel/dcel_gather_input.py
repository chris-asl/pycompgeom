# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Chris Aslanoglou'
from pycompgeom import *
from math import sqrt


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


class DcelInputData:
    def __init__(self):
        self.vertices, self.edges, self.v_edges, self.v_vertices = [], [], [], []
        self.epsilon = 5.0
        self.is_connected_graph = True
        # Bounding box related data members
        # bb_dist : Is the distance which is added to the main shape (min/max{x/y}) coordinates, so as to
        #           place the Bounding Box edges
        self.bb_dist, self.min_x, self.min_y, self.max_x, self.max_y = 0, None, None, None, None
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
        for e in self.edges:
            if similar_edges(edge, e, self.epsilon):
                is_similar = True
        return is_similar

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
        self.bb_dist = int(self.bb_dist) + 1
        d = self.bb_dist
        lower_left_v = Point2(self.min_x - d, self.min_y - d)
        lower_right_v = Point2(self.max_x + d, self.min_y - d)
        upper_right_v = Point2(self.max_x + d, self.max_y + d)
        upper_left_v = Point2(self.min_x - d, self.max_y + d)
        print [upper_right_v, upper_left_v, lower_left_v, lower_right_v]
        self.vertices += [upper_right_v, upper_left_v, lower_left_v, lower_right_v]
        self.v_vertices += [VPoint2(upper_right_v), VPoint2(upper_left_v), VPoint2(lower_left_v), VPoint2(lower_right_v)]
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
                    edge_length = edge.length()
                    if edge_length > self.bb_dist:
                        self.bb_dist = edge_length
                    if self.edge_already_added(edge) is False:
                        self.edges.append(edge)
                        self.v_edges.append(VSegment2(self.edges[-1]))
                return vertex_result[1]
            else:
                self.update_bounding_box_members(vertex)
                self.vertices.append(vertex)
                self.v_vertices.append(VPoint2(self.vertices[-1]))
                if len(self.vertices) > 1 and add_segment:
                    self.edges.append(Segment2(previous_vertex,self. vertices[-1]))
                    self.v_edges.append(VSegment2(self.edges[-1]))
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
                    self.add_bounding_box_elements()
                    vert = (self.vertices, self.v_vertices)
                    edg = (self.edges, self.v_edges)
                    min_max_coords_tuple = (self.min_x, self.min_y, self.max_x, self.max_y)
                    return vert, edg, min_max_coords_tuple
                elif not should_i_quit(event):
                    event = None

    def __repr__(self):
        return "DCEL Data Members:\n\t[*] Segments: %s\n\t[*] Points: %s\n" \
               "\t[*] Min_x(%s),\tMax_x(%s)\n" \
               "\t[*] Min_y(%s),\tMax_y(%s)\n" % (self.edges, self.vertices, self.min_x, self.max_x, self.min_y, self.max_y)


if __name__ == '__main__':
    dcel_data = DcelInputData()
    vertices_pack, edges_pack, min_max_coords_tuple, bb_dist = dcel_data.get_visual_dcel_members()
    print dcel_data
    pause()
    del vertices_pack, edges_pack, dcel_data
