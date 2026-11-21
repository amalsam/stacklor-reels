# Writes the scripted mouse/keyboard input for the headless gravity3d.cpp run:
# one line per frame "mouse_x mouse_y left_button key_3 wheel". Same moves as the Python reel.
import sys
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
def ease(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
with open(sys.argv[1], "w") as f:
    for a, b, p, q, m in SEG:
        for k in range(b - a):
            e = ease(k / (b - a))
            x, y = round(p[0] + (q[0] - p[0]) * e), round(p[1] + (q[1] - p[1]) * e)
            wheel = (1 if m == "zin" else -1) if m in ("zin", "zout") and k % 6 == 0 and k < 48 else 0
            f.write(f"{x} {y} {int(m == 'drag')} {int(m == 'spawn')} {wheel}\n")
    for _ in range(10): f.write(f"{x} {y} 0 0 0\n")
