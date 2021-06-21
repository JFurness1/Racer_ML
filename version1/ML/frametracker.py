import numpy as np
import HyperParameters
from collections import dequeue

class FrameTracker:
    def __init__(self, init_frames=[]):
        self.memory = dequeue(init_frames)

    def add_frame(self, frame):
        self.memory.appendleft(frame)
        if len(self.memory) > HyperParameters.FRAME_STACK_SIZE:
            self.memory.pop()
    
    def get_frames(self):
        assert len(self.memory) > 0, "Memory must have at least one frame to return shape"
        
        if len(self.memory) < HyperParameters.FRAME_STACK_SIZE:
            out = np.zeros((HyperParameters.FRAME_STACK_SIZE,) + self.memory[0].shape)
            for i, frame in enumerate(self.memory):
                out[i] = frame
            return out
        else:
            return np.array(self.memory)

