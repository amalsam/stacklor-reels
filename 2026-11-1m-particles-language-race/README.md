# 1,000,000 particles in 9 languages

The gravity sim from [2024-02-gravity-particles-pygame](../2024-02-gravity-particles-pygame/), scaled to one million particles and written nine ways. Every version runs the same maths on the same starting positions, one CPU core each, and the reel races them to 150 frames. Nobody reaches 60 FPS on one core. C++ with OpenMP on all four cores does.

**Watch:** [Instagram](https://instagram.com/stacklor.dev) · [YouTube](https://youtube.com/@DeveloperAmal)

## Results

1,000,000 particles, frames per second, median of 3 runs (after 3 warm-up frames). Higher is better.

| # | Language | Version / flags | ms per frame | FPS | vs Python |
| --- | --- | --- | ---: | ---: | ---: |
| ★ | C++, 4 threads | g++ 13.3 `-O3 -march=native -fopenmp` | 10.9 | **92.1** | 43x |
| 1 | C | gcc 13.3 `-O3 -march=native` | 34.9 | 28.7 | 13x |
| 2 | C++ | g++ 13.3 `-O3 -march=native` | 39.2 | 25.5 | 12x |
| 3 | Go | go 1.24.7 | 42.3 | 23.6 | 11x |
| 4 | Rust | rustc 1.97.0 `-C opt-level=3 -C target-cpu=native` | 45.6 | 21.9 | 10x |
| 5 | Java | OpenJDK 21.0.13 | 49.1 | 20.3 | 9.5x |
| 6 | JavaScript | Node 22.23.5 | 54.6 | 18.3 | 8.6x |
| 7 | Python + NumPy | Python 3.13.18, NumPy 2.5.3 | 60.1 | 16.6 | 7.8x |
| 8 | Python | CPython 3.13.18, no libraries | 467.7 | 2.1 | 1x |

Not in the video: **Bun 1.4.4** runs the same `gravity.js` at 18.6 FPS (53.6 ms), level with Node.
Raw output of every run is in [results/raw.txt](results/raw.txt).

## Test machine

| | |
| --- | --- |
| CPU | Intel Xeon @ 2.30 GHz (KVM cloud VM, AVX-512) |
| Cores | 4 cores, 1 thread per core |
| RAM | 15 GB |
| OS | Ubuntu 24.04.5 LTS, Linux 6.18 |
| Toolchains | see [results/specs.txt](results/specs.txt) |

Your numbers will differ on your machine. The ranking is the interesting part.

## Run it

Needs python3 (+ `pip install -r requirements.txt` for NumPy), node, java, go, rustc, gcc/g++.

```bash
./run_all.sh                # builds everything, prints specs, 3 runs of each on 1,000,000 particles
N=20000 ./run_all.sh        # quick check with fewer particles
```

Or one at a time: `python3 gravity.py 3`, `node gravity.js 50`, `java -cp bin Gravity 50`, `bin/gravity_go 50`, ... (first argument = timed frames, second = particle count).

## How it works

- Every frame, every particle is pulled toward a fixed mass in the middle of a 1500x800 screen: `sqrt` for the distance, `atan2` for the angle, `cos` and `sin` to split the force. That is 4 million maths calls per frame. The particle is then plotted into a framebuffer, like the original pygame version.
- Starting positions come from the same xorshift32 generator in every language, so all nine start identical. Each program prints a checksum (mean of x + y) at the end, and they all match for the same frame count. That is the proof they did the same work.
- Single thread everywhere except the one entry marked x4, which is `gravity.cpp` built with `-fopenmp`: one `#pragma omp parallel for` line.
- No `-ffast-math` and no hand-written SIMD. This is the code you would write first, not the fastest possible code in each language.

Things you can tweak:

- `N` (particle count) and the frame count on the command line.
- `G`, `M`, `DT` at the top of each file change how hard the mass pulls and how fast time runs.
- Try Numba (`@njit`) on the Python version, or `rayon` on the Rust one, and send the numbers.

## Why no Numba?

The original sim used Numba. The machine this was benchmarked on had no access to PyPI, so Numba could not be installed and it is not in the race. NumPy was already installed, so it stands in for "fast Python".
