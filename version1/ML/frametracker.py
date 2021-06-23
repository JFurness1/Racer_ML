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
            state = np.zeros((HyperParameters.FRAME_STACK_SIZE,) + self.memory[0].shape)
            state[0] = self.memory[0]
            last_good = 0
            for i in range(1, len(self.memory)):
                try:
                    state[i] = self.memory[i]
                    last_good += 1
                except IndexError:
                    state[i] = self.memory[last_good]
        else:
            state = np.array(self.memory)
        
        return state

