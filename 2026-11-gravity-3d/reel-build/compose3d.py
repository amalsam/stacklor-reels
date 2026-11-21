# Builds the vertical 3D reel: VS Code-style editor -> right-click > Run Python File -> captured gravity3d.py run.
# usage: python compose3d.py <gravity3d.py> <sim.mp4 (from run_capture3d.py)> <work dir> <out.mp4>
import sys, json, subprocess, wave, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pygments.lexers import PythonLexer
from pygments.token import Token

SRC, SIM, S, OUT = sys.argv[1:5]
W, H, FPS = 1080, 1920, 30

MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
UI = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
UIM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
fcode = ImageFont.truetype(MONO, 28)
fgut = ImageFont.truetype(MONO, 26)
fui = ImageFont.truetype(UI, 24)
fuis = ImageFont.truetype(UI, 21)
fuim = ImageFont.truetype(UIM, 24)
fterm = ImageFont.truetype(MONO, 24)

BG = (30, 30, 30); FG = (212, 212, 212)
# ---------- layout ----------
TITLE_H, TAB_H, CRUMB_H, STATUS_H = 54, 60, 40, 40
ED_TOP = TITLE_H + TAB_H + CRUMB_H
ED_BOT = H - STATUS_H
LH = 42
GUT = 96

# ---------- syntax highlight (Dark+) ----------
code = open(SRC).read().splitlines()
def color(tt, val, prev):
    if tt in Token.Comment: return (106, 153, 85)
    if tt in Token.Literal.String: return (206, 145, 120)
    if tt in Token.Literal.Number: return (181, 206, 168)
    if tt in Token.Name.Decorator: return (220, 220, 170)
    if tt in Token.Keyword.Namespace: return (197, 134, 192)
    if tt in Token.Keyword:
        if val in ("if", "else", "elif", "return", "for", "while", "in", "import", "from", "try", "except"): return (197, 134, 192)
        return (86, 156, 214)
    if tt in Token.Operator.Word: return (86, 156, 214)
    if tt in Token.Name.Function: return (220, 220, 170)
    if tt in Token.Name.Class: return (78, 201, 176)
    if tt in Token.Name.Builtin.Pseudo: return (86, 156, 214)
    if tt in Token.Name.Builtin: return (220, 220, 170)
    if tt in Token.Name: return (156, 220, 254)
    return FG
lex = PythonLexer()
codeimg = Image.new("RGB", (2400, LH * (len(code) + 60)), BG)
d = ImageDraw.Draw(codeimg)
y = 0; x = 0
toks = list(lex.get_tokens(open(SRC).read()))
prev = None
CW = fcode.getlength("M")
for i, (tt, val) in enumerate(toks):
    nxt = toks[i + 1][1] if i + 1 < len(toks) else ""
    parts = val.split("\n")
    for k, p in enumerate(parts):
        if k > 0: y += LH; x = 0
        if p:
            c = color(tt, p, prev)
            if tt in Token.Name and not (tt in Token.Name.Function or tt in Token.Name.Class) and nxt.startswith("("):
                c = (220, 220, 170)
            if tt in Token.Name and p.isupper() and len(p) > 1: c = (79, 193, 255)
            d.text((x, y + 6), p, font=fcode, fill=c)
            x += CW * len(p)
    if val.strip(): prev = val

