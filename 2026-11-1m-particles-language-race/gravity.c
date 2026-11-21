// 1,000,000-particle gravity benchmark - C
// gcc -O3 -march=native gravity.c -o gravity_c -lm
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define W 1500
#define H 800
static const double G = 0.1, M = 1e8, MASS = 2, DT = 0.001, CX = W / 2.0, CY = H / 2.0;
static uint32_t s = 2463534242u, fb[W * H];
static double rnd(void) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s / 4294967296.0; }
static double now_ms(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e3 + t.tv_nsec / 1e6; }

static int n;
static double *xs, *ys, *pxs, *pys;

static void frame(void) {
    const double k = G * MASS * M;
    for (int i = 0; i < W * H; i++) fb[i] = 0x141414;
    for (int i = 0; i < n; i++) {
        double x = xs[i], y = ys[i];
        double dx = x - CX, dy = y - CY;
        double hyp = sqrt(dx * dx + dy * dy);
        if (hyp >= 1) {
            double theta = atan2(CY - y, CX - x);
            double force = k / hyp;
            double px = pxs[i] + force * cos(theta) * DT;
            double py = pys[i] + force * sin(theta) * DT;
            pxs[i] = px; pys[i] = py;
            x += px / MASS * DT; y += py / MASS * DT;
            xs[i] = x; ys[i] = y;
        }
        int ix = (int)x, iy = (int)y;
        if (ix >= 0 && ix < W && iy >= 0 && iy < H) fb[iy * W + ix] = 0xFFFFFF;
    }
}

int main(int argc, char** argv) {
    int frames = argc > 1 ? atoi(argv[1]) : 100;
    n = argc > 2 ? atoi(argv[2]) : 1000000;
    xs = malloc(n * sizeof(double)); ys = malloc(n * sizeof(double));
    pxs = malloc(n * sizeof(double)); pys = malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) { xs[i] = rnd() * W; ys[i] = rnd() * H; pxs[i] = pys[i] = 500; }
    frame(); frame(); frame();
    double t0 = now_ms();
    for (int f = 0; f < frames; f++) frame();
    double ms = (now_ms() - t0) / frames, sum = 0;
    for (int i = 0; i < n; i++) sum += xs[i] + ys[i];
    printf("c frames=%d ms=%.3f fps=%.3f check=%.6f\n", frames, ms, 1000 / ms, sum / n);
}
