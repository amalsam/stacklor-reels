# Minimal headless stand-in for pygame (PyPI is blocked in this container). Supports exactly the
# calls gravity3d.py makes. Frames stream to ffmpeg; mouse/keyboard input comes from CONTROL["script"].
import numpy as np, subprocess, time as _T
from PIL import Image, ImageDraw, ImageFont
QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, MOUSEWHEEL = 256, 1025, 1026, 1024, 1027
K_3 = 51
CONTROL = {"frame": 0, "script": None, "out": None, "log": [], "proc": None}
_COL = {"white": (255, 255, 255), "yellow": (255, 255, 0)}
def _c(c): return _COL[c] if isinstance(c, str) else tuple(c[:3])
def init(): pass
def quit():
    p = CONTROL["proc"]
    if p: p.stdin.close(); p.wait()
class Surface:
    def __init__(s, w, h): s.w, s.h = w, h; s.a = np.zeros((w, h, 3), np.uint8)   # x-major like pygame
    def fill(s, c): s.a[:] = _c(c)
    def blit(s, surf, rect):
        x, y = rect.x, rect.y; w, h = surf.a.shape[:2]
        reg = s.a[x:x + w, y:y + h]; m = surf.mask[:reg.shape[0], :reg.shape[1], None]
        reg[:] = (reg * (1 - m) + surf.a[:reg.shape[0], :reg.shape[1]] * m).astype(np.uint8)
class _Rect:
    def __init__(s, w, h): s.w, s.h, s.x, s.y = w, h, 0, 0
    @property
    def midtop(s): return (s.x + s.w // 2, s.y)
    @midtop.setter
    def midtop(s, v): s.x = int(v[0] - s.w // 2); s.y = int(v[1])
class _Text:
    def __init__(s, a, m): s.a, s.mask = a, m
    def get_rect(s): return _Rect(*s.a.shape[:2])
class surfarray:
    @staticmethod
    def pixels3d(surf): return surf.a
class display:
    screen = None
    @staticmethod
    def set_mode(size): display.screen = Surface(*size); return display.screen
    @staticmethod
    def set_caption(t): CONTROL["caption"] = t
    @staticmethod
    def flip():
        s = display.screen
        if CONTROL["proc"] is None:
            CONTROL["proc"] = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                "-s", f"{s.w}x{s.h}", "-r", "60", "-i", "-", "-c:v", "libx264", "-crf", "10", "-preset", "veryfast",
                "-pix_fmt", "yuv444p", CONTROL["out"]], stdin=subprocess.PIPE)
        CONTROL["proc"].stdin.write(np.ascontiguousarray(s.a.transpose(1, 0, 2)).tobytes())
        CONTROL["log"].append(dict(CONTROL.get("state", {})))
        CONTROL["frame"] += 1
    update = flip
class font:
    class Font:
        def __init__(s, name, size):
            s.f = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf", size)
        def render(s, text, aa, color):
            l, t, r, b = s.f.getbbox(text); w, h = r + 1, max(b, s.f.size) + 4
            im = Image.new("L", (w, h)); ImageDraw.Draw(im).text((0, 0), text, font=s.f, fill=255)
            m = (np.asarray(im, np.float32) / 255).T
            a = np.zeros((w, h, 3), np.uint8); a[:] = _c(color)
            return _Text(a, m)
class draw:
    @staticmethod
    def circle(surf, color, center, radius):
        x, y = int(center[0]), int(center[1]); W, H = surf.w, surf.h
        x0, x1 = max(0, x - radius), min(W, x + radius + 1); y0, y1 = max(0, y - radius), min(H, y + radius + 1)
        if x0 >= x1 or y0 >= y1: return
        xx, yy = np.ogrid[x0:x1, y0:y1]
        surf.a[x0:x1, y0:y1][(xx - x) ** 2 + (yy - y) ** 2 <= radius * radius] = _c(color)
class _Ev:
    def __init__(s, **k): s.__dict__.update(k)
class event:
    @staticmethod
    def get():
        evs, st = CONTROL["script"](CONTROL["frame"])
        CONTROL["state"] = st
        return [_Ev(**e) for e in evs]
class key:
    @staticmethod
    def get_pressed():
        k = CONTROL.get("state", {}).get("keys", ())
        return {K_3: K_3 in k}
class mouse:
    @staticmethod
    def get_pos(): return tuple(CONTROL.get("state", {}).get("pos", (0, 0)))
class time:
    class Clock:
        def __init__(s): s.last = None; s.d = []
        def tick(s, cap):
            now = _T.perf_counter()
            if s.last is not None: s.d = (s.d + [max(now - s.last, 1 / cap)])[-10:]
            s.last = now
        def get_fps(s): return len(s.d) / sum(s.d) if s.d else 0.0
