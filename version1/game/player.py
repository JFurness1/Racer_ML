import numpy as np
from pyglet.window import key
from pyglet import shapes
from . import physicalobject, resources

class Player(physicalobject.PhysicalObject):

    def __init__(self, ss, *args, **kwargs):
        self.ss = ss
        
        super(Player, self).__init__(img=self.ss[0], *args, **kwargs)

        self.thrust = 20000.0
        self.rotate_speed = 200.0

        self.frame = 0

        self.key_handler = key.KeyStateHandler()

        self.radius = 45
        self.collision = shapes.Arc(self.world_position[0], self.world_position[1], self.radius, closed=True, color=(255,255,255))

    def update(self, dt, camera):
        if self.key_handler[key.LEFT]:
            self.rotate(np.radians(self.rotate_speed*dt))    
        if self.key_handler[key.RIGHT]:
            self.rotate(-np.radians(self.rotate_speed*dt))
            
        self.frame = int((max(0.0, self.d_rotation) + 15)//23)%16
        self.image = self.ss[self.frame]

        if self.key_handler[key.UP]:
            self.force += self.direction*self.thrust*dt
        
        super(Player, self).update(dt)
        self.collision.x, self.collision.y = camera.transform_point(self.world_position[0], self.world_position[1])

    def delete(self):
        self.engine_sprite.delete()
        super(Player, self).delete()