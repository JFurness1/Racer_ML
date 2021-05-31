from numpy.lib.utils import byte_bounds
import pyglet
from pyglet import shapes
import numpy as np

class Track:
    def __init__(self, batch, window_width, track_height, h_spacing=200, v_segments=5, track_width=100):
        self.world_position = np.array((0.0, 0.0))
        
        self.batch = batch

        self.h_spacing = h_spacing
        self.v_spacing = track_height/v_segments
        self.h_segments = window_width/h_spacing
        self.v_segments = v_segments

        self.max_segments = self.h_segments*self.v_segments

        self.segments = []

        # Initial track point
        self.node_list = [(0, self.v_spacing*v_segments//2)]

        self.line_width = 5

        self.new_segment_pad = max(window_width + 100, h_spacing)

        self.hide_offscreen = True
        
        self.track_width = 100

    def generate_next_track_segment(self):
        next_h = self.node_list[-1][0] + self.h_spacing
        next_v = np.random.randint(self.v_segments)*self.v_spacing
        
        last = self.node_list[-1]
        self.segments.append(TrackSegment(last[0], last[1], next_h, next_v, self.track_width, self.batch))
        
        self.node_list.append((next_h, next_v))
   

    def draw(self, camera):
        for i, seg in enumerate(self.segments):
            if seg.is_on_camera(camera) or not self.hide_offscreen:
                seg.g_upper.visible = True
                seg.g_lower.visible = True
                seg.shift_for_camera(camera)
            else:
                seg.g_upper.visible = False
                seg.g_lower.visible = False

    def update(self, player_x):
        if player_x > self.node_list[-1][0] - self.new_segment_pad:
            self.generate_next_track_segment()

class TrackSegment:
    def __init__(self, x, y, x2, y2, track_width, batch, previous=None, next=None, *args, **kwargs):

        self.world_position = np.array((x, y))
        self.world_position_2 = np.array((x2, y2))

        self.dx = x2 - x
        self.dy = y2 - y

        self.track_width = track_width

        self.upper = np.array((-self.dy, self.dx))
        self.upper = self.track_width*self.upper/np.linalg.norm(self.upper) + self.world_position
        self.upper_2 = np.array((-self.dy, self.dx))
        self.upper_2 = self.track_width*self.upper_2/np.linalg.norm(self.upper_2) + self.world_position_2

        self.lower = np.array((self.dy, -self.dx))
        self.lower = self.track_width*self.lower/np.linalg.norm(self.lower) + self.world_position
        self.lower_2 = np.array((self.dy, -self.dx))
        self.lower_2 = self.track_width*self.lower_2/np.linalg.norm(self.lower_2) + self.world_position_2

        self.g_upper = pyglet.shapes.Line(self.upper[0], self.upper[1], self.upper_2[0], self.upper_2[1], batch=batch)
        self.g_lower = pyglet.shapes.Line(self.lower[0], self.lower[1], self.lower_2[0], self.lower_2[1], batch=batch)

        self.g_upper.visible = False
        self.g_lower.visible = False

        if previous is not None:
            self.set_previous(previous)
        if next is not None:
            self.set_next(next)

    def set_previous(self, prev):
        self.previous_node = prev

    def set_next(self, next):
        self.next_node = next

    def is_on_camera(self, camera):
        return (self.world_position[0] > camera.bounds_min[0] \
                and self.world_position[0] < camera.bounds_max[0]) \
            or (self.world_position_2[0] > camera.bounds_min[0] \
                and self.world_position_2[0] < camera.bounds_max[0]) \
            or (self.world_position[0] < camera.bounds_min[0] 
                and self.world_position_2[0] > camera.bounds_max[0])
        # return camera.is_in_bounds((self.world_position[0] , self.world_position[1])) or camera.is_in_bounds((self.world_position_2[0], self.world_position_2[1]))

    def shift_for_camera(self, camera):
        self.g_upper.x, self.g_upper.y = camera.transform_point(self.upper[0], self.upper[1])
        self.g_upper.x2, self.g_upper.y2 = camera.transform_point(self.upper_2[0], self.upper_2[1])

        self.g_lower.x, self.g_lower.y = camera.transform_point(self.lower[0], self.lower[1])
        self.g_lower.x2, self.g_lower.y2 = camera.transform_point(self.lower_2[0], self.lower_2[1])