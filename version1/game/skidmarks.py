import pyglet
from pyglet import shapes
import numpy as np

class SkidmarkManager:
    def __init__(self, batch, MAX_SKIDS=192):
        self.batch = batch
        self.MAX_SKIDS = MAX_SKIDS

        self.skid_ptr = 0

        self.skid_list = [Skidmark(batch) for i in range(self.MAX_SKIDS)]

    def draw(self, camera):
        for skid in self.skid_list:
            camera.transform_line(skid.world_pt1, skid.world_pt2, skid.g)

    def add_skid(self, start, finish, alpha):
        self.skid_list[self.skid_ptr].refresh(start, finish, alpha)
        self.skid_ptr = (self.skid_ptr + 1)%self.MAX_SKIDS

class Skidmark:
    SKID_THICKNESS = 3
    BASE_COLOR = (0, 0, 0)

    def __init__(self, batch):
        self.world_pt1 = np.zeros((2))
        self.world_pt2 = np.zeros((2))
        self.alpha = 0
        self.batch = batch

        self.g = pyglet.shapes.Line(self.world_pt1[0], self.world_pt1[1], self.world_pt2[0], self.world_pt2[1], width=self.SKID_THICKNESS, color=(0, 0, 0), batch=batch)
        self.g.visible = False
    
    def refresh(self, pt1, pt2, alpha):
        self.world_pt1 = np.array(pt1)
        self.world_pt2 = np.array(pt2)
        self.alpha = alpha

        self.g.color = self.BASE_COLOR
        self.g.opacity = int(self.alpha*255)
        self.g.visible = True
