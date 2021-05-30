import numpy as np

class Camera:
    def __init__(self, batch, window):
        self.world_position = np.array((0, 0))

        self.focus = None

        self.batch = batch

        self.window = window
        self.width = window.width
        self.height = window.height

        self.items = []

        self.bounds_padding = 100

    def update(self, dt):
        if self.focus is not None:
            self.world_position[0] = self.focus.world_position[0] - self.width//2
            self.world_position[1] = self.focus.world_position[1] - self.height//2

    
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
        return point[0] >= self.world_position[0] - self.bounds_padding \
            and point[0] <= self.world_position[0] + self.width + self.bounds_padding \
            and point[1] >= self.world_position[1] - self.bounds_padding \
            and point[1] <= self.world_position[1] + self.height + self.bounds_padding