def editor_frame(scroll_px, cur_line):
    im = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(im)
    # title bar
    dr.rectangle([0, 0, W, TITLE_H], fill=(24, 24, 24))
    for k, cx in enumerate([22, 52, 82]): pass
    t = "gravity3d.py - stacklor-reels - Visual Studio Code"
    dr.text((W / 2, TITLE_H / 2), t, font=fuis, fill=(204, 204, 204), anchor="mm")
    cy = TITLE_H // 2
    dr.line([W - 150, cy, W - 132, cy], fill=(204, 204, 204), width=2)
    dr.rectangle([W - 100, cy - 8, W - 84, cy + 8], outline=(204, 204, 204), width=2)
    dr.line([W - 50, cy - 8, W - 34, cy + 8], fill=(204, 204, 204), width=2)
    dr.line([W - 50, cy + 8, W - 34, cy - 8], fill=(204, 204, 204), width=2)
    # tabs
    dr.rectangle([0, TITLE_H, W, TITLE_H + TAB_H], fill=(24, 24, 24))
    dr.rectangle([0, TITLE_H, 290, TITLE_H + TAB_H], fill=BG)
    dr.line([0, TITLE_H, 290, TITLE_H], fill=(0, 120, 212), width=3)
    dr.text((22, TITLE_H + TAB_H / 2), "py", font=fuim, fill=(255, 202, 40), anchor="lm")
    dr.text((60, TITLE_H + TAB_H / 2), "gravity3d.py", font=fui, fill=(255, 255, 255), anchor="lm")
    dr.text((262, TITLE_H + TAB_H / 2), "✕", font=fuis, fill=(180, 180, 180), anchor="mm")
    dr.text((322, TITLE_H + TAB_H / 2), "README.md", font=fui, fill=(150, 150, 150), anchor="lm")
    # breadcrumbs
    dr.text((24, TITLE_H + TAB_H + CRUMB_H / 2), "gravity-3d  ›  gravity3d.py  ›  ƒ draw",
            font=fuis, fill=(170, 170, 170), anchor="lm")
    # code
    view_h = ED_BOT - ED_TOP
    top = int(scroll_px)
    crop = codeimg.crop((0, top, W - GUT - 20, top + view_h))
    first = top // LH
    off = top - first * LH
    hl_y = ED_TOP + (cur_line - 1) * LH - top
    if ED_TOP <= hl_y < ED_BOT:
        dr.rectangle([0, hl_y, W, hl_y + LH - 1], outline=(40, 40, 40), width=2)
    im.paste(crop, (GUT + 10, ED_TOP))
    for n in range(first, first + view_h // LH + 2):
        yy = ED_TOP + n * LH - top
        if yy < ED_TOP - LH or n >= len(code): continue
        col = (198, 198, 198) if n + 1 == cur_line else (110, 118, 129)
        dr.text((GUT - 16, yy + 7), str(n + 1), font=fgut, fill=col, anchor="ra")
    # keep gutter/header clean where text overlapped
    dr.rectangle([0, 0, W, 0], fill=(24, 24, 24))
    # minimap-ish scrollbar
    total = len(code) * LH
    sb_h = max(60, view_h * view_h / total)
    sb_y = ED_TOP + (view_h - sb_h) * (scroll_px / max(1, total - view_h))
    dr.rectangle([W - 14, sb_y, W - 2, sb_y + sb_h], fill=(70, 70, 70))
    # status bar
    dr.rectangle([0, ED_BOT, W, H], fill=(0, 122, 204))
    dr.text((20, ED_BOT + STATUS_H / 2), "⎇ main   ⊗ 0  ⚠ 0", font=fuis, fill=(255, 255, 255), anchor="lm")
    dr.text((W - 20, ED_BOT + STATUS_H / 2), f"Ln {cur_line}, Col 9   Spaces: 4   UTF-8   Python 3.12", font=fuis, fill=(255, 255, 255), anchor="rm")
    return im

# ---------- context menu ----------
MENU = [("Go to Definition", "F12"), ("Go to References", "Shift+F12"), ("Peek", "›"), None,
        ("Find All References", "Shift+Alt+F12"), ("Show Call Hierarchy", "Shift+Alt+H"), None,
        ("Rename Symbol", "F2"), ("Change All Occurrences", "Ctrl+F2"), ("Format Document", "Shift+Alt+F"),
        ("Refactor...", "Ctrl+Shift+R"), ("Source Action...", ""), None,
        ("Cut", "Ctrl+X"), ("Copy", "Ctrl+C"), ("Paste", "Ctrl+V"), None,
        ("Run Python", "›"), None, ("Command Palette...", "Ctrl+Shift+P")]
SUB = [("Run Python File in Terminal", ""), ("Run Selection/Line in Python Terminal", "")]
IH, SEPH, MW, SW = 46, 15, 430, 500
def menu_layout(x0, y0, items, w):
    rows = []; y = y0 + 8
    for it in items:
        if it is None: rows.append((None, y, y + SEPH)); y += SEPH
        else: rows.append((it, y, y + IH)); y += IH
    return rows, (x0, y0, x0 + w, y + 8)
def draw_menu(im, x0, y0, items, w, hover, alpha=1.0):
    rows, box = menu_layout(x0, y0, items, w)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0] + 4, box[1] + 10, box[2] + 10, box[3] + 16], 10, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(12))
    dr = ImageDraw.Draw(layer)
    dr.rounded_rectangle(box, 8, fill=(37, 37, 38, 255), outline=(69, 69, 69, 255), width=1)
    for it, a, b in rows:
        if it is None:
            dr.line([box[0] + 12, (a + b) // 2, box[2] - 12, (a + b) // 2], fill=(80, 80, 80, 255)); continue
        hov = it[0] == hover
        if hov: dr.rounded_rectangle([box[0] + 6, a, box[2] - 6, b], 5, fill=(4, 57, 94, 255))
        fill = (255, 255, 255, 255) if hov else (204, 204, 204, 255)
        dr.text((box[0] + 30, (a + b) / 2), it[0], font=fui, fill=fill, anchor="lm")
        if it[1]:
            dr.text((box[2] - 24, (a + b) / 2), it[1], font=fuis if it[1] != "›" else fuim, fill=fill, anchor="rm")
    comb = Image.alpha_composite(sh, layer)
    if alpha < 1:
        comb.putalpha(comb.getchannel("A").point(lambda v: int(v * alpha)))
    im.paste(comb, (0, 0), comb)
    return rows, box

# ---------- cursor ----------
def draw_cursor(im, x, y, s=1.7, press=0.0):
    pts = [(0, 0), (0, 25), (6, 19), (10, 29), (14, 27), (10, 18), (18, 18)]
    sc = s * (1 - 0.12 * press)
    P = [(x + px * sc, y + py * sc) for px, py in pts]
    dr = ImageDraw.Draw(im)
    dr.polygon([(px + 2, py + 3) for px, py in P], fill=(0, 0, 0))
    dr.polygon(P, fill=(255, 255, 255), outline=(0, 0, 0), width=2)
def ripple(im, x, y, t):
    if not (0 <= t < 0.45): return
    r = 12 + 70 * (t / 0.45); a = int(200 * (1 - t / 0.45))
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, a), width=4)
    im.paste(lay, (0, 0), lay)

