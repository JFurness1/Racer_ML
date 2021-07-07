import Settings
import numpy as np
from pyglet.window import key

class InputObject:
    def __init__(self, rot=0, accel=0):
        self.rot = np.clip(rot, -1.0, 1.0)
        self.accel = np.clip(accel, 0.0, 1.0)

class InputManager:
    def __init__(self):
        self.key_handler = key.KeyStateHandler()

    def update(self):
        if Settings.ML_MODE:
            return InputObject()
        else:
            return self.read_keyboard()

    def read_keyboard(self):
        rot = 0
        if self.key_handler[key.LEFT]:
            rot += 1
        if self.key_handler[key.RIGHT]:
            rot -= 1

        accel = 0
        if self.key_handler[key.UP]:
            accel += 1

        return InputObject(rot=rot, accel=accel)