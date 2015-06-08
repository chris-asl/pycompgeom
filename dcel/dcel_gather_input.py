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
    return sqrt((v1.x - v2.x)**2 + (v1.y - v2.y)**2) < epsilon


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
        # Bounding box data members
        self.min_x, self.min_y, self.max_x, self.max_y = None, None, None, None
        self.min_x_vertex, self.min_y_vertex, self.max_x_vertex, self.max_y_vertex = None, None, None, None

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
            self.max_x_vertex = vertex
        if vertex.y > self.max_y:
            self.max_y = vertex.y
            self.max_y_vertex = vertex
        if vertex.x < self.min_x:
            self.min_x = vertex.x
            self.min_x_vertex = vertex
        if vertex.y < self.min_y:
            self.min_y = vertex.y
            self.min_y_vertex = vertex.y

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
        """Gathers all the necessary data (vertices, edges) for the Doubly Connected Edge List data structure"""
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
                        self.max_y_vertex = self.max_x_vertex = self.min_x_vertex = self.min_y_vertex = vertex
                    previous_vertex = self.handle_input(vertex, previous_vertex, True)
                elif event.button == button_new_segment:
                    pos = window.cartesian(event.pos)
                    previous_vertex = vertex = Point2.from_tuple(pos)
                    self.handle_input(vertex, previous_vertex, False)
                elif event.button == button_exit:
                    vert = (self.vertices, self.v_vertices)
                    edg = (self.edges, self.v_edges)
                    return vert, edg
                elif not should_i_quit(event):
                    event = None

    def __repr__(self):
        return "DCEL Data Members:\n\t[*] Segments: %s\n\t[*] Points: %s\n" \
               "\t[*] Min_x(%s),\tMax_x(%s)\n" \
               "\t[*] Min_y(%s),\tMax_y(%s)\n" % (self.edges, self.vertices, self.min_x, self.max_x, self.min_y, self.max_y)


if __name__ == '__main__':
    dcel_data = DcelInputData()
    vertices_pack, edges_pack = dcel_data.get_visual_dcel_members()
    print dcel_data
    pause()
    del vertices_pack, edges_pack, dcel_data
