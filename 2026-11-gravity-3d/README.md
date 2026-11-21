# Gravity particles in 3D

The [2024-02 gravity sim](../2024-02-gravity-particles-pygame/) taken into three dimensions. Same white particles and yellow sun, same force formula, but every particle now has x, y and z, and you can spin the camera around the whole thing while it runs.

**Watch:** [Instagram](https://instagram.com/stacklor.dev) · [YouTube](https://youtube.com/@DeveloperAmal)
**C++ version:** [2026-11-gravity-3d-cpp](../2026-11-gravity-3d-cpp/) (10x the particles at 60 FPS)

## Run it

```bash
pip install -r requirements.txt
python gravity3d.py
```

## Controls

- Hold `3` to spawn particles at the mouse.
- Drag with the left mouse button to orbit the camera.
- Mouse wheel to zoom.

## How it works

- Gravity is the same as the 2D version: `force = G * MASS * M / distance`, pushed into the momentum every step. In 3D there is no `atan2`/`cos`/`sin`: the direction to the sun is just `-pos / distance`.
- New particles start spinning around the direction you are looking from, so if you rotate the camera between bursts you get orbits in different planes crossing each other.
- The camera is a yaw/pitch rotation plus a perspective divide (`FOV / z`). Closer particles are drawn brighter.
- numpy does every particle at once, so it stays smooth with tens of thousands of particles.
- Tweak `SPEED` (low = particles dive into the sun and get flung out, high = wide orbits), `FOV`, and `n` in `generate_cloud`.
