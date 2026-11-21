# 1,000,000-particle gravity benchmark - Python + NumPy (vectorised)
import sys, time
import numpy as np

W, H = 1500, 800
G, M, MASS, DT = 0.1, 1e8, 2.0, 0.001
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
CX, CY = W / 2, H / 2
BG, FG = 0x141414, 0xFFFFFF

# same xorshift32 sequence as every other language
s = 2463534242
r = np.empty(2 * N)
for i in range(2 * N):
    s ^= (s << 13) & 0xFFFFFFFF; s ^= s >> 17; s ^= (s << 5) & 0xFFFFFFFF
    r[i] = s / 4294967296.0
x = r[0::2] * W
y = r[1::2] * H
px = np.full(N, 500.0)
py = np.full(N, 500.0)
fb = np.empty(W * H, dtype=np.uint32)

def frame():
    global x, y, px, py
    fb.fill(BG)
    dx = x - CX; dy = y - CY
    hyp = np.sqrt(dx * dx + dy * dy)
    m = hyp >= 1
    theta = np.arctan2(CY - y, CX - x)
    force = (G * MASS * M) / np.where(m, hyp, 1.0)
    npx = px + force * np.cos(theta) * DT
    npy = py + force * np.sin(theta) * DT
    px = np.where(m, npx, px); py = np.where(m, npy, py)
    x = np.where(m, x + px / MASS * DT, x)
    y = np.where(m, y + py / MASS * DT, y)
    ix = x.astype(np.int64); iy = y.astype(np.int64)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    fb[iy[ok] * W + ix[ok]] = FG

frames = int(sys.argv[1]) if len(sys.argv) > 1 else 50
frame(); frame(); frame()
t0 = time.perf_counter()
for _ in range(frames):
    frame()
ms = (time.perf_counter() - t0) * 1000 / frames
print(f"numpy frames={frames} ms={ms:.3f} fps={1000/ms:.3f} check={(x.sum()+y.sum())/N:.6f}")
