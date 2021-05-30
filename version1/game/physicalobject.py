import pyglet
import numpy as np

class PhysicalObject(pyglet.sprite.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.world_position = np.array((0.0, 0.0))

        self.velocity = np.array((0.0, 0.0))
        self.speed = 0.0
        self.force = np.array((0.0, 0.0))

        self.aligned_friction = 0.5
        self.normal_friction = 2.0

        # Unit vector pointing in direction of 
        self.direction = np.array((0.0, 1.0))
        self.d_rotation = 0.0
        self.set_sprite_rot()
        self.aligned_velocity = np.array((0.0, 0.0))
        self.normal_velocity = np.array((0.0, 0.0))

    def update(self, dt):
        self.speed = np.linalg.norm(self.velocity)
        if self.speed > 0:
            vunit = self.velocity/self.speed
            self.aligned_velocity = np.dot(vunit, self.direction)*self.velocity
            self.normal_velocity = self.velocity - self.aligned_velocity
        else:
            self.aligned_velocity[0] = self.aligned_velocity[1] = 0.0
            self.normal_velocity[0] = self.normal_velocity[1] = 0.0

        friction = -1.0*self.velocity
        self.force += friction

        self.velocity += self.force*dt
        self.force[0] = self.force[1] = 0.0

        self.world_position += self.velocity*dt
    
    def rotate(self, rot):
        self.direction[0] = self.direction[0]*np.cos(rot) - self.direction[1]*np.sin(rot)
        self.direction[1] = self.direction[0]*np.sin(rot) + self.direction[1]*np.cos(rot)
        self.direction /= np.linalg.norm(self.direction)
        self.set_sprite_rot()

    def set_sprite_rot(self):
        self.d_rotation = (np.degrees(-np.arctan2(self.direction[1], self.direction[0])) + 90.0) % 360.0

    def check_bounds(self):
        min_x = self.image.width / 2
        min_y = self.image.height / 2
        max_x = 800 - self.image.width / 2
        max_y = 600 - self.image.height / 2

        if self.world_position[0] < min_x:
            self.world_position[0] = min_x
            self.velocity[0] *= -1
        if self.world_position[0] > max_x:
            self.world_position[0] = max_x
            self.velocity[0] *= -1
        
        if self.world_position[1] < min_y:
            self.world_position[1] = min_y
            self.velocity[1] *= -1
        if self.world_position[1] > max_y:
            self.world_position[1] = max_y
            self.velocity[1] *= -1

    def move_to(self, x, y):
        self.world_position[0] = x
        self.world_position[1] = y