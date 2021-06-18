import numpy as np
from pyglet.window import key
from pyglet import shapes
from . import physicalobject, resources

class Player(physicalobject.PhysicalObject):

    SKID_INTERVAL = 3   # Frames between laying down a skid mark

    MIN_SKID_SPEED = 60

    def __init__(self, ss, *args, **kwargs):
        self.ss = ss
        
        super(Player, self).__init__(img=self.ss[0], *args, **kwargs)

        self.thrust = 20000.0
        self.rotate_speed = 200.0

        self.frame = 3

        self.key_handler = key.KeyStateHandler()

        self.radius = 45

        rad_turn = np.radians(45)
        wheel_offsets = np.array((np.sin(rad_turn), np.cos(rad_turn)))*self.radius
        self.wheel_offsets = [
            wheel_offsets,
            wheel_offsets*-1,
            np.array((-wheel_offsets[0], wheel_offsets[1])),
            np.array((wheel_offsets[0], -wheel_offsets[1]))
        ]

        self.skid_elapsed = 0
        self.last_skid_point = np.array(self.world_position)
        self.last_skid_d_rotation = self.d_rotation
        self.is_skidding = False

    def update(self, dt, skidman):
        if self.key_handler[key.LEFT]:
            self.rotate(np.radians(self.rotate_speed*dt))    
        if self.key_handler[key.RIGHT]:
            self.rotate(-np.radians(self.rotate_speed*dt))
            
        self.frame = int((max(0.0, self.d_rotation) + 15)//23)%16
        self.image = self.ss[self.frame]

        if self.key_handler[key.UP]:
            self.force += self.direction*self.thrust*dt
        
        super(Player, self).update(dt)
        self.world_position[0] = max(self.radius, self.world_position[0])

        # If we are moving sideways fast enough to trigger skid at *any* point in the 
        # skid check time. Resets when skid_elapsed ticks over
        skid_v = np.linalg.norm(self.normal_velocity)
        if skid_v >= self.MIN_SKID_SPEED:
            self.is_skidding = True

        if self.skid_elapsed == 0:
            if self.is_skidding:
                r_dir_cos = np.cos(np.radians(self.d_rotation))
                r_dir_sin = np.sin(np.radians(self.d_rotation))
                l_dir_cos = np.cos(np.radians(self.last_skid_d_rotation))
                l_dir_sin = np.sin(np.radians(self.last_skid_d_rotation))
                for offset in self.wheel_offsets:
                    rot = np.array((offset[0]*r_dir_cos - offset[1]*r_dir_sin, offset[0]*r_dir_sin + offset[1]*r_dir_cos))
                    l_rot = np.array((offset[0]*l_dir_cos - offset[1]*l_dir_sin, offset[0]*l_dir_sin + offset[1]*l_dir_cos))
                    skidman.add_skid(np.rint(self.last_skid_point+l_rot), np.rint(self.world_position+rot), self.skid_opacity(skid_v))
            self.last_skid_point[:] = self.world_position[:]
            self.last_skid_d_rotation = self.d_rotation
            self.is_skidding = False
        
        self.skid_elapsed = (self.skid_elapsed + 1)%self.SKID_INTERVAL

    def skid_opacity(self, v):
        return np.max((0.0, np.min((1.0, np.tanh((v - self.MIN_SKID_SPEED)/(3.0*self.MIN_SKID_SPEED))))))

    def delete(self):
        self.engine_sprite.delete()
        super(Player, self).delete()