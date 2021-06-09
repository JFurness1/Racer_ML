from typing import Type
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

        self.new_segment_pad = max(2*window_width, h_spacing)

        self.hide_offscreen = True
        
        self.track_width = 100

        self.seg_index = 0
        self.last_seg = 0

        self.wall_friction = 0.8

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
        if player.world_position[0] > self.segments[-1].world_position[0] - self.new_segment_pad:
            self.generate_next_track_segment()

        # Collision detection
        self.last_seg = self.seg_index
        self.seg_index = int(player.world_position[0]//self.h_spacing)

        lines = []

        for i in range(-1, 1):
            if self.seg_index + i < 0:
                continue

            c_seg = self.segments[self.seg_index + i]

            lines += [
                (c_seg.upper, c_seg.upper_2),
                (c_seg.lower, c_seg.lower_2)
            ]

            if c_seg.bevel is not None:
                lines.append((c_seg.bevel, c_seg.bevel_2))
        
        hit = list(filter(None,
            [self.circle_line_collision(player.world_position, player.radius, l[0], l[1]) for l in lines]))

        
        player.collision.color = (255, 255, 255)
        
        best_hit = {'dist':None}
        for h in hit:
            pos = player.world_position + h['normal']*h['depth']
            dist = np.linalg.norm(player.last_position - pos)
            if best_hit['dist'] is None or dist < best_hit['dist']:
                best_hit['dist'] = dist
                best_hit['normal'] = h['normal']
                best_hit['depth'] = h['depth']
            player.collision.color = (255, 0, 0)
        
        if best_hit['dist'] is not None:
            # increase displacement by 1 pixel to avoid 
            print("Hit!", best_hit['normal'], best_hit['depth'])
            player.world_position += best_hit['normal']*(best_hit['depth'] + 1)
            player.reflect_velocity(best_hit['normal'], scale=self.wall_friction)

    def circle_line_collision(self, cpt, rad, lpt1, lpt2):
        if np.allclose(lpt1, lpt2):
            # Two points are so close the line will be unstable
            return None 

        # Bounding box coarse graining
        bb_l = min(lpt1[0], lpt2[0]) - rad
        bb_r = max(lpt1[0], lpt2[0]) + rad
        bb_t = max(lpt1[1], lpt2[1]) + rad
        bb_b = min(lpt1[1], lpt2[1]) - rad
        if cpt[0] < bb_l or cpt[0] > bb_r or cpt[1] > bb_t or cpt[1] < bb_b:
            return None

        loc_cpt = cpt - lpt1
        loc_lpt2 = lpt2 - lpt1
        norm_lpt2 = np.linalg.norm(loc_lpt2)

        # If circle is centered on point 1 or 2 then resolution is arbitrarily away from line
        if np.allclose(cpt, lpt1):
            return {'normal':-loc_lpt2/norm_lpt2, 'depth':rad}
        if np.allclose(cpt, lpt2):
            return {'normal':loc_lpt2/norm_lpt2, 'depth':rad}

        p1_dist = np.linalg.norm(loc_cpt)
        p2_sep = cpt - lpt2
        p2_dist = np.linalg.norm(p2_sep)

        projection = loc_lpt2*np.dot(loc_cpt, loc_lpt2)/np.dot(loc_lpt2, loc_lpt2)
        normp = np.linalg.norm(projection)
        rejection = loc_cpt - projection
        normr = np.linalg.norm(rejection)

        pos_dir = np.dot(projection, loc_lpt2)

        if (normr > rad # Rejection is larger than rad
                or (normp > norm_lpt2 + rad and p2_dist > rad) # projection along line is past p2
                or (pos_dir < 0 and p1_dist > rad)): # we are the other way and past p1
            return None
        
        if normp > norm_lpt2:
            # Must be close to p2 but past end of line
            if p2_dist > rad:
                return None
            else:
                return {'normal':p2_sep/p2_dist, 'depth':rad - p2_dist}
        
        if p1_dist < rad and pos_dir < 0:
            # Past end of line but close to p1
            return {'normal':loc_cpt/p1_dist, 'depth':rad - p1_dist}

        if normr == 0.0:
            # Circle lies exactly on the line
            return {'normal':np.array((-projection[1], projection[0]))/normp, 'depth':rad}

        return {'normal':rejection/normr, 'depth':rad - normr}


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
        # TODO: No need for bevels if parallel segments
        self.next_node = next

        intersection = find_line_intersections(self.upper, self.upper_2, self.next_node.upper, self.next_node.upper_2)

        if intersection is not None:
            # Upper lines are joined
            
            self.upper_2[0], self.upper_2[1] = intersection
            self.next_node.upper[0], self.next_node.upper[1] = intersection

            self.bevel = np.array((self.lower_2[0], self.lower_2[1]))
            self.bevel_2 = np.array((self.next_node.lower[0], self.next_node.lower[1]))
            
        else:
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
        try:
            self.g_bevel.x, self.g_bevel.y = camera.transform_point(self.bevel[0], self.bevel[1])
            self.g_bevel.x2, self.g_bevel.y2 = camera.transform_point(self.bevel_2[0], self.bevel_2[1])
        except TypeError:
            pass

    def set_visible(self, visible):
        self.g_lower.visible = visible
        self.g_upper.visible = visible
        self.g_bevel.visible = visible


def find_line_intersections(a1, a2, b1, b2):
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

    if ix < a1[0] or ix > a2[0] or ix < b1[0] or ix > b2[0]:
        # Intersection happened outside the line segments
        return None
    else:
        return ix, iy