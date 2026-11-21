# Gravity particles in 3D, in C++

The C++ port of [gravity3d.py](../2026-11-gravity-3d/). Same physics, same camera, same controls, but it spawns 1,500 particles a frame instead of 150 and still runs well above 60 FPS with 360,000 particles, using all CPU cores through OpenMP.

**Watch:** [Instagram](https://instagram.com/stacklor.dev) · [YouTube](https://youtube.com/@DeveloperAmal)

## Run it

Needs SDL2 (`sudo apt install libsdl2-dev`, `brew install sdl2`, or MSYS2 `pacman -S mingw-w64-x86_64-SDL2` on Windows).

```bash
g++ -O3 -march=native -fopenmp -DUSE_SDL gravity3d.cpp -o gravity3d -lSDL2
./gravity3d
```

The particle count and FPS are shown in the window title.

## Controls

- Hold `3` to spawn particles at the mouse.
- Drag with the left mouse button to orbit the camera.
- Mouse wheel to zoom.

## How it works

- `move()` is the same maths as the Python version, one particle at a time, and the loop over particles runs on every core (`#pragma omp parallel for`).
- Each particle is projected to the screen and adds light to its pixel, so dense areas glow. `GLOW` sets how much light one particle adds.
- Without `-DUSE_SDL` it builds headless: it reads one line of scripted input per frame and writes raw RGB frames to stdout. That is how the reel was recorded.
