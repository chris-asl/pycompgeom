# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
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


def point_key_repr(*args):
    if len(args) == 2 and type(args) is tuple:
        return str(args[0]) + "," + str(args[1])
    elif len(args) == 1 and isinstance(args[0], Point2):
        return str(args[0].x) + "," + str(args[0].y)
    else:
        raise TypeError("point_key_repr: Expected type \"tuple\" or \"Point2\", got: " + str(type(args)))


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


def line(p1, p2):
    """
    This method calculates the equation of a line that passes through p1 and p2 points
    :param p1: Point2
    :param p2: Point2
    :return:    A function f(x) that computes the value of the line equation that passes through p1, p2 points
    """
    horizontal_line = False
    vertical_line = False
    if p1.x == p2.x:
        horizontal_line = True
    if p1.y == p2.y:
        vertical_line = True
    coef = (p1.y - p2.y) / (p1.x - p2.x)
    inv_coef = 1 / coef if coef != 0 else 0
    b = p1.y - coef * p1.x

    def result(param, is_function_of_x):
        """
        Returns the other coordinate of the equation, depending on the is_function_of_x parameter
        That is, it returns y, if is_function_of_x is true, x, otherwise

        :param param: int The x or y coordinate
        :param is_function_of_x: Boolean Indicates whether we need an f(x) or f^(-1)(y) solution
        :return: The x or y coordinate that holds for the other given coordinate
        """
        if is_function_of_x:
            if not horizontal_line:
                return coef * param + b
            else:
                return p1.y
        else:
            if not vertical_line:
                return inv_coef * (param - b)
            else:
                return p1.x
    return result


