# 1,000,000-particle gravity benchmark - pure Python (no libraries)
import math, sys, time

W, H = 1500, 800
G, M, MASS, DT = 0.1, 1e8, 2.0, 0.001
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
CX, CY = W / 2, H / 2
BG, FG = 0x141414, 0xFFFFFF

s = 2463534242
def rnd():
    global s
    s ^= (s << 13) & 0xFFFFFFFF
    s ^= s >> 17
    s ^= (s << 5) & 0xFFFFFFFF
    return s / 4294967296.0

xs, ys = [], []
for _ in range(N):
    xs.append(rnd() * W)
    ys.append(rnd() * H)
pxs = [500.0] * N
pys = [500.0] * N
fb = [BG] * (W * H)

def frame():
    sqrt, atan2, cos, sin = math.sqrt, math.atan2, math.cos, math.sin
    k = G * MASS * M
    fb[:] = [BG] * (W * H)
    for i in range(N):
        x = xs[i]; y = ys[i]
        dx = x - CX; dy = y - CY
        hyp = sqrt(dx * dx + dy * dy)
        if hyp >= 1:
            theta = atan2(CY - y, CX - x)
            force = k / hyp
            px = pxs[i] + force * cos(theta) * DT
            py = pys[i] + force * sin(theta) * DT
            pxs[i] = px; pys[i] = py
            x += px / MASS * DT
            y += py / MASS * DT
            xs[i] = x; ys[i] = y
        ix = int(x); iy = int(y)
        if 0 <= ix < W and 0 <= iy < H:
            fb[iy * W + ix] = FG

frames = int(sys.argv[1]) if len(sys.argv) > 1 else 5
frame(); frame(); frame()  # warm-up (same as the other languages)
t0 = time.perf_counter()
for _ in range(frames):
    frame()
ms = (time.perf_counter() - t0) * 1000 / frames
print(f"python frames={frames} ms={ms:.3f} fps={1000/ms:.3f} check={(sum(xs)+sum(ys))/N:.6f}")
