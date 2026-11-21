// Same sim as bench/gravity.cpp, but writes a density image per frame (glow look) for the video.
// usage: dump FRAMES SCALE_DIV > raw (gray8, W/div x H/div per frame)
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
const int W = 1500, H = 800;
const double G = 0.1, M = 1e8, MASS = 2, DT = 0.001, CX = W / 2.0, CY = H / 2.0;
int main(int argc, char** argv) {
    int frames = atoi(argv[1]), div = atoi(argv[2]); int start = argc > 3 ? atoi(argv[3]) : 0; int every = argc>4?atoi(argv[4]):1;
    int n = 1000000; uint32_t s = 2463534242u;
    auto rnd = [&] { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s / 4294967296.0; };
    std::vector<double> xs(n), ys(n), pxs(n, 500.0), pys(n, 500.0);
    for (int i = 0; i < n; i++) { xs[i] = rnd() * W; ys[i] = rnd() * H; }
    int w = W / div, h = H / div;
    std::vector<float> acc(w * h); std::vector<uint8_t> out(w * h);
    const double k = G * MASS * M;
    for (int f = 0; f < frames; f++) {
        std::fill(acc.begin(), acc.end(), 0.f);
        #pragma omp parallel for
        for (int i = 0; i < n; i++) {
            double x = xs[i], y = ys[i], dx = x - CX, dy = y - CY, hyp = std::sqrt(dx * dx + dy * dy);
            if (hyp >= 1) {
                double th = std::atan2(CY - y, CX - x), fo = k / hyp;
                pxs[i] += fo * std::cos(th) * DT; pys[i] += fo * std::sin(th) * DT;
                x += pxs[i] / MASS * DT; y += pys[i] / MASS * DT; xs[i] = x; ys[i] = y;
            }
        }
        if (f < start || (f - start) % every) continue;
        for (int i = 0; i < n; i++) {
            int ix = (int)(xs[i] / div), iy = (int)(ys[i] / div);
            if (xs[i] >= 0 && ix < w && ys[i] >= 0 && iy < h) acc[iy * w + ix] += 1.f;
        }
        float norm = 1.0f / (div * div);
        for (int i = 0; i < w * h; i++) { float v = acc[i] * norm; out[i] = (uint8_t)std::min(255.f, 255.f * (1 - std::exp(-v * 0.9f))); }
        fwrite(out.data(), 1, out.size(), stdout);
    }
}
