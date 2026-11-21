# Runs the unmodified gravity.py from stacklor-reels with scripted input, capturing every frame.
import sys, runpy, json, os
S = sys.argv[1]; sys.path.insert(0, S + "/shim")
import pygame
SPAWN, TOTAL, MX = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
def script(f):
    keys = {pygame.K_3: 10 <= f < 10 + SPAWN}
    return keys, (MX, 400), f >= TOTAL
pygame.CONTROL.update(script=script, out=sys.argv[2])
try:
    runpy.run_path(S + "/stacklor-reels/2024-02-gravity-particles-pygame/gravity.py", run_name="__main__")
except SystemExit:
    pass
json.dump(pygame.CONTROL["log"], open(sys.argv[2] + ".json", "w"))
print("frames", pygame.CONTROL["frame"])
