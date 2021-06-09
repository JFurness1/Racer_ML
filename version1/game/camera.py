import numpy as np

class Camera:
    def __init__(self, batch, window):
        self.world_position = np.array((0, 0))

        self.focus = None
        self.focus_hpos = 0.5
        self.focus_vpos = 0.5

        self.batch = batch

        self.window = window
        self.width = window.width
        self.height = window.height

        self.items = []

        self.bounds_padding = 500

    def set_focus(self, focus, hpos=0.5, vpos=0.5):
        self.focus = focus
        self.focus_hpos = hpos
        self.focus_vpos = vpos

    def update(self, dt):
        if self.focus is not None:
            self.world_position[0] = self.focus.world_position[0] - self.width*self.focus_hpos
            self.world_position[1] = self.focus.world_position[1] - self.height*self.focus_vpos
        self.bounds_min = [
            self.world_position[0] - self.bounds_padding - self.focus_hpos*self.width, 
            self.world_position[1] - self.bounds_padding - self.focus_vpos*self.height]
        self.bounds_max = [
            self.world_position[0] + (1 + self.focus_hpos)*self.width + self.bounds_padding,
            self.world_position[1] + (1 + self.focus_vpos)*self.height +  self.bounds_padding]

    
    def draw(self):
        for item in self.items:
            item.x, item.y = self.transform_point(item.world_position[0], item.world_position[1])
        
    def transform_point(self, x, y):
        return x - self.world_position[0], y - self.world_position[1]


    def add_item(self, item):
        assert hasattr(item, 'x') and hasattr(item, 'y') and hasattr(item, 'world_position'), "Inappropriate object for Camera"
        
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def is_in_bounds(self, point):
        hp = self.focus_hpos*self.width
        vp = self.focus_vpos*self.height

        return point[0] >= self.world_position[0] - self.bounds_padding - hp \
                and point[0] <= self.world_position[0] + self.width + self.bounds_padding + hp \
                and point[1] >= self.world_position[1] - self.bounds_padding - vp \
                and point[1] <= self.world_position[1] + self.height + self.bounds_padding + vp
