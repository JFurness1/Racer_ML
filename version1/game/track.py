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

        self.seg_index = 0
        self.last_seg = 0

    def generate_next_track_segment(self):
        next_h = self.node_list[-1][0] + self.h_spacing
        next_v = np.random.randint(self.v_segments)*self.v_spacing
        
        last = self.node_list[-1]
        self.segments.append(TrackSegment(last[0], last[1], next_h, next_v, self.track_width, self.batch))
        if len(self.segments) > 1:
            self.segments[-1].set_previous(self.segments[-2])
            self.segments[-2].set_next(self.segments[-1])

        self.node_list.append((next_h, next_v))

    def draw(self, camera):
        for i, seg in enumerate(self.segments):
            if seg.is_on_camera(camera) or not self.hide_offscreen:
                seg.set_visible(True)
                seg.shift_for_camera(camera)
                if i == self.last_seg:
                    seg.g_upper.color = (255, 255, 255)
                    seg.g_lower.color = (255, 255, 255)
                    seg.g_bevel.color = (255, 255, 255)
                    try:
                        seg.previous_node.g_bevel.color = (255, 255, 255)
                    except AttributeError:
                        pass
                
                if i == self.seg_index:
                    seg.g_upper.color = (0, 255, 0)
                    seg.g_lower.color = (0, 255, 0)
                    seg.g_bevel.color = (0, 255, 0)
                    try:
                        seg.previous_node.g_bevel.color = (0, 255, 0)
                    except AttributeError:
                        pass
            else:
                seg.set_visible(False)

    def update(self, dt, player):
        if player.world_position[0] > self.node_list[-1][0] - self.new_segment_pad:
            self.generate_next_track_segment()

        # Collision detection
        self.last_seg = self.seg_index
        self.seg_index = int(player.world_position[0]//self.h_spacing)

        c_seg = self.segments[self.seg_index]

        lines = [
            (c_seg.upper, c_seg.upper_2, "upper"),
            (c_seg.lower, c_seg.lower_2, "lower"),
            (c_seg.bevel, c_seg.bevel_2, "bevel")
        ]
        
        try:
            lines.append((c_seg.previous_node.bevel, c_seg.previous_node.bevel_2, "prev_bevel"))
        except AttributeError:
            pass

        hit = False
        for l in lines:
            if self.circle_line_collision(player.world_position, player.radius, l[0], l[1]) is not None:
                player.collision.color = (0, 0, 255)
                hit = True
                break

        if not hit:
            player.collision.color = (255, 255, 255)

    def circle_line_collision(self, cpt, rad, lpt1, lpt2):
        loc_cpt = cpt - lpt1
        loc_lpt2 = lpt2 - lpt1

        if loc_cpt[0] < rad or loc_cpt[0] > loc_lpt2[0] + rad:
            # circle is too far from the ends of the line to be possible
            return None
        
        projection = loc_cpt*np.dot(loc_cpt, loc_lpt2)/np.dot(loc_lpt2, loc_lpt2)
        rejection = loc_cpt - projection

        if np.linalg.norm(rejection) > rad:
            return None
        
        normal = rejection/np.linalg.norm(rejection)
        depth = np.linalg.norm(rejection) - rad

        return {'normal':normal, 'depth':depth}


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
        self.g_bevel = pyglet.shapes.Line(0, 0, 0, 0, batch=batch)


        self.g_upper.visible = False
        self.g_lower.visible = False
        self.g_bevel.visible = False

        self.bevel = None
        self.bevel_2 = None

        self.previous_node = None
        self.next_node = None

        if previous is not None:
            self.set_previous(previous)
        if next is not None:
            self.set_next(next)

    def set_previous(self, prev):
        self.previous_node = prev

    def set_next(self, next):
        self.next_node = next

        intersection = find_line_intersections(self.upper, self.upper_2, self.next_node.upper, self.next_node.upper_2)

        if intersection is not None:
            print("Joining Upper")
            # Upper lines are joined
            
            self.upper_2[0], self.upper_2[1] = intersection
            self.next_node.upper[0], self.next_node.upper[1] = intersection

            self.bevel = np.array((self.lower_2[0], self.lower_2[1]))
            self.bevel_2 = np.array((self.next_node.lower[0], self.next_node.lower[1]))
            
        else:
            print("Joining Lower")
            # lower are joined
            intersection = find_line_intersections(self.lower, self.lower_2, self.next_node.lower, self.next_node.lower_2)
            
            self.lower_2[0], self.lower_2[1] = intersection
            self.next_node.lower[0], self.next_node.lower[1] = intersection

            self.bevel = np.array((self.upper_2[0], self.upper_2[1]))
            self.bevel_2 = np.array((self.next_node.upper[0], self.next_node.upper[1]))
        
        self.g_bevel.x = self.bevel[0]
        self.g_bevel.y = self.bevel[1]
        self.g_bevel.x2 = self.bevel_2[0]
        self.g_bevel.y2 = self.bevel_2[1]

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

        self.g_bevel.x, self.g_bevel.y = camera.transform_point(self.bevel[0], self.bevel[1])
        self.g_bevel.x2, self.g_bevel.y2 = camera.transform_point(self.bevel_2[0], self.bevel_2[1])

    def set_visible(self, visible):
        self.g_lower.visible = visible
        self.g_upper.visible = visible
        self.g_bevel.visible = visible


def find_line_intersections(a1, a2, b1, b2):
    print("Intersection ({:.1f}, {:.1f}) - ({:.1f}, {:.1f}), ({:.1f}, {:.1f}) - ({:.1f}, {:.1f})".format(
        a1[0], a1[1], a2[0], a2[1], b1[0], b1[1], b2[0], b2[1]
    ))
    # Warning, will throw error if either line is vertical. Should never happen.
    a_m = (a2[1] - a1[1])/(a2[0] - a1[0])
    a_c = a1[1] - a_m*a1[0]
    
    b_m = (b2[1] - b1[1])/(b2[0] - b1[0])
    b_c = b1[1] - b_m*b1[0]

    # if a_m == b_m and a_c != b_c:
    #     # Parallel Lines
    #     return None
    if a_m == b_m and a_c == b_c:
        # Eqivalent lines, arbitrarily return a2 as intersection point
        return a2[0], a2[1]


    ix = (b_c - a_c)/(a_m - b_m)
    iy = a_m*ix + a_c

    print("Found at ({:.1f}, {:.1f})".format(ix, iy))

    if ix < a1[0] or ix > a2[0] or ix < b1[0] or ix > b2[0]:
        # Intersection happened outside the line segments
        print("No intersection", ix < a1[0], ix > a2[0], ix < b1[0], ix > b2[0])
        return None
    else:
        return ix, iy