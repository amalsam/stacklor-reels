# Minimal headless stand-in for pygame (PyPI blocked here). Renders into a numpy buffer
# and streams each display.update() to ffmpeg. Input is scripted via CONTROL.
import numpy as np, time, json, subprocess, os
from PIL import Image, ImageDraw, ImageFont
QUIT = 256; K_LCTRL, K_1, K_2, K_3 = 1, 2, 3, 4
CONTROL = {"frame": 0, "script": lambda f: ({}, (0, 0), False), "out": None, "log": []}
COLORS = {"white": (255,255,255), "yellow": (255,255,0)}
def _c(c): return COLORS[c] if isinstance(c, str) else tuple(c[:3])
def init(): pass
def quit(): 
    p = CONTROL.get("proc")
    if p: p.stdin.close(); p.wait()
class Rect:
    def __init__(s, x, y, w, h): s.x, s.y, s.w, s.h = x, y, w, h
class Surface:
    def __init__(s, w, h): s.w, s.h = w, h; s.a = np.zeros((h, w, 3), np.uint8)
    def fill(s, c): s.a[:] = _c(c)
    def blit(s, surf, rect):
        x, y = rect.x, rect.y; h, w = surf.a.shape[:2]
        m = surf.mask
        reg = s.a[y:y+h, x:x+w]; mm = m[:reg.shape[0], :reg.shape[1], None]
        reg[:] = (reg * (1 - mm) + surf.a[:reg.shape[0], :reg.shape[1]] * mm).astype(np.uint8)
class _TRect:
    def __init__(s, w, h): s.w, s.h, s.x, s.y = w, h, 0, 0
    @property
    def midtop(s): return (s.x + s.w // 2, s.y)
    @midtop.setter
    def midtop(s, v): s.x = v[0] - s.w // 2; s.y = v[1]
class _Text:
    def __init__(s, a, m): s.a, s.mask = a, m
    def get_rect(s): return _TRect(s.a.shape[1], s.a.shape[0])
class _display:
    screen = None
    @staticmethod
    def set_mode(size):
        _display.screen = Surface(*size); return _display.screen
    @staticmethod
    def set_caption(t): CONTROL["caption"] = t
    @staticmethod
    def update():
        scr = _display.screen
        if CONTROL.get("proc") is None:
            CONTROL["proc"] = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24",
                "-s",f"{scr.w}x{scr.h}","-r","60","-i","-","-c:v","libx264","-crf","10","-preset","fast",
                "-pix_fmt","yuv444p",CONTROL["out"]], stdin=subprocess.PIPE)
        CONTROL["proc"].stdin.write(scr.a.tobytes())
        CONTROL["log"].append({"caption": CONTROL.get("caption")})
        CONTROL["frame"] += 1
display = _display
class font:
    class Font:
        def __init__(s, name, size):
            p = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if "freesansbold" in name else name
            s.f = ImageFont.truetype(p, size)
        def render(s, text, aa, color):
            l, t, r, b = s.f.getbbox(text); w, h = r + 1, max(b, s.f.size) + 4
            im = Image.new("L", (w, h)); ImageDraw.Draw(im).text((0, 0), text, font=s.f, fill=255)
            m = np.asarray(im, np.float32) / 255
            a = np.zeros((h, w, 3), np.uint8); a[:] = _c(color)
            return _Text(a, m)
class draw:
    @staticmethod
    def circle(surf, color, center, radius):
        x, y = int(center[0]), int(center[1]); a = surf.a; H, W = a.shape[:2]
        if radius <= 1:
            if 0 < x < W-1 and 0 < y < H-1:
                c = _c(color); a[y, x-1:x+2] = c; a[y-1, x] = c; a[y+1, x] = c
            return
        y0, y1 = max(0, y-radius), min(H, y+radius+1); x0, x1 = max(0, x-radius), min(W, x+radius+1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        a[y0:y1, x0:x1][(xx-x)**2 + (yy-y)**2 <= radius*radius] = _c(color)
class _Ev:
    def __init__(s, t): s.type = t
class event:
    @staticmethod
    def get():
        keys, pos, quit_ = CONTROL["script"](CONTROL["frame"])
        CONTROL["keys"], CONTROL["pos"] = keys, pos
        return [_Ev(QUIT)] if quit_ else []
class key:
    @staticmethod
    def get_pressed():
        k = CONTROL.get("keys", {}); return {K_LCTRL: k.get(K_LCTRL, False), K_1: k.get(K_1, False), K_2: k.get(K_2, False), K_3: k.get(K_3, False)}
class mouse:
    @staticmethod
    def get_pos(): return CONTROL.get("pos", (0, 0))
class time:
    class Clock:
        def __init__(s): s.last = None; s.d = []
        def tick(s, cap):
            import time as T
            now = T.perf_counter()
            if s.last is not None: s.d = (s.d + [max(now - s.last, 1 / cap)])[-10:]
            s.last = now
        def get_fps(s): return len(s.d) / sum(s.d) if s.d else 0.0
