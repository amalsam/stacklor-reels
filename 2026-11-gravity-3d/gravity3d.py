# 3D gravity particles  -  pygame + numpy
# hold 3 : spawn particles at the mouse    drag : orbit camera    wheel : zoom
import math
import numpy as np
import pygame

W, H = 1500, 800
G, M, MASS, DT = 0.1, 1e8, 2.0, 0.001
SPEED = 2200        # starting momentum of new particles
FOV = 900           # camera focal length in pixels
BG = 20

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("gravity 3d")
font = pygame.font.Font("freesansbold.ttf", 22)
clock = pygame.time.Clock()

pos = np.zeros((0, 3))      # x, y, z of every particle
mom = np.zeros((0, 3))      # momentum x, y, z
yaw, pitch, dist = 0.5, 0.35, 1400.0

# faint rings on the x-z plane so you can feel the 3D space
a = np.linspace(0, 2 * math.pi, 720)
GRID = np.vstack([np.c_[r * np.cos(a), 0 * a, r * np.sin(a)] for r in (250, 500, 750)])


def camera():
    cy, sy = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)
    ry = np.array([[cy, 0, -sy], [0, 1, 0], [sy, 0, cy]])
    rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    return rx @ ry                      # world -> camera rotation


def project(p):
    c = p @ camera().T
    z = c[:, 2] + dist
    sx = W / 2 + c[:, 0] * FOV / z
    sy = H / 2 - c[:, 1] * FOV / z
    return sx, sy, z


def generate_cloud(mx, my, n=150):
    global pos, mom
    R = camera()
    # point under the mouse, on the plane through the sun facing the camera
    centre = np.array([(mx - W / 2) * dist / FOV, -(my - H / 2) * dist / FOV, 0]) @ R
    p = centre + np.random.normal(0, 20, (n, 3))
    view = np.array([0, 0, 1.0]) @ R            # direction the camera looks
    t = np.cross(view, p)                        # spin around the view axis
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    pos = np.vstack([pos, p])
    mom = np.vstack([mom, t * SPEED * np.random.uniform(0.4, 1.2, (n, 1))])


def move():
    global pos, mom
    hyp = np.linalg.norm(pos, axis=1, keepdims=True)
    ok = hyp >= 1
    force = G * MASS * M / np.maximum(hyp, 1)
    direction = -pos / np.maximum(hyp, 1)       # unit vector towards the sun
    mom = np.where(ok, mom + force * direction * DT, mom)
    pos = np.where(ok, pos + mom / MASS * DT, pos)


def splat(p, bright):
    sx, sy, z = project(p)
    x, y = sx.astype(int), sy.astype(int)
    vis = (z > 1) & (x >= 0) & (x < W) & (y >= 0) & (y < H)
    shade = bright * np.clip(1.6 - z[vis] / dist, 0.3, 1.0)    # near = bright
    return np.bincount(x[vis] * H + y[vis], shade, W * H)


def draw():
    screen.fill((BG, BG, BG))
    sx, sy, z = project(np.zeros((1, 3)))
    pygame.draw.circle(screen, "yellow", (sx[0], sy[0]), max(2, int(14 * FOV / z[0])))
    light = splat(GRID, 80) + splat(pos, 255)
    light = np.minimum(light, 255).reshape(W, H, 1)
    pix = pygame.surfarray.pixels3d(screen)
    np.maximum(pix, light.astype(np.uint8), out=pix)
    del pix
    for i, txt in enumerate([f"particles : {len(pos)}", f"Fps : {int(clock.get_fps())}"]):
        label = font.render(txt, True, "white")
        rect = label.get_rect()
        rect.midtop = (110, 100 + i * 30)
        screen.blit(label, rect)


dragging = False
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            dragging = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            dragging = False
        elif e.type == pygame.MOUSEMOTION and dragging:
            yaw -= e.rel[0] * 0.005
            pitch = max(-1.5, min(1.5, pitch + e.rel[1] * 0.005))
        elif e.type == pygame.MOUSEWHEEL:
            dist = max(300, min(4000, dist * 0.9 ** e.y))

    if pygame.key.get_pressed()[pygame.K_3]:
        generate_cloud(*pygame.mouse.get_pos())

    move()
    draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
