import numpy as np

class Camera:

    WORLD_WIDTH = 800
    WORLD_HEIGHT = 600

    def __init__(self, batch, window):

        self.focus = None
        self.focus_hpos = 0.0
        self.focus_vpos = 0.0

        self.batch = batch

        self.window = window
        self.width = window.width
        self.height = window.height

        self.h_scale = self.width/self.WORLD_WIDTH
        self.v_scale = self.height/self.WORLD_HEIGHT

        self.world_position = np.array((0, 0))
        self.bounds_min = [self.world_position[0], self.world_position[1]]
        self.bounds_max = [self.world_position[0] + self.WORLD_WIDTH, self.world_position[1] + self.WORLD_HEIGHT]

        self.items = []

        self.bounds_padding = 500

    def set_focus(self, focus, hpos=0.5, vpos=0.5):
        self.focus = focus
        self.focus_hpos = hpos
        self.focus_vpos = vpos

    def update(self, dt):
        if self.focus is not None:
            self.world_position[0] = self.focus.world_position[0] - self.WORLD_WIDTH*self.focus_hpos
            self.world_position[1] = self.focus.world_position[1] - self.WORLD_HEIGHT*self.focus_vpos
        self.bounds_min = [
            self.world_position[0] - self.bounds_padding - self.focus_hpos*self.WORLD_WIDTH, 
            self.world_position[1] - self.bounds_padding - self.focus_vpos*self.WORLD_HEIGHT]
        self.bounds_max = [
            self.world_position[0] + (1 + self.focus_hpos)*self.WORLD_WIDTH + self.bounds_padding,
            self.world_position[1] + (1 + self.focus_vpos)*self.WORLD_HEIGHT +  self.bounds_padding]

    
    def draw(self):
        for item in self.items:
            item.x, item.y = self.transform_point(item.world_position[0], item.world_position[1])
            item.scale_x = self.h_scale
            item.scale_y = self.v_scale
        
    def transform_point(self, x, y):
        return (x - self.world_position[0])*self.h_scale, (y - self.world_position[1])*self.v_scale

    def transform_line(self, pt1, pt2, ln):
        ln.x, ln.y = self.transform_point(pt1[0], pt1[1])
        ln.x2, ln.y2 = self.transform_point(pt2[0], pt2[1])

    def transform_triangle(self, pt1, pt2, pt3, tri):
        # Takes a triangle in world space and applies the camera space transform
        tri.x, tri.y = self.transform_point(pt1[0], pt1[1])
        tri.x2, tri.y2 = self.transform_point(pt2[0], pt2[1])
        tri.x3, tri.y3 = self.transform_point(pt3[0], pt3[1])


    def add_item(self, item):
        assert hasattr(item, 'x') and hasattr(item, 'y') and hasattr(item, 'world_position'), "Inappropriate object for Camera"
        
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def is_in_bounds(self, point):
        return point[0] >= self.bounds_min[0] \
                and point[0] <= self.bounds_max[0] \
                and point[1] >= self.bounds_min[1] \
                and point[1] <= self.bounds_max[1]
    
    def is_in_horizontal_bounds(self, point):
        return point[0] >= self.bounds_min[0] and point[0] <= self.bounds_max[0]
