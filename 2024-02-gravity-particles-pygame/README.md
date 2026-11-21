# Thousands of particles under gravity

A particle simulation in pygame. Every particle is pulled by gravity, and numba compiles the force loop so it stays fast with many particles.

Play the browser version at [labs.stacklor.com/gravity](https://labs.stacklor.com/gravity/). Moved here from the root of [amalsam/Gravity](https://github.com/amalsam/Gravity).

## Run it

```bash
pip install -r requirements.txt
python gravity.py
```

## Controls

- Hold left Ctrl and click to add particles at the cursor.
- `1` spawns a horizontal line of particles at the cursor's height.
- `2` spawns a circular cluster around the cursor.
- `3` spawns a vertical line of particles at the cursor's x position.

## reel-build/

Scripts for the 2026 "run the code" reel of this sim: `run_capture.py` runs `gravity.py` unmodified with scripted input through a headless pygame stand-in (`shim/`), and `compose.py` builds the editor + right-click Run + result video.
