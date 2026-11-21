// 1,000,000-particle gravity benchmark - C++
// single thread:  g++ -O3 -march=native gravity.cpp -o gravity_cpp
// 4 threads:      g++ -O3 -march=native -fopenmp gravity.cpp -o gravity_cpp_mt
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#ifdef _OPENMP
#include <omp.h>
#endif

const int W = 1500, H = 800;
const double G = 0.1, M = 1e8, MASS = 2, DT = 0.001, CX = W / 2.0, CY = H / 2.0;
const uint32_t BG = 0x141414, FG = 0xFFFFFF;

int main(int argc, char** argv) {
    int frames = argc > 1 ? atoi(argv[1]) : 100;
    int n = argc > 2 ? atoi(argv[2]) : 1000000;
    uint32_t s = 2463534242u;
    auto rnd = [&] { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s / 4294967296.0; };
    std::vector<double> xs(n), ys(n), pxs(n, 500.0), pys(n, 500.0);
    for (int i = 0; i < n; i++) { xs[i] = rnd() * W; ys[i] = rnd() * H; }
    std::vector<uint32_t> fb(W * H);

    auto frame = [&] {
        const double k = G * MASS * M;
        std::fill(fb.begin(), fb.end(), BG);
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < n; i++) {
            double x = xs[i], y = ys[i];
            double dx = x - CX, dy = y - CY;
            double hyp = std::sqrt(dx * dx + dy * dy);
            if (hyp >= 1) {
                double theta = std::atan2(CY - y, CX - x);
                double force = k / hyp;
                double px = pxs[i] + force * std::cos(theta) * DT;
                double py = pys[i] + force * std::sin(theta) * DT;
                pxs[i] = px; pys[i] = py;
                x += px / MASS * DT; y += py / MASS * DT;
                xs[i] = x; ys[i] = y;
            }
            int ix = (int)x, iy = (int)y;
            if (ix >= 0 && ix < W && iy >= 0 && iy < H) fb[iy * W + ix] = FG;  // same colour from any thread
        }
    };
    frame(); frame(); frame();
    auto t0 = std::chrono::steady_clock::now();
    for (int f = 0; f < frames; f++) frame();
    double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count() / frames;
    double sum = 0; for (int i = 0; i < n; i++) sum += xs[i] + ys[i];
#ifdef _OPENMP
    printf("cpp_mt(%d) frames=%d ms=%.3f fps=%.3f check=%.6f\n", omp_get_max_threads(), frames, ms, 1000 / ms, sum / n);
#else
    printf("cpp frames=%d ms=%.3f fps=%.3f check=%.6f\n", frames, ms, 1000 / ms, sum / n);
#endif
}