def ease(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def path(p0, p1, t):
    e = ease(t)
    # slight arc
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 60
    return ((1 - e) ** 2 * p0[0] + 2 * (1 - e) * e * mx + e * e * p1[0],
            (1 - e) ** 2 * p0[1] + 2 * (1 - e) * e * my + e * e * p1[1])

# ---------- timeline ----------
T_SCROLL0, T_SCROLL1 = 0.3, 2.6
SCROLL_END = 55 * LH
T_RCLICK = 3.6
T_HOVER_RUN = 4.5
T_SUB = 4.7
T_LCLICK = 5.6
T_TERM = 5.8
T_WIN = 6.7
T_ZOOM0, T_ZOOM1 = 8.0, 8.9
TARGET_LINE = 81
CLICK_PT = (70, ED_TOP + (TARGET_LINE - 1) * LH - SCROLL_END + LH // 2)
MENU_X, MENU_Y = CLICK_PT[0] + 4, CLICK_PT[1] - 520
menu_rows, menu_box = menu_layout(MENU_X, MENU_Y, MENU, MW)
run_row = [r for r in menu_rows if r[0] and r[0][0] == "Run Python"][0]
RUN_PT = (MENU_X + 150, (run_row[1] + run_row[2]) / 2)
SUB_X, SUB_Y = menu_box[2] - 4 - (menu_box[2] + SW - 4 - (W - 20)) - 0, run_row[1] - 8
SUB_X = menu_box[2] - 4
sub_rows, sub_box = menu_layout(SUB_X, SUB_Y, SUB, SW)
RUNF_PT = (SUB_X + 200, (sub_rows[0][1] + sub_rows[0][2]) / 2)
START_PT = (900, 1650)

# sim
log = json.load(open(SIM + ".json"))
simproc = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SIM, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
SW_, SH_ = 1500, 800
CROP_X, CROP_W = 400, 700   # middle of the 1500x800 window, scaled up to fill the reel width
nsim = len(log)
sim_frames_needed = nsim // 2
DUR = T_WIN + sim_frames_needed / FPS
NF = int(DUR * FPS)
sim_cache = {"idx": -1, "img": None}
def sim_frame(k):
    k = min(k, nsim - 1)
    while sim_cache["idx"] < k:
        buf = simproc.stdout.read(SW_ * SH_ * 3)
        if len(buf) < SW_ * SH_ * 3: break
        sim_cache["idx"] += 1
        sim_cache["img"] = Image.frombytes("RGB", (SW_, SH_), buf)
    return sim_cache["img"]

TERM_TOP = 1260
def draw_terminal(im, t):
    e = ease((t - T_TERM) / 0.35)
    if e <= 0: return
    top = int(lerp(ED_BOT, TERM_TOP, e))
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, top, W, ED_BOT], fill=(24, 24, 24))
    dr.line([0, top, W, top], fill=(60, 60, 60), width=2)
    x = 24
    for name in ["PROBLEMS", "OUTPUT", "DEBUG CONSOLE", "TERMINAL", "PORTS"]:
        c = (231, 231, 231) if name == "TERMINAL" else (150, 150, 150)
        dr.text((x, top + 30), name, font=fuis, fill=c, anchor="lm")
        wdt = fuis.getlength(name)
        if name == "TERMINAL": dr.line([x, top + 50, x + wdt, top + 50], fill=(0, 120, 212), width=3)
        x += wdt + 30
    lines = ["PS D:\\stacklor-reels\\gravity-3d>", "& python gravity3d.py"]
    if t > T_TERM + 0.35:
        for i, ln in enumerate(lines):
            dr.text((24, top + 80 + i * 36), ln, font=fterm, fill=(204, 204, 204))
        if int(t * 2.5) % 2 == 0 or t < T_WIN:
            cx = 24 + fterm.getlength(lines[1])
            dr.rectangle([24, top + 80 + 2 * 36, 38, top + 80 + 2 * 36 + 28], fill=(204, 204, 204))

