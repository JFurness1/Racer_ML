import pyglet
import numpy as np
from pyglet import shapes

game_window = pyglet.window.Window(800, 600)
main_batch = pyglet.graphics.Batch()

cp = np.array((100, 100))
radius = 40
circle = shapes.Arc(cp[0], cp[1], radius, closed=True, color=(255,255,255), batch=main_batch)

p1 = np.array((200, 250))
p2 = np.array((200, 550))
line = pyglet.shapes.Line(p1[0], p1[1], p2[0], p2[1], batch=main_batch)
global flipflop
flipflop = True

resolution = pyglet.shapes.Line(0, 0, 0, 0, color=(80, 255, 80), batch=main_batch)
resolution.visible = False
resolution_c = pyglet.shapes.Arc(0, 0, radius, color=(80, 255, 80), batch=main_batch)
resolution_c.visible = False

@game_window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if pyglet.window.mouse.LEFT == buttons:
        cp[0] = x
        cp[1] = y
        circle.x = cp[0]
        circle.y = cp[1]

@game_window.event
def on_mouse_release(x, y, button, modifiers):
    global flipflop
    if button == pyglet.window.mouse.RIGHT:
        if flipflop:
            p1[0] = x
            p1[1] = y
            line.x = p1[0]
            line.y = p1[1]
        else:
            p2[0] = x
            p2[1] = y
            line.x2 = p2[0]
            line.y2 = p2[1]
        flipflop = not flipflop

@game_window.event
def on_draw():
    game_window.clear()
    main_batch.draw()

def update(dt):
    res = circle_line_collision(cp, radius, p1, p2)

    if res is None:
        circle.color = (255, 255, 255)
        resolution.visible = False
        resolution_c.visible = False
    else:
        circle.color = (255, 0, 0)
        resolution.x = circle.x
        resolution.y = circle.y
        resolution.x2 = circle.x + res['normal'][0]*res['depth']
        resolution.y2 = circle.y + res['normal'][1]*res['depth']
        resolution.visible = True

        resolution_c.x = circle.x + res['normal'][0]*res['depth']
        resolution_c.y = circle.y + res['normal'][1]*res['depth']
        resolution_c.visible = True

def circle_line_collision(cpt, rad, lpt1, lpt2):
    # Bounding box coarse graining
    bb_l = min(lpt1[0], lpt2[0]) - rad
    bb_r = max(lpt1[0], lpt2[0]) + rad
    bb_t = max(lpt1[1], lpt2[1]) + rad
    bb_b = min(lpt1[1], lpt2[1]) - rad
    if cpt[0] < bb_l or cpt[0] > bb_r or cpt[1] > bb_t or cpt[1] < bb_b:
        return None

    loc_cpt = cpt - lpt1
    loc_lpt2 = lpt2 - lpt1
    norm_lpt2 = np.linalg.norm(loc_lpt2)

    # If circle is centered on point 1 or 2 then resolution is arbitrarily away from line
    if np.allclose(cpt, lpt1):
        return {'normal':-loc_lpt2/norm_lpt2, 'depth':rad}
    if np.allclose(cpt, lpt2):
        return {'normal':loc_lpt2/norm_lpt2, 'depth':rad}

    p1_dist = np.linalg.norm(loc_cpt)
    p2_sep = cpt - lpt2
    p2_dist = np.linalg.norm(p2_sep)

    projection = loc_lpt2*np.dot(loc_cpt, loc_lpt2)/np.dot(loc_lpt2, loc_lpt2)
    normp = np.linalg.norm(projection)
    rejection = loc_cpt - projection
    normr = np.linalg.norm(rejection)

    pos_dir = np.dot(projection, loc_lpt2)

    if (normr > rad # Rejection is larger than rad
            or (normp > norm_lpt2 + rad and p2_dist > rad) # projection along line is past p2
            or (pos_dir < 0 and p1_dist > rad)): # we are the other way and past p1
        return None
    
    if normp > norm_lpt2:
        # Must be close to p2 but past end of line
        if p2_dist > rad:
            return None
        else:
            return {'normal':p2_sep/p2_dist, 'depth':rad - p2_dist}
    
    if p1_dist < rad and pos_dir < 0:
        # Past end of line but close to p1
        return {'normal':loc_cpt/p1_dist, 'depth':rad - p1_dist}

    if normr == 0.0:
        # Circle lies exactly on the line
         return {'normal':np.array((-projection[1], projection[0]))/normp, 'depth':rad}

    return {'normal':rejection/normr, 'depth':rad - normr}

if __name__ == "__main__":
    pyglet.clock.schedule_interval(update, 1/15.0)
    pyglet.app.run()