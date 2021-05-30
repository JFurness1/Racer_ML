import pyglet

pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()

def center_image(image):
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2

player_img_raw = pyglet.resource.image("car_SS.png")
player_img = pyglet.image.ImageGrid(player_img_raw, 2, 8)
for img in player_img:
    center_image(img)
# player_img_tex = pyglet.image.TextureGrid(player_img)
# center_image(player_img)