# Composes the 1M-particle language race reel (1080x1920, 30 fps).
# Timing and numbers come from score.json (exported from the animation's score.js), the explainer
# section (5-14 s) is the animation-studio render, everything else is drawn here from real sim frames.
#   python3 compose.py OUT.mp4 [t0 t1]
import json, subprocess, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = "/home/user/build/compose/"
SIM = "/home/user/build/sim/"
EXPL = "/home/user/build/race-explainer/out/video.mp4"
MUSIC = "/home/user/build/race-explainer/out/final-mix.wav"
SC = json.load(open(HERE + "score.json"))
EV = SC["ev"]
W, H, FPS = 1080, 1920, 30
DUR = SC["DURATION"]
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1 = 60, 940, 230, 1460

BG = (11, 12, 16)
WHITE = (244, 246, 251)
GRAY = (154, 163, 184)
YEL = (255, 210, 63)
PINK = (255, 92, 138)
CYAN = (76, 224, 255)
GREEN = (91, 234, 140)

_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(HERE + {"b": "Bungee-Regular.ttf", "i8": "Inter-800.ttf", "i7": "Inter-700.ttf", "i4": "Inter-400.ttf"}[name], size)
    return _fc[k]

def hexc(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def out_back(x, s=1.9):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def pop(t, t0, d=0.22): return out_back((t - t0) / d) if t >= t0 else 0.0
def fade(t, t0, t1, d=0.2): return clamp((t - t0) / d) * clamp((t1 - t) / d)

# ---------- sim frames ----------
lane_raw = np.fromfile(SIM + "lane.raw", dtype=np.uint8).reshape(-1, 200, 375)
mt_raw = np.fromfile(SIM + "mt.raw", dtype=np.uint8).reshape(-1, 400, 750)
SIM0 = 120  # spotlights start the sim here, where the shape is forming
hook_raw = np.memmap(SIM + "hook.raw", dtype=np.uint8, mode="r").reshape(-1, 800, 1500)

def lut(color, bg=BG, knee=0.55, gain=1.0):
    c = np.array(color, float); b = np.array(bg, float); wv = np.array([255, 255, 255], float)
    x = np.clip(np.linspace(0, 1, 256)[:, None] * gain, 0, 1)
    lo = b + (c - b) * np.clip(x / knee, 0, 1)
    hi = c + (wv - c) * np.clip((x - knee) / (1 - knee), 0, 1) ** 1.6
    return np.where(x < knee, lo, hi).astype(np.uint8)

FIRE = lut((255, 110, 30), knee=0.8, gain=0.85)
_luts = {}
def colorize(gray, color):
    if color not in _luts: _luts[color] = lut(color, knee=0.8, gain=0.85)
    return Image.fromarray(_luts[color][gray])

def glow(img, r=6, k=0.8):
    b = img.filter(ImageFilter.GaussianBlur(r))
    a = np.asarray(img, np.int16) + (np.asarray(b, np.int16) * k).astype(np.int16)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def mass(d, cx, cy, r):
    for rr, a in ((r * 3, 40), (r * 2, 80)):
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(255, 210, 63, a))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=YEL + (255,))

# ---------- text helpers ----------
def text(d, s, x, y, font, fill, anchor="mm", stroke=0, sfill=(0, 0, 0)):
    d.text((x, y), s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=sfill)

def text_pop(im, s, x, y, font, fill, t, t0, t1=1e9, anchor="mm", stroke=6):
    """text that pops in (scale overshoot) and fades out"""
    a = fade(t, t0, t1, 0.12)
    if a <= 0: return
    p = pop(t, t0)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    size = max(4, int(font.size * (0.6 + 0.4 * p)))
    f2 = font.font_variant(size=size)
    text(d, s, x, y, f2, fill + (int(255 * a),), anchor, stroke, (0, 0, 0, int(255 * a)))
    im.alpha_composite(lay)

def box(d, xy, fill, r=18, outline=None, w=4):
    d.rounded_rectangle(xy, r, fill=fill, outline=outline, width=w)

# ---------- explainer frames (decoded once) ----------
def load_explainer():
    t0, t1 = EV["explain"], EV["go"]
    n = int(round((t1 - t0) * FPS))
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", f"{t0}", "-i", EXPL, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)

# ---------- sections ----------
def hook_bg(i, dim=1.0):
    """portrait crop of the full-res 1M particle frame"""
    g = np.asarray(hook_raw[min(i, hook_raw.shape[0] - 1)])[:, 330:1170]  # 840 x 800
    img = Image.fromarray(FIRE[g]).resize((1080, 1029), Image.BILINEAR)
    img = glow(img, 10, 0.45)
    if dim != 1.0: img = Image.fromarray((np.asarray(img) * dim).astype(np.uint8))
    im = Image.new("RGBA", (W, H), BG + (255,))
    im.paste(img, (0, 446))
    d = ImageDraw.Draw(im, "RGBA")
    mass(d, 540, 446 + 1029 // 2, 13)
    return im

def sec_hook(t):
    i = int(t * FPS)
    im = hook_bg(i)
    d = ImageDraw.Draw(im, "RGBA")
    # the old sim HUD, so it reads as the real program running
    text(d, "particles : 1000000", 80, 470, F("i7", 34), (230, 230, 230), "lm")
    if False:
        pass
    text_pop(im, "9 LANGUAGES", 540, 290, F("b", 84), WHITE, t, 0.0, EV["explain"])
    text_pop(im, "1,000,000 PARTICLES", 540, 385, F("b", 78), YEL, t, 0.25, EV["explain"])
    if t >= EV["hook2"]:
        a = fade(t, EV["hook2"], EV["explain"], 0.1); p = pop(t, EV["hook2"])
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        w2, h2 = 440 * p + 10, 62 * p + 5
        box(dl, [540 - w2, 1330 - h2, 540 + w2, 1330 + h2], PINK + (int(235 * a),), 20)
        text(dl, "#1 IS NOT WHO YOU THINK", 540, 1332, F("b", max(4, int(56 * p))), (255, 255, 255, int(255 * a)))
        im.alpha_composite(lay)
    return im


RES = {r["id"]: r for r in SC["RESULTS"]}
RES["cppmt"] = SC["MT"]
CODE = {
    "python": "theta = math.atan2(CY - y, CX - x)",
    "numpy": "theta = np.arctan2(CY - y, CX - x)",
    "js": "const theta = Math.atan2(CY - y, CX - x);",
    "java": "double theta = Math.atan2(CY - y, CX - x);",
    "rust": "let theta = (CY - y).atan2(CX - x);",
    "go": "theta := math.Atan2(CY-y, CX-x)",
    "cpp": "double theta = std::atan2(CY - y, CX - x);",
    "c": "double theta = atan2(CY - y, CX - x);",
    "cppmt": "#pragma omp parallel for",
}
MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 30)

def wrap(d, s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        nxt = (cur + " " + w_).strip()
        if d.textlength(nxt, font) <= maxw: cur = nxt
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def caption(im, t):
    v = next((v for v in SC["vo"] if v["at"] <= t < v["end"]), None)
    if v is None or v["id"] in ("hook", "cta"): return
    a = fade(t, v["at"], v["end"], 0.12)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = F("i8", 38)
    lines = wrap(d, v["cap"], f, 840)
    y0 = 1440 - len(lines) * 50
    wmax = max(d.textlength(l, f) for l in lines)
    box(d, [540 - wmax / 2 - 22, y0 - 14, 540 + wmax / 2 + 22, y0 + len(lines) * 50 + 6], (0, 0, 0, int(170 * a)), 14)
    for i, l in enumerate(lines):
        text(d, l, 540, y0 + 22 + i * 50, f, (255, 255, 255, int(255 * a)))
    im.alpha_composite(lay)

def ladder(im, t, y0=1118, show_mt=False):
    """the growing results ladder; places not revealed yet stay as ???"""
    d = ImageDraw.Draw(im, "RGBA")
    rows = list(SC["order"])
    if show_mt: rows = [SC["MT"]] + rows
    rh = 25 if show_mt else 27
    x0, x1 = 300, 900
    sc = lambda v: x0 + (x1 - x0) * v / 95
    revealed = {r["id"]: r["land"] for r in EV["ranks"]}
    for i, r in enumerate(rows):
        y = y0 + i * rh
        lab = "x4" if r["id"] == "cppmt" else f"#{r['place']}"
        land = revealed.get(r["id"], EV["mtLand"] if r["id"] == "cppmt" else 1e9)
        if t < land:
            text(d, f"{lab}  ???", 90, y, F("i8", 22), (90, 98, 120), "lm")
            box(d, [x0, y - 8, x1, y + 8], (24, 28, 38, 255), 8)
            continue
        col = hexc(r["color"])
        p = clamp((t - land) / 0.4)
        text(d, f"{lab}  {r['name']}", 90, y, F("i8", 22), WHITE, "lm")
        box(d, [x0, y - 8, x0 + max(10, (sc(r["fps"]) - x0) * p), y + 8], col + (255,), 8)
        text(d, f"{r['fps']:.1f}", min(x0 + (sc(r["fps"]) - x0) * p + 10, 860), y, F("i8", 20), WHITE, "lm")
    d.line([sc(60), y0 - 22, sc(60), y0 + len(rows) * rh - 12], fill=(255, 255, 255, 170), width=2)
    text(d, "60 FPS", sc(60), y0 - 26, F("i8", 18), WHITE, "mb")

def spotlight(im, t, rid, t0, land, place_label):
    r = RES[rid]; col = hexc(r["color"]); tau = t - t0
    d = ImageDraw.Draw(im, "RGBA")
    p = pop(t, t0, 0.3)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    fb = F("b", max(4, int(110 * (0.6 + 0.4 * p))))
    text(dl, place_label, 90, 300, fb, col + (255,), "lm")
    nx = 90 + dl.textlength(place_label, fb) + 28
    text(dl, "C++  4 CORES" if rid == "cppmt" else r["name"], nx, 300, F("b", max(4, int(80 * (0.6 + 0.4 * p)))), WHITE + (255,), "lm")
    im.alpha_composite(lay)
    text(d, r["sub"] + ("" if rid == "cppmt" else "  ·  1 core"), 92, 372, F("i7", 30), GRAY, "lm")
    # the sim, at this language's measured speed
    k = min(SC["GOAL"], int(max(0, tau) * r["fps"]))
    g = mt_raw[min(len(mt_raw) - 1, SIM0 + k)][:, 125:625]
    panel = glow(colorize(g, col).resize((900, 480), Image.BILINEAR), 5, 0.5)
    im.paste(panel, (90, 410))
    d.rectangle([90, 410, 990, 890], outline=col + (255,), width=3)
    mass(d, 540, 650, 8)
    text(d, f"frame {k}/150", 970, 870, F("i8", 26), WHITE, "rs")
    # FPS lands on the bell
    v = r["fps"] * clamp((t - (land - 1.0)) / 1.0) ** 0.6
    if t >= land - 1.0:
        s = 1 + 0.25 * math.exp(-(t - land) * 9) if t >= land else 1
        text(d, f"{v:.1f}", 90, 975, F("b", int(104 * s)), (YEL if t >= land else WHITE), "lm")
        fx_ = 90 + d.textlength(f"{v:.1f}", F("b", int(104 * s))) + 18
        text(d, "FPS", fx_, 990, F("b", 48), GRAY, "lm")
        if t >= land:
            text(d, f"{r['ms']:.1f} ms / frame", 990, 960, F("i8", 30), GRAY, "rm")
            py = RES["python"]["fps"]
            if rid != "python": text(d, f"{r['fps'] / py:.1f}x Python", 990, 1000, F("i8", 30), col, "rm")
    else:
        text(d, "measuring...", 90, 975, F("b", 60), (90, 98, 120), "lm")
    box(d, [90, 1035, 990, 1063 + 0], (22, 26, 37, 255), 8)
    text(d, CODE[rid], 104, 1049, MONO, (200, 210, 230), "lm")

def sec_rank(t):
    im = Image.new("RGBA", (W, H), BG + (255,))
    r = [x for x in EV["ranks"] if x["t"] <= t][-1]
    spotlight(im, t, r["id"], r["t"], r["land"], f"#{r['place']}")
    ladder(im, t)
    return im

def sec_twist(t):
    im = Image.new("RGBA", (W, H), BG + (255,))
    text_pop(im, "NOBODY HIT", 540, 520, F("b", 100), WHITE, t, EV["twist"])
    text_pop(im, "60 FPS.", 540, 650, F("b", 140), PINK, t, EV["twist"] + 0.15)
    text_pop(im, "so C++ gets all 4 cores", 540, 820, F("i8", 56), CYAN, t, EV["twist"] + 1.8)
    ladder(im, t)
    return im

def sec_mt(t):
    im = Image.new("RGBA", (W, H), BG + (255,))
    spotlight(im, t, "cppmt", EV["mtGo"], EV["mtLand"], "x4")
    
    ladder(im, t, 1112, True)
    if t >= EV["mtFinish"]:
        text_pop(im, f"150 frames in {SC['MT']['finish']:.2f}s", 540, 650, F("b", 62), WHITE, t, EV["mtFinish"], stroke=4)
    return im
SPECS = [
    ("CPU", "Intel Xeon @ 2.30 GHz (cloud VM)"),
    ("Cores", "4 cores, 4 threads"),
    ("RAM", "15 GB"),
    ("OS", "Ubuntu 24.04.5 LTS"),
    ("Python", "3.13.18 · NumPy 2.5.3"),
    ("Node", "22.23.5"),
    ("Java", "OpenJDK 21.0.13"),
    ("Go", "1.24.7"),
    ("Rust", "rustc 1.97.0, -C opt-level=3"),
    ("C / C++", "gcc / g++ 13.3, -O3 -march=native"),
]
def sec_specs(t):
    im = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    text_pop(im, "THE TEST MACHINE", 540, 300, F("b", 66), YEL, t, EV["specs"])
    box(d, [60, 380, 940, 1200], (22, 26, 37, 255), 26, (60, 68, 90, 255), 3)
    for i, (k, v) in enumerate(SPECS):
        y = 432 + i * 76
        a = int(255 * clamp((t - EV["specs"] - 0.1 - i * 0.07) / 0.2))
        if a <= 0: continue
        text(d, k, 100, y, F("i8", 34), CYAN + (a,), "lm")
        text(d, v, 300, y, F("i7", 32), WHITE + (a,), "lm")
    text(d, "same algorithm, same seed, checksums match", 540, 1240, F("i7", 30), GRAY)
    text(d, "code: github.com/amalsam/stacklor-reels", 540, 1280, F("i7", 30), GRAY)
    return im

def sec_cta(t):
    i = int((t - EV["cta"]) * FPS) + 150
    im = hook_bg(i, 0.55)
    text_pop(im, "WHICH LANGUAGE", 540, 290, F("b", 76), WHITE, t, EV["cta"])
    text_pop(im, "IS NEXT?", 540, 385, F("b", 76), YEL, t, EV["cta"] + 0.15)
    text_pop(im, "I'll run it on", 540, 1150, F("i8", 52), WHITE, t, EV["cta"] + 0.6)
    text_pop(im, "1,000,000 PARTICLES", 540, 1230, F("b", 66), PINK, t, EV["cta"] + 0.8)
    return im

def frame(t, expl):
    if t < EV["explain"]: im = sec_hook(t)
    elif t < EV["go"]:
        im = Image.fromarray(expl[min(len(expl) - 1, int(round((t - EV["explain"]) * FPS)))]).convert("RGBA")
    elif t < EV["twist"]: im = sec_rank(t)
    elif t < EV["mtGo"]: im = sec_twist(t)
    elif t < EV["specs"]: im = sec_mt(t)
    elif t < EV["cta"]: im = sec_specs(t)
    else: im = sec_cta(t)
    caption(im, t)
    return np.asarray(im.convert("RGB"))

def main():
    out = sys.argv[1]
    t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    t1 = float(sys.argv[3]) if len(sys.argv) > 3 else DUR
    if out.endswith(".png"):
        expl = load_explainer() if EV["explain"] <= t0 < EV["go"] else None
        Image.fromarray(frame(t0, expl)).save(out); return
    expl = load_explainer()
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-ss", str(t0), "-t", str(t1 - t0), "-i", MUSIC, "-map", "0:v", "-map", "1:a",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                           "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    n0, n1 = int(round(t0 * FPS)), int(round(t1 * FPS))
    for n in range(n0, n1):
        ff.stdin.write(frame(n / FPS, expl).tobytes())
        if n % 60 == 0: print(f"{n / FPS:.1f}s", flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main()
