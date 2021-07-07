import pyglet

pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()

def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

player_img_raw = pyglet.resource.image("car.png")
player_img = pyglet.image.ImageGrid(player_img_raw, 3, 12)

for img in player_img:
    center_image(img)
