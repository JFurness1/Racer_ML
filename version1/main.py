import pyglet
from game import resources
from game.physicalobject import PhysicalObject
from game.player import Player
from game.camera import Camera
from game.track import Track
import numpy as np


game_window = pyglet.window.Window(800, 600)
fps_display = pyglet.window.FPSDisplay(window=game_window)
main_batch = pyglet.graphics.Batch()

camera = Camera(main_batch, game_window)


score_label = pyglet.text.Label(text="Score: 0", x=10, y=460, batch=main_batch)
dbg_label = pyglet.text.Label(text="N/A", x=10, y=game_window.height, anchor_y='top', batch=main_batch)
dbg_label2 = pyglet.text.Label(text="N/A", x=10, y=game_window.height-20, anchor_y='top', batch=main_batch)
cam_label = pyglet.text.Label(text="N/A", x=10, y=game_window.height-40, anchor_y='top', batch=main_batch)

player_car = Player(resources.player_img, x=400, y=200, batch=main_batch)
game_window.push_handlers(player_car.key_handler)

game_objects = [player_car]

for item in game_objects:
    camera.add_item(item)
camera.focus = player_car

track = Track(main_batch, game_window.width, 2*game_window.height, v_segments=20, h_spacing=300)
for i, n in enumerate(track.node_list):
    print("node",i,":",n)

player_car.move_to(track.node_list[0][0], track.node_list[0][1])

for i in range(10):
    print("Track Segment ", i)
    track.generate_next_track_segment()

global accumulated_time
accumulated_time = 0

dbg_txt = "Position: ({:.1f}, {:.1f}) Direction: ({:.1f}, {:.1f}) Velocity: {:.1f} ({:.1f}, {:.1f}) Rotation: {:.1f} ({:2d})"
dbg_txt2 = "Aligned Velocity: {:.1f} ({:.1f}, {:.1f}) Normal Velocity: {:.1f} ({:.1f}, {:.1f})"
cam_txt = "Camera Position: ({:d}, {:d})"

@game_window.event
def on_draw():
    game_window.clear()
    fps_display.draw()
    main_batch.draw()

def update(dt):
    global accumulated_time
    accumulated_time += dt
    fps = 1/60.0
    while accumulated_time >= fps:
        for obj in game_objects:
            obj.update(fps)

        track.update(player_car.world_position[0])
        accumulated_time -= fps

    camera.update(dt)
    track.draw(camera)
    camera.draw()
    
    dbg_label.text = dbg_txt.format(player_car.world_position[0], player_car.world_position[1], 
        player_car.direction[0], player_car.direction[1], 
        player_car.speed, player_car.velocity[0], player_car.velocity[1], 
        player_car.d_rotation, player_car.frame)

    dbg_label2.text = dbg_txt2.format(
        np.linalg.norm(player_car.aligned_velocity), player_car.aligned_velocity[0], player_car.aligned_velocity[1], 
        np.linalg.norm(player_car.normal_velocity), player_car.normal_velocity[0], player_car.normal_velocity[1]
        )
    cam_label.text = cam_txt.format(camera.world_position[0], camera.world_position[1])

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()