class DcelInputData:
    def __init__(self, bb_dist=20):
        self.vertices, self.edges, self.v_edges, self.v_vertices = [], [], [], []
        # The starting segment at the case of non-connected graph
        self.starting_segment = None
        self.epsilon = 5.0
        self.is_connected_graph = True
        self.ch_segments_list = None
        self.outer_segments_list = None
        # Temporary storage for initial infinite segments
        self.inf_segments_list = []
        self.v_inf_segments_list = []
        self.v_inf_vertices_list = []
        # Hashing the segments using two keys (start,end) and (end, start) for each one
        self.points_to_segment_dict = {}
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
                break
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
            if s_repr[0] in self.points_to_segment_dict or s_repr[1] in self.points_to_segment_dict:
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
            # We need to iterate through the inf segments and find their incision points with the BB lines
            # Storing then, each intersection point to a respective list (lower/ right/ upper/ left) of BB line points
            # Finally, for each BB line, sort its points (from the list above) by x or y coord (depending on which line)
            # and start walking the line and creating new segments

            # Find BB line equations
            bb_upper_line = upper_left_v.y
            bb_lower_line = lower_left_v.y
            bb_left_line = upper_left_v.x
            bb_right_line = upper_right_v.x
            bb_upper_line_points = []
            bb_lower_line_points = []
            bb_left_line_points = []
            bb_right_line_points = []
            for inf_segment, inf_point in self.inf_segments_list:
                inf_line_equation = line(inf_segment.start, inf_segment.end)
                tmp_s = VSegment2(inf_segment, MAGENTA)
                # Covering the vertical bb lines first
                vert_result = DcelInputData.check_intersection(inf_line_equation, inf_point, bb_left_line,
                                                               bb_right_line, bb_lower_line, bb_upper_line, True)
                hor_result = DcelInputData.check_intersection(inf_line_equation, inf_point, bb_left_line,
                                                              bb_right_line, bb_lower_line, bb_upper_line, False)
                # The usual case is that one of the above points is None, the degenerate case is when the
                # segment is a diagonal of the BB, in that case
                is_on_left_bb_line = is_on_lower_bb_line = False
                if vert_result is not None and hor_result is None:
                    intersection_point, minimum_dist, is_on_left_bb_line = vert_result
                elif vert_result is None and hor_result is not None:
                    intersection_point, minimum_dist, is_on_lower_bb_line = hor_result
                elif vert_result is not None and hor_result is not None:
                    vert_intersection_point, vert_minimum_dist, is_on_left_bb_line = vert_result
                    hor_intersection_point, hor_minimum_dist, is_on_lower_bb_line = hor_result
                    intersection_point, minimum_dist, _ = vert_result if vert_minimum_dist < hor_minimum_dist \
                        else hor_result
                else:
                    raise ValueError("Erroneous intersection detection\nSth went terribly wrong")

                self.vertices.append(Point2.from_tuple(intersection_point))
                self.v_vertices.append(VPoint2(self.vertices[-1], YELLOW))
                if vert_result is not None and hor_result is None:
                    if is_on_left_bb_line:
                        bb_left_line_points.append(self.vertices[-1])
                    else:
                        bb_right_line_points.append(self.vertices[-1])
                elif vert_result is None and hor_result is not None:
                    if is_on_lower_bb_line:
                        bb_lower_line_points.append(self.vertices[-1])
                    else:
                        bb_upper_line_points.append(self.vertices[-1])
                elif vert_result is not None and hor_result is not None:
                    if vert_minimum_dist < hor_minimum_dist:
                        if is_on_left_bb_line:
                            bb_left_line_points.append(self.vertices[-1])
                        else:
                            bb_right_line_points.append(self.vertices[-1])
                    else:
                        if is_on_lower_bb_line:
                            bb_lower_line_points.append(self.vertices[-1])
                        else:
                            bb_upper_line_points.append(self.vertices[-1])

                other_v = inf_segment.start if inf_segment.start != inf_point else inf_segment.end
                self.edges.append(Segment2(other_v, self.vertices[-1]))
                repr_tuple = segment_double_key_repr(self.edges[-1])
                self.points_to_segment_dict.update({repr_tuple[0]: self.edges[-1], repr_tuple[1]: self.edges[-1]})
                self.v_edges.append(VSegment2(self.edges[-1], YELLOW))

                del tmp_s
            del self.v_inf_segments_list, self.v_inf_vertices_list, self.inf_segments_list
            # Start creating the new segments of the BB
            self.outer_segments_list = []
            _, upper_segments = self.create_bb_segments(True, bb_upper_line_points, upper_left_v, upper_right_v)
            self.starting_segment, lower_segments = \
                self.create_bb_segments(True, bb_lower_line_points, lower_left_v, lower_right_v)
            _, left_segments = self.create_bb_segments(False, bb_left_line_points, lower_left_v, upper_left_v)
            _, right_segments = self.create_bb_segments(False, bb_right_line_points, lower_right_v, upper_right_v)
            self.outer_segments_list.extend(upper_segments + lower_segments + left_segments + right_segments)

    def create_bb_segments(self, is_horizontal_movement, bb_line_points, start_point, end_point):
        """
        Sort the bb line points by x or y coordinate, walk the line of points and create the segments

        :param is_horizontal_movement: Boolean True, if bb line is a horizontal one, False, otherwise
        :param bb_line_points: List of Point2 The list of the points that belong at the specific bb line
        :param start_point: Point2 The starting point of the bb line
        :param end_point: Point2 The end point of the bb line
        :return: A 2-tuple (The first segment that was created, all the segments in a list)
        """
        # Will attempt sorting with an optimized version, given that we might have a lot of points to process
        if len(bb_line_points) == 0:
            self.edges.append(Segment2(start_point, end_point))
            self.v_edges.append(VSegment2(self.edges[-1]))
            self.bb_edges_number += 1
            return self.edges[-1], [self.edges[-1]]
        try:
            import operator
        except ImportError:
            key_function = lambda p: p.x if is_horizontal_movement else lambda p: p.y
        else:
            key_function = operator.attrgetter("x") if is_horizontal_movement else operator.attrgetter("y")
        bb_line_points.sort(key=key_function, reverse=False)
        # Start walking the line and creating new segments
        first_segment = Segment2(start_point, bb_line_points[0])
        segments = [first_segment]
        self.edges.append(first_segment)
        self.v_edges.append(VSegment2(self.edges[-1]))
        for i in range(1, len(bb_line_points)):
            self.edges.append(Segment2(bb_line_points[i-1], bb_line_points[i]))
            segments.append(self.edges[-1])
            self.v_edges.append(VSegment2(self.edges[-1]))
        self.edges.append(Segment2(bb_line_points[len(bb_line_points) - 1], end_point))
        segments.append(self.edges[-1])
        self.v_edges.append(VSegment2(self.edges[-1]))
        self.bb_edges_number += len(bb_line_points) + 1
        return first_segment, segments

    @staticmethod
    def check_intersection(inf_line_equation, inf_point, bb_left_line, bb_right_line, bb_lower_line, bb_upper_line,
                           check_vertical_bb_lines):
        """
        Finds the minimum distance intersection point of the line equation given and the two vertical/horizontal BB
        lines, if any

        :param inf_line_equation: Segment2 The line equation of the infinite segment
        :param inf_point: Point2 The infinite point
        :param bb_left_line: int The BB left line (x-coord)
        :param bb_right_line: int The BB right line (x-coord)
        :param bb_lower_line: int The BB upper line (y-coord)
        :param bb_upper_line: int The BB lower line (y-coord)
        :return:    A 3-tuple (minimum_distance_intersection_point, minimum_distance_to_inf_point,
                    is_on_first_bb_line), or None if there isn't any intersection point
                    is_on_first_bb_line: This shows that if check_vertical_bb_lines(=True), then the intersection point
                    was on the left one, or if check_vertical_bb_lines(=False), the intersection point was on the lower
                    bb line
        """
        # Setting some aliases so as to use the same method for finding the intersection points of the equation with
        # both the vertical and horizontal lines of the BB
        if check_vertical_bb_lines:
            main_lines = bb_left_line, bb_right_line
            other_lines = bb_lower_line, bb_upper_line
            other_coord = 1
        else:
            main_lines = bb_lower_line, bb_upper_line
            other_lines = bb_left_line, bb_right_line
            other_coord = 0

        if check_vertical_bb_lines:
            inters_p1 = (main_lines[0], int(inf_line_equation(main_lines[0], check_vertical_bb_lines)))
            inters_p2 = (main_lines[1], int(inf_line_equation(main_lines[1], check_vertical_bb_lines)))
        else:
            inters_p1 = (int(inf_line_equation(main_lines[0], check_vertical_bb_lines)), main_lines[0])
            inters_p2 = (int(inf_line_equation(main_lines[1], check_vertical_bb_lines)), main_lines[1])
        dist = lambda p: ((p[0] - inf_point.x) ** 2 + (p[1] - inf_point.y) ** 2) ** 0.5
        # Check if point belongs into the BB
        if inters_p1[other_coord] < other_lines[0] or inters_p1[other_coord] > other_lines[1]:
            inters_p1 = None
        if inters_p2[other_coord] < other_lines[0] or inters_p2[other_coord] > other_lines[1]:
            inters_p2 = None
        # Both points are out of the BB
        if inters_p1 is None and inters_p2 is None:
            return None
        # One point is into the BB, return (p, dist(p, inf_point))
        elif inters_p1 is not None and inters_p2 is None:
            return inters_p1, dist(inters_p1), True
        elif inters_p1 is None and inters_p2 is not None:
            return inters_p2, dist(inters_p2), False
        # Both points are into the BB, return the min{ dist(p1, inf_point), dist(p2, inf_point) } in the form of a
        # minimum_distance_point, minimum_distance
        else:
            distances = (dist(inters_p1), dist(inters_p2))
            if distances[0] <= distances[1]:
                return inters_p1, distances[0], True
            else:
                return inters_p2, distances[1], False

    def handle_input(self, vertex, previous_vertex, add_segment, is_inf_point):
        """
        Handles the input and does the bookkeeping on adding the vertices and edges

        :param vertex: Point2 The latest vertex
        :param previous_vertex: Point2 The previously added vertex
        :param add_segment: Boolean Should add segment flag
        :param is_inf_point: Boolean Vertex is infinite point
        """
        if len(self.vertices) > 0:
            # Don't add new vertex (already added before)
            v_was_already_added, already_added_vertex = self.vertex_already_added(vertex)
            if v_was_already_added:
                # Create new edge if:
                #   1. It's not same with the ones already added
                #   2. The previous and current vertices aren't the same
                if not similar_vertices(previous_vertex, already_added_vertex):
                    edge = Segment2(previous_vertex, already_added_vertex)
                    if self.edge_already_added(edge) is False:
                        self.edges.append(edge)
                        repr_tuple = segment_double_key_repr(edge)
                        self.points_to_segment_dict.update({repr_tuple[0]: edge, repr_tuple[1]: edge})
                        self.v_edges.append(VSegment2(self.edges[-1]))
                return already_added_vertex
            else:
                if not is_inf_point:
                    self.update_bounding_box_members(vertex)
                    self.vertices.append(vertex)
                    self.v_vertices.append(VPoint2(self.vertices[-1]))
                else:
                    self.v_inf_vertices_list.append(VPoint2(vertex, RED))
                if len(self.vertices) > 1 and add_segment:
                    edge = Segment2(previous_vertex, vertex)
                    if not is_inf_point:
                        self.edges.append(edge)
                        repr_tuple = segment_double_key_repr(edge)
                        self.points_to_segment_dict.update({repr_tuple[0]: edge, repr_tuple[1]: edge})
                        self.v_edges.append(VSegment2(edge))
                    else:
                        self.inf_segments_list.append((edge, vertex))
                        self.v_inf_segments_list.append(VSegment2(edge, CYAN))
                return vertex
        else:
            if not is_inf_point:  # First point must not be an inf one
                self.update_bounding_box_members(vertex)
                self.vertices.append(vertex)
                self.v_vertices.append(VPoint2(self.vertices[-1]))
                return vertex
            else:
                return None

    def get_visual_dcel_members(self, button_in=LEFTBUTTON, button_new_segment=MIDDLEBUTTON,
                                button_inf_point=RIGHTBUTTON):
        """
        Gathers all the necessary data (vertices, edges) for the Doubly Connected Edge List data structure
        Notes:
        1. End input with ESCAPE button
        2. [Case of non-connected graph]
            To insert an infinite point (denoted by RED colour), you have to have the previous point (start of the
            infinite segment) already created. Do that by either :
            i. Using LMB and then RMB, or
            ii. If you already have created the start point and continued with not-creating the inf-segment: click on
                the start point with MMB (so as to "select" that point as start) and then RMB to add the infinity point

        :param button_in:   The new point button (creates point and segment - in sequence with the previous segment)
                            [default is LMB]
        :param button_new_segment:  The new starting point button (creates point and segment - not in sequence with the
                                    previous segment) [default is MMB]
        :param button_inf_point:    The new infinite point button (creates infinite point and segment - in sequence
                                    with the previous segment) [default is RMB]
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
                pos = window.cartesian(event.pos)
                vertex = Point2.from_tuple(pos)
                if event.button == button_in:
                    # First initialization of bounding box data members
                    if self.min_x is None and self.min_y is None and self.max_x is None and self.max_y is None:
                        self.min_x = self.max_x = vertex.x
                        self.min_y = self.max_y = vertex.y
                    previous_vertex = self.handle_input(vertex, previous_vertex, True, False)
                elif event.button == button_new_segment:
                    previous_vertex = vertex
                    previous_vertex = self.handle_input(vertex, previous_vertex, False, False)
                elif event.button == button_inf_point:
                    previous_vertex = self.handle_input(vertex, previous_vertex, True, True)
                elif not should_i_quit(event):
                    event = None
            elif event.type == pygame.KEYDOWN:
                print event
                if event.key == pygame.K_ESCAPE:
                    if len(self.vertices) < 3:
                        raise ValueError("#vertices must be >= 3")
                    if len(self.edges) < 3:
                        raise ValueError("#edges must be >= 3")
                    if len(self.inf_segments_list) > 0:
                        self.is_connected_graph = False
                    if self.is_connected_graph:
                        self.ch_segments_list = get_segments_of_convex_hull(self.vertices)
                    self.add_bounding_box_elements()
                    return

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
    dcel_data.pickle_dcel_data()
    # dcel_data.add_bounding_box_elements()
    # dcel_test = DcelInputData.unpickle_dcel_data("dcel_input_data-2015-07-10,19:20:51.bin")
    # print dcel_test
    pause()
    del dcel_data
