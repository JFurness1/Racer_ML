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

        self.vertical_chance = 0.25

        self.line_width = 5

        self.new_segment_pad = max(window_width + 100, h_spacing)

    def generate_next_track_segment(self):
        next_h = self.node_list[-1][0] + self.h_spacing
        next_v = np.random.randint(self.v_segments)*self.v_spacing
        
        last = self.node_list[-1]
        self.segments.append(TrackSegment(last[0], last[1], next_h, next_v, width=self.line_width, batch=self.batch))
        
        self.node_list.append((next_h, next_v))

        if np.random.random() < self.vertical_chance:
            print("Adding vertical Segment")
            last = self.node_list[-1]
            while next_v == last[1]:
                next_v = np.random.randint(self.v_segments)
            
            self.segments.append(TrackSegment(last[0], last[1], next_h, next_v, width=self.line_width, batch=self.batch))
            self.node_list.append((next_h, next_v))
    

    def draw(self, camera):
        for i, seg in enumerate(self.segments):
            if seg.is_on_camera(camera):
                seg.visible = True
                seg.shift_for_camera(camera)
            else:
                seg.visible = False

    def update(self, player_x):
        if player_x > self.node_list[-1][0] - self.new_segment_pad:
            self.generate_next_track_segment()

class TrackSegment(shapes.Line):
    def __init__(self, x, y, x2, y2, *args, **kwargs):
        super(TrackSegment, self).__init__(x, y, x2, y2, *args, **kwargs)

        self.world_position = np.array((x, y))
        self.world_position_2 = np.array((x2, y2))

        self.dx = x2 - x
        self.dy = y2 - y

        print("ADDING SEGMENT: ({:.1f}, {:.1f}) -> ({:.1f}, {:.1f})".format(x, y, x2, y2))

    def is_on_camera(self, camera):
        return camera.is_in_bounds((self.world_position[0] , self.world_position[1])) or camera.is_in_bounds((self.world_position_2[0], self.world_position_2[1]))

    def shift_for_camera(self, camera):
        self.x, self.y = camera.transform_point(self.world_position[0], self.world_position[1])
        self.x2, self.y2 = camera.transform_point(self.world_position_2[0], self.world_position_2[1])