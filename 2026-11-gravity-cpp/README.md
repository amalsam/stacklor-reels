# Gravity particles, in C++

A straight C++ port of the [2024-02 pygame gravity sim](../2024-02-gravity-particles-pygame/): same physics (`move()` is the same maths as `move_numba()`), same controls.

**Watch:** [Instagram](https://instagram.com/stacklor.dev) · [YouTube](https://youtube.com/@DeveloperAmal)

## Run it

Needs SDL2.

```bash
g++ -O3 -march=native -DUSE_SDL gravity.cpp -o gravity -lSDL2
./gravity
```

## Controls

- Hold left Ctrl to add particles at the cursor.
- `1` spawns a horizontal line, `2` a circular cluster, `3` a vertical line at the cursor.

Without `-DUSE_SDL` it builds headless and writes raw frames to stdout (scripted input), which is how the reel was recorded.
