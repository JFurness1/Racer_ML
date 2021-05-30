import numpy as np
from pyglet.window import key
from . import physicalobject, resources

class Player(physicalobject.PhysicalObject):

    def __init__(self, ss, *args, **kwargs):
        self.ss = ss
        
        super(Player, self).__init__(img=self.ss[0], *args, **kwargs)

        self.thrust = 12000.0
        self.rotate_speed = 200.0

        self.frame = 0

        self.key_handler = key.KeyStateHandler()

    def update(self, dt):

        if self.key_handler[key.LEFT]:
            self.rotate(np.radians(self.rotate_speed*dt))
            
        if self.key_handler[key.RIGHT]:
            self.rotate(-np.radians(self.rotate_speed*dt))
        self.frame = int(max(0.0, self.d_rotation)//23)%16
        self.image = self.ss[self.frame]

        if self.key_handler[key.UP]:
            self.force += self.direction*self.thrust*dt
        
        super(Player, self).update(dt)
        
    def delete(self):
        self.engine_sprite.delete()
        super(Player, self).delete()