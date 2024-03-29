import numpy as np
from pyglet import shapes
import math

import pyglet
from . import physicalobject, resources
import Settings

class Player(physicalobject.PhysicalObject):

    SKID_INTERVAL = 3   # Frames between laying down a skid mark

    MIN_SKID_SPEED = 60

    SCORE_DECAY = 60

    WALL_PENALTY = 100

    def __init__(self, ss, *args, **kwargs):
        self.ss = ss

        super(Player, self).__init__(img=self.ss[0], *args, **kwargs)

        self.score = 0

        self.thrust = 20000.0
        self.rotate_speed = 200.0

        self.frame = 3

        self.radius = 25

        self.wheel_offsets = [
            np.array((18, 36)),
            np.array((-18, 36)),
            np.array((18, -30)),
            np.array((-18, -30))
        ]

        self.skid_elapsed = 0
        self.last_skid_point = np.array(self.world_position)
        self.last_skid_d_rotation = self.d_rotation
        self.is_skidding = False

    def update(self, dt, skidman, inputs):
        
        self.rotate(inputs.rot*np.radians(self.rotate_speed*dt))

        step = 360.0/len(self.ss)
        self.frame = math.ceil((self.d_rotation)//step)
        self.image = self.ss[self.frame]

        self.force += inputs.accel*self.direction*self.thrust*dt
        
        super(Player, self).update(dt)
        self.world_position[0] = max(self.radius, self.world_position[0])

        # If we are moving sideways fast enough to trigger skid at *any* point in the 
        # skid check time. Resets when skid_elapsed ticks over
        skid_v = np.linalg.norm(self.normal_velocity)
        if skid_v >= self.MIN_SKID_SPEED:
            self.is_skidding = True

        if self.skid_elapsed == 0:
            if not Settings.ML_MODE and self.is_skidding:
                r_dir_cos = np.cos(np.radians(-self.d_rotation))
                r_dir_sin = np.sin(np.radians(-self.d_rotation))
                l_dir_cos = np.cos(np.radians(-self.last_skid_d_rotation))
                l_dir_sin = np.sin(np.radians(-self.last_skid_d_rotation))
                for offset in self.wheel_offsets:
                    rot = np.array((offset[0]*r_dir_cos - offset[1]*r_dir_sin, offset[0]*r_dir_sin + offset[1]*r_dir_cos))
                    l_rot = np.array((offset[0]*l_dir_cos - offset[1]*l_dir_sin, offset[0]*l_dir_sin + offset[1]*l_dir_cos))
                    skidman.add_skid(np.rint(self.last_skid_point+l_rot), np.rint(self.world_position+rot), self.skid_opacity(skid_v))
            self.last_skid_point[:] = self.world_position[:]
            self.last_skid_d_rotation = self.d_rotation
            self.is_skidding = False
        
        self.skid_elapsed = (self.skid_elapsed + 1)%self.SKID_INTERVAL

        self.score += self.world_position[0] - self.last_position[0] - dt*self.SCORE_DECAY

    def skid_opacity(self, v):
        return np.max((0.0, np.min((1.0, np.tanh((v - self.MIN_SKID_SPEED)/(3.0*self.MIN_SKID_SPEED))))))

    def delete(self):
        self.engine_sprite.delete()
        super(Player, self).delete()