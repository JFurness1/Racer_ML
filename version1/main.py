from typing import Set
import pyglet
from game import resources
from game.player import Player
from game.camera import Camera
from game.track import Track
from game.skidmarks import SkidmarkManager
import Settings
import numpy as np


game_window = pyglet.window.Window(Settings.RENDER_WIDTH, Settings.RENDER_HEIGHT)
if Settings.ML_MODE:
    pyglet.gl.glClearColor(0, 0, 0, 1)
else:
    pyglet.gl.glClearColor(153/255.0, 255/255.0, 204/255.0, 1)
    fps_display = pyglet.window.FPSDisplay(window=game_window)

main_batch = pyglet.graphics.Batch()
background_batch = pyglet.graphics.Batch()
skid_batch = pyglet.graphics.Batch()

camera = Camera(main_batch, game_window)

if not Settings.ML_MODE:
    dbg_label = pyglet.text.Label(text="N/A", x=10, y=camera.height, anchor_y='top', batch=main_batch, color=(0,0,0,255))
    dbg_label2 = pyglet.text.Label(text="N/A", x=10, y=camera.height-20, anchor_y='top', batch=main_batch, color=(0,0,0,255))
    cam_label = pyglet.text.Label(text="N/A", x=10, y=camera.height-40, anchor_y='top', batch=main_batch, color=(0,0,0,255))
    score_label = pyglet.text.Label(text="Score: 0", x=10, y=camera.height-60, anchor_y='top', batch=main_batch, color=(0,0,0,255))

player_car = Player(resources.player_img, x=400, y=200, batch=main_batch)

player_car.visible = not Settings.ML_MODE

game_window.push_handlers(player_car.key_handler)

game_objects = [player_car]

for item in game_objects:
    camera.add_item(item)
camera.set_focus(player_car, hpos=0.25)

track = Track(background_batch, camera.WORLD_WIDTH, 2*camera.WORLD_HEIGHT, v_segments=3, h_spacing=300)
skidman = SkidmarkManager(skid_batch, MAX_SKIDS=194*(not Settings.ML_MODE))

for i in range(10):
    track.generate_next_track_segment()

player_car.move_to(track.segments[0].world_position[0], track.segments[0].world_position[1])
player_car.turn_to_face([track.segments[0].dx, track.segments[0].dy])

global accumulated_time
accumulated_time = 0

dbg_txt = "Position: ({:.1f}, {:.1f}) Direction: ({:.1f}, {:.1f}) Velocity: {:.1f} ({:.1f}, {:.1f}) Rotation: {:.1f} ({:2d})"
dbg_txt2 = "Aligned Velocity: {:.1f} ({:.1f}, {:.1f}) Normal Velocity: {:.1f} ({:.1f}, {:.1f})"
cam_txt = "Camera Position: ({:d}, {:d}), Segment Index: {:d}, # tris: {:d}"
score_txt = "Score: {:.1f}"


@game_window.event
def on_draw():
    game_window.clear()
    if not Settings.ML_MODE:
        fps_display.draw()
    background_batch.draw()
    skid_batch.draw()
    main_batch.draw()

    # This code seems to show how to get the frame as a pixel array
    if Settings.ML_MODE:
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        image_data = buffer.get_image_data()
        arr = np.frombuffer(image_data.get_data(), dtype=np.uint8)

        arr = arr.reshape(buffer.height, buffer.width, 4)
        print(arr.shape)


def update(dt):
    global accumulated_time
    accumulated_time += dt
    fps = 1/60.0
    while accumulated_time >= fps:
        for obj in game_objects:
            obj.update(fps, skidman)

        track.update(fps, player_car)
        accumulated_time -= fps

    camera.update(dt)
    track.draw(camera)
    skidman.draw(camera)
    camera.draw()
    
    if not Settings.ML_MODE:
        dbg_label.text = dbg_txt.format(player_car.world_position[0], player_car.world_position[1], 
            player_car.direction[0], player_car.direction[1], 
            player_car.speed, player_car.velocity[0], player_car.velocity[1], 
            player_car.d_rotation, player_car.frame)

        dbg_label2.text = dbg_txt2.format(
            np.linalg.norm(player_car.aligned_velocity), player_car.aligned_velocity[0], player_car.aligned_velocity[1], 
            np.linalg.norm(player_car.normal_velocity), player_car.normal_velocity[0], player_car.normal_velocity[1]
            )
        cam_label.text = cam_txt.format(camera.world_position[0], camera.world_position[1], track.seg_index, len(track.triangle_list))

        score_label.text = score_txt.format(player_car.score)

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/120.0)
    pyglet.app.run()