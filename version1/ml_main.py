import numpy as np
import game_main
import Settings
import matplotlib.pyplot as plt
import pyglet

Settings.ML_MODE = True

# print(game_main.player_car)
# game_main.update(1/60.0)
# frame = game_main.on_draw()
# print(frame.shape)
# plt.matshow(frame[:,:,0])
# plt.show()

window = game_main.game_window

while True:
    pyglet.clock.tick()
    window.switch_to()
    window.dispatch_events()
    window.dispatch_event('on_draw')
    window.flip()


# input("foo")