# audio clicks
clicks = []  # times of press
# write audio first
SR = 48000
aud = np.zeros(int((DUR + 1) * SR), np.float32)
rng = np.random.default_rng(7)
def click(t, amp=0.8, bright=1.0):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    noise = rng.standard_normal(n) * np.exp(-tt / 0.0018)
    tone = np.sin(2 * np.pi * 3100 * bright * tt) * np.exp(-tt / 0.004) * 0.6
    body = np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.006) * 0.5
    s = (noise * 0.7 + tone + body)
    s = np.convolve(s, [0.5, 0.5], mode="same")
    i = int(t * SR); aud[i:i + n] += amp * s / np.abs(s).max()
for tp in (T_RCLICK, T_LCLICK):
    click(tp, 0.85, 1.0); click(tp + 0.085, 0.55, 1.25)
# in the running sim: a click on every mouse press / release, a soft tick on every wheel notch
for i in range(1, nsim):
    ts = T_WIN + i / (FPS * 2)
    if log[i]["drag"] != log[i - 1]["drag"]:
        click(ts, 0.75 if log[i]["drag"] else 0.5, 1.0 if log[i]["drag"] else 1.25)
    if log[i]["wheel"]:
        click(ts, 0.3, 1.6)
with wave.open(S + "/clicks.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    a16 = (np.clip(aud, -1, 1) * 32000).astype(np.int16)
    wf.writeframes(np.repeat(a16[:, None], 2, axis=1).tobytes())

frames_out = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-i", S + "/clicks.wav",
                               "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                               "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT],
                              stdin=subprocess.PIPE)

