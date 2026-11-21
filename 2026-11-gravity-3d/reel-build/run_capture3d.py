# Runs the unmodified gravity3d.py with scripted mouse/keyboard input, capturing every frame.
# usage: python run_capture3d.py <gravity3d.py> <out.mp4>
import sys, os, runpy, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "shim"))
import pygame
SRC, OUT = sys.argv[1], sys.argv[2]
# (start, end, from, to, mode)  mode: "move" | "spawn" (hold 3) | "drag" (left button) | "zin"/"zout" (wheel)
SEG = [(0, 110, (560, 320), (560, 320), "move"),
       (110, 200, (560, 320), (575, 360), "spawn"),
       (200, 240, (575, 360), (760, 600), "move"),
       (240, 360, (760, 600), (1060, 600), "drag"),
       (360, 390, (1060, 600), (940, 300), "move"),
       (390, 470, (940, 300), (950, 330), "spawn"),
       (470, 500, (950, 330), (700, 430), "move"),
       (500, 590, (700, 430), (700, 600), "drag"),
       (590, 620, (700, 600), (600, 520), "move"),
       (620, 690, (600, 520), (610, 540), "spawn"),
       (690, 730, (610, 540), (820, 600), "move"),
       (730, 910, (820, 600), (500, 500), "drag"),
       (910, 970, (500, 500), (520, 480), "zin"),
       (970, 1090, (520, 480), (820, 430), "drag"),
       (1090, 1150, (820, 430), (800, 440), "zout"),
       (1150, 1230, (800, 440), (500, 480), "drag")]
END = SEG[-1][1] + 10
def ease(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def at(f):
    for a, b, p, q, m in SEG:
        if a <= f < b:
            e = ease((f - a) / (b - a)); return (p[0] + (q[0] - p[0]) * e, p[1] + (q[1] - p[1]) * e), m, f - a
    return SEG[-1][3], "move", 0
prev = {"pos": SEG[0][2], "down": False}
def script(f):
    pos, mode, k = at(f)
    pos = (int(round(pos[0])), int(round(pos[1])))
    evs = []
    down = mode == "drag"
    if down and not prev["down"]: evs.append(dict(type=pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
    if not down and prev["down"]: evs.append(dict(type=pygame.MOUSEBUTTONUP, button=1, pos=pos))
    rel = (pos[0] - prev["pos"][0], pos[1] - prev["pos"][1])
    if rel != (0, 0): evs.append(dict(type=pygame.MOUSEMOTION, pos=pos, rel=rel))
    wheel = 0
    if mode in ("zin", "zout") and k % 6 == 0 and k < 48:
        wheel = 1 if mode == "zin" else -1
        evs.append(dict(type=pygame.MOUSEWHEEL, x=0, y=wheel))
    if f >= END: evs.append(dict(type=pygame.QUIT))
    prev.update(pos=pos, down=down)
    keys = (pygame.K_3,) if mode == "spawn" else ()
    return evs, {"pos": pos, "drag": down, "keys": keys, "wheel": wheel, "mode": mode}
pygame.CONTROL.update(script=script, out=OUT)
runpy.run_path(SRC, run_name="__main__")
json.dump(pygame.CONTROL["log"], open(OUT + ".json", "w"))
print("frames", pygame.CONTROL["frame"])
