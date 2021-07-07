import pytorch
import numpy as np
from frametracker import FrameTracker

class Agent:

    def __init__(self):
        self.frametrack = FrameTracker()

    def decide_action(self, canvas, player):
        return