for f in range(NF):
    t = f / FPS
    # editor state
    scroll = lerp(0, SCROLL_END, ease((t - T_SCROLL0) / (T_SCROLL1 - T_SCROLL0)))
    cur_line = 1 if t < T_RCLICK else TARGET_LINE
    if t < T_ZOOM1:
        im = editor_frame(scroll, cur_line)
        draw_terminal(im, t)
        # cursor position
        if t < T_RCLICK:
            pos = path(START_PT, CLICK_PT, (t - 1.6) / (T_RCLICK - 0.15 - 1.6))
        elif t < T_HOVER_RUN:
            pos = path(CLICK_PT, RUN_PT, (t - T_RCLICK - 0.2) / (T_HOVER_RUN - T_RCLICK - 0.2))
        elif t < T_LCLICK:
            pos = path(RUN_PT, RUNF_PT, (t - T_SUB - 0.05) / (T_LCLICK - 0.15 - T_SUB - 0.05))
        else:
            pos = path(RUNF_PT, (RUNF_PT[0] + 120, RUNF_PT[1] + 260), (t - T_LCLICK - 0.3) / 1.0)
        if T_RCLICK <= t < T_LCLICK + 0.12:
            hover = "Run Python" if t >= T_HOVER_RUN - 0.05 else None
            draw_menu(im, MENU_X, MENU_Y, MENU, MW, hover, alpha=ease((t - T_RCLICK) / 0.08))
            if t >= T_SUB:
                h2 = "Run Python File in Terminal" if t >= T_LCLICK - 0.35 else None
                draw_menu(im, SUB_X, SUB_Y, SUB, SW, h2, alpha=ease((t - T_SUB) / 0.08))
        for tc, pt in ((T_RCLICK, CLICK_PT), (T_LCLICK, RUNF_PT)):
            ripple(im, pt[0], pt[1], t - tc)
        press = 1.0 if any(0 <= t - tc < 0.09 for tc in (T_RCLICK, T_LCLICK)) else 0.0
        if t >= T_WIN:
            # pygame window pops up, then zooms to fill the reel
            k = int((t - T_WIN) * FPS) * 2
            simg = sim_frame(k)
            z = ease((t - T_ZOOM0) / (T_ZOOM1 - T_ZOOM0))
            pop = ease((t - T_WIN) / 0.22)
            # window rect A and full-bleed rect B (crop x 300..1200 -> 1080 wide)
            aw = 1040 * (0.88 + 0.12 * pop); ah = aw * SH_ / SW_
            ax, ay = (W - aw) / 2, 700 - ah / 2
            bs = W / CROP_W; bw, bh = SW_ * bs, SH_ * bs; bx, by = -CROP_X * bs, (H - bh) / 2
            rx, ry, rw, rh = lerp(ax, bx, z), lerp(ay, by, z), lerp(aw, bw, z), lerp(ah, bh, z)
            # dim editor toward sim bg
            dimc = Image.new("RGB", (W, H), (20, 20, 20))
            im = Image.blend(im, dimc, 0.35 * pop + 0.65 * z)
            dr = ImageDraw.Draw(im)
            tb = 40 * (1 - z)
            if tb > 1:
                dr.rectangle([rx - 1, ry - tb, rx + rw + 1, ry + rh + 1], fill=(240, 240, 240), outline=(90, 90, 90))
                cap = "gravity 3d"
                dr.text((rx + 14, ry - tb / 2), cap, font=fuis, fill=(20, 20, 20), anchor="lm")
                cy = ry - tb / 2
                for j, sym in enumerate(["min", "max", "x"]):
                    bx0 = rx + rw - 30 - (2 - j) * 40
                    if sym == "min": dr.line([bx0 - 8, cy, bx0 + 8, cy], fill=(20, 20, 20), width=2)
                    elif sym == "max": dr.rectangle([bx0 - 7, cy - 7, bx0 + 7, cy + 7], outline=(20, 20, 20), width=2)
                    else:
                        dr.line([bx0 - 7, cy - 7, bx0 + 7, cy + 7], fill=(20, 20, 20), width=2)
                        dr.line([bx0 - 7, cy + 7, bx0 + 7, cy - 7], fill=(20, 20, 20), width=2)
            im.paste(simg.resize((int(rw), int(rh)), Image.BILINEAR), (int(rx), int(ry)))
        if t < T_ZOOM0: draw_cursor(im, pos[0], pos[1], press=press)
    else:
        k = int((t - T_WIN) * FPS) * 2
        simg = sim_frame(k)
        im = Image.new("RGB", (W, H), (20, 20, 20))
        bs = W / CROP_W; bw, bh = int(SW_ * bs), int(SH_ * bs)
        im.paste(simg.resize((bw, bh), Image.BILINEAR), (int(-CROP_X * bs), (H - bh) // 2))
        # soften the top/bottom edge of the window so zoomed-in particles don't end in a hard line
        arr = np.asarray(im).astype(np.float32); y0 = (H - bh) // 2; FE = 160
        ramp = (np.arange(FE, dtype=np.float32) / FE)[:, None, None]
        arr[y0:y0 + FE] = 20 + (arr[y0:y0 + FE] - 20) * ramp
        arr[y0 + bh - FE:y0 + bh] = 20 + (arr[y0 + bh - FE:y0 + bh] - 20) * ramp[::-1]
        im = Image.fromarray(arr.astype(np.uint8))
        # program's own particle / fps readout, lifted from its frame
        ro = simg.crop((10, 95, 210, 158)).resize((380, 120), Image.LANCZOS)
        a = ease((t - T_ZOOM1) / 0.4)
        ry0 = (H - bh) // 2 + 20
        base = im.crop((40, ry0, 420, ry0 + 120))
        im.paste(Image.blend(base, ro, a), (40, ry0))
        # mouse sits where the program spawns particles while key 3 is held
        st = log[min(k, nsim - 1)]
        mx = (st["pos"][0] - CROP_X) * bs; my = (H - bh) / 2 + st["pos"][1] * bs
        draw_cursor(im, mx, my, press=1.0 if st["drag"] else 0.0)
        if st["drag"]:
            lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
            ImageDraw.Draw(lay).ellipse([mx - 22, my - 22, mx + 22, my + 22], outline=(255, 255, 255, 110), width=3)
            im.paste(lay, (0, 0), lay)
    frames_out.stdin.write(im.tobytes())
frames_out.stdin.close(); frames_out.wait()
print("done", NF, DUR)
