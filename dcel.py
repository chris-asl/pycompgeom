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


def vertex_already_added(vertex, vertices, epsilon=5.0):
    """Checks if the given vertex is an already added one"""
    is_similar = False
    similar_vertex = None
    for vert in vertices:
        if similar_vertices(vertex, vert, epsilon):
            is_similar = True
            similar_vertex = vert
    return is_similar, similar_vertex


def edge_already_added(edge, edges, epsilon=5.0):
    """Checks if the given edge is an already added one"""
    is_similar = False
    for e in edges:
        if similar_edges(edge, e, epsilon):
            is_similar = True
    return is_similar


def handle_input(vertices, v_vertices, edges, v_edges, vertex, previous_vertex, add_segment):
    """Handles the input and does the bookkeeping on adding the vertices and edges"""
    if len(vertices) > 0:
        # Don't add new vertex (already added before)
        vertex_result = vertex_already_added(vertex, vertices)
        if vertex_result[0]:
            # Create new edge if:
            #   1. It's not same with the ones already added
            #   2. The previous and current vertices aren't the same
            if not similar_vertices(previous_vertex, vertex_result[1]):
                edge = Segment2(previous_vertex, vertex_result[1])
                if edge_already_added(edge, edges) is False:
                    edges.append(edge)
                    v_edges.append(VSegment2(edges[-1]))
            return vertex_result[1]
        else:
            vertices.append(vertex)
            v_vertices.append(VPoint2(vertices[-1]))
            if len(vertices) > 1 and add_segment:
                edges.append(Segment2(previous_vertex, vertices[-1]))
                v_edges.append(VSegment2(edges[-1]))
            return vertex
    else:
        vertices.append(vertex)
        v_vertices.append(VPoint2(vertices[-1]))
        return vertex


def get_vdcel(button_in=LEFTBUTTON, button_new_segment=MIDDLEBUTTON, button_exit=RIGHTBUTTON):
    """Gathers all the necessary data (vertices, edges) for the Doubly Connected Edge List data structure"""
    # Boilerplate code for adding some descriptive text
    pygame.display.set_caption("Create a DCEL (no intersections with the edges)")
    background = window.background
    my_font = pygame.font.SysFont(None, 22)
    label_1st = my_font.render("Enter segments in sequence with LMB (click for its points)", 1, (255, 255, 255))
    label_2nd = my_font.render("MMB creates new sequence of segments, right click ends input", 1, (255, 0, 0))
    window.canvas.blit(label_1st, (1, 1))
    window.canvas.blit(label_2nd, (1, 20))
    pygame.display.flip()

    vertices, v_vertices = [], []
    previous_vertex = None
    edges, v_edges = [], []
    while True:
        event = pygame.event.poll()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == button_in:
                pos = window.cartesian(event.pos)
                vertex = Point2.from_tuple(pos)
                previous_vertex = handle_input(vertices, v_vertices, edges, v_edges, vertex, previous_vertex, True)
            elif event.button == button_new_segment:
                pos = window.cartesian(event.pos)
                previous_vertex = vertex = Point2.from_tuple(pos)
                handle_input(vertices, v_vertices, edges, v_edges, vertex, previous_vertex, False)
            elif event.button == button_exit:
                vert = (vertices, v_vertices)
                edg = (edges, v_edges)
                return vert, edg
            elif not should_i_quit(event):
                event = None


if __name__ == '__main__':
    # Get VSegments, but only accept them if the new
    # starts at the start/end of a previous one
    segments = []
    points_set = set()
    vertices_pack, edges_pack = get_vdcel()
    del vertices_pack
    del edges_pack