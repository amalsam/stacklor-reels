// 3D gravity particles - C++ port of gravity3d.py
// hold 3 : spawn particles at the mouse    drag : orbit camera    wheel : zoom
//
// Window build (needs SDL2): g++ -O3 -march=native -fopenmp -DUSE_SDL gravity3d.cpp -o gravity3d -lSDL2
// Headless build (raw frames, scripted input, used for the reel):
//   g++ -O3 -march=native -fopenmp gravity3d.cpp -o gravity3d
//   ./gravity3d input.txt 2> stats.txt | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1500x800 -r 60 -i - out.mp4
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <random>
#include <vector>
#ifdef USE_SDL
#include <SDL2/SDL.h>
#endif

const int W = 1500, H = 800;
const double G = 0.1, M = 1e8, MASS = 2.0, DT = 0.001;
const double SPEED = 2200;     // starting momentum of new particles
const double FOV = 900;        // camera focal length in pixels
const int SPAWN = 1500;        // particles per frame while 3 is held (10x the Python version)
const int BG = 20;
const float GLOW = 80;         // light added per particle (10x the particles, so each one is dimmer)

struct Vec { double x, y, z; };
Vec operator+(Vec a, Vec b) { return {a.x + b.x, a.y + b.y, a.z + b.z}; }
Vec operator*(Vec a, double s) { return {a.x * s, a.y * s, a.z * s}; }
Vec cross(Vec a, Vec b) { return {a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x}; }
double len(Vec a) { return std::sqrt(a.x * a.x + a.y * a.y + a.z * a.z); }

struct Particle { Vec pos, mom; };
std::vector<Particle> particles;
std::vector<Vec> grid;                   // faint rings on the x-z plane
double yaw = 0.5, pitch = 0.35, dist = 1400;
double R[3][3];                          // world -> camera rotation
std::vector<float> light(W * H);
std::vector<uint32_t> screen(W * H);
std::mt19937 rng(42);

void camera() {
    double cy = std::cos(yaw), sy = std::sin(yaw), cp = std::cos(pitch), sp = std::sin(pitch);
    double r[3][3] = {{cy, 0, -sy}, {-sp * sy, cp, -sp * cy}, {cp * sy, sp, cp * cy}};
    std::copy(&r[0][0], &r[0][0] + 9, &R[0][0]);
}
Vec to_camera(Vec p) {
    return {R[0][0] * p.x + R[0][1] * p.y + R[0][2] * p.z,
            R[1][0] * p.x + R[1][1] * p.y + R[1][2] * p.z,
            R[2][0] * p.x + R[2][1] * p.y + R[2][2] * p.z};
}
Vec to_world(Vec c) {   // inverse rotation = transpose
    return {R[0][0] * c.x + R[1][0] * c.y + R[2][0] * c.z,
            R[0][1] * c.x + R[1][1] * c.y + R[2][1] * c.z,
            R[0][2] * c.x + R[1][2] * c.y + R[2][2] * c.z};
}

void generate_cloud(int mx, int my, int n = SPAWN) {
    std::normal_distribution<double> jitter(0, 20);
    std::uniform_real_distribution<double> speed(0.4, 1.2);
    // point under the mouse, on the plane through the sun facing the camera
    Vec centre = to_world({(mx - W / 2.0) * dist / FOV, -(my - H / 2.0) * dist / FOV, 0});
    Vec view = to_world({0, 0, 1});                   // direction the camera looks
    for (int i = 0; i < n; i++) {
        Vec p = centre + Vec{jitter(rng), jitter(rng), jitter(rng)};
        Vec t = cross(view, p);                       // spin around the view axis
        particles.push_back({p, t * (SPEED * speed(rng) / (len(t) + 1e-9))});
    }
}

// one step of gravity towards the sun at (0, 0, 0) - same math as move() in gravity3d.py
inline void move(Particle& p) {
    double hyp = len(p.pos);
    if (hyp < 1) return;
    double force = G * MASS * M / hyp;
    p.mom = p.mom + p.pos * (-force * DT / hyp);      // unit vector towards the sun
    p.pos = p.pos + p.mom * (DT / MASS);
}

// project a point; returns false if it is off screen
inline bool project(Vec p, int& x, int& y, float& shade) {
    Vec c = to_camera(p);
    double z = c.z + dist;
    if (z <= 1) return false;
    x = int(W / 2 + c.x * FOV / z);
    y = int(H / 2 - c.y * FOV / z);
    shade = (float)std::clamp(1.6 - z / dist, 0.3, 1.0);   // near = bright
    return x >= 0 && x < W && y >= 0 && y < H;
}

std::vector<int> idx;
std::vector<float> val;
void step_and_draw() {
    camera();
    size_t n = particles.size();
    idx.resize(n); val.resize(n);
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < n; i++) {
        move(particles[i]);
        int x, y; float s;
        if (project(particles[i].pos, x, y, s)) { idx[i] = y * W + x; val[i] = s * GLOW; }
        else idx[i] = -1;
    }
    std::fill(light.begin(), light.end(), 0.f);
    for (size_t i = 0; i < n; i++) if (idx[i] >= 0) light[idx[i]] += val[i];
    for (Vec g : grid) { int x, y; float s; if (project(g, x, y, s)) light[y * W + x] += 80 * s; }

    int sx, sy; float s;
    project({0, 0, 0}, sx, sy, s);
    int r = std::max(2, int(14 * FOV / dist));
    #pragma omp parallel for schedule(static)
    for (int y = 0; y < H; y++)
        for (int x = 0; x < W; x++) {
            int v = std::max(BG, (int)std::min(255.f, light[y * W + x]));
            uint32_t c = v << 16 | v << 8 | v;
            if ((x - sx) * (x - sx) + (y - sy) * (y - sy) <= r * r) c = 0xFFFF00 | v;   // sun
            screen[y * W + x] = c;
        }
}

int main(int argc, char** argv) {
    for (int r : {250, 500, 750})
        for (int i = 0; i < 720; i++) {
            double a = i * 2 * M_PI / 720;
            grid.push_back({r * std::cos(a), 0, r * std::sin(a)});
        }
    using clk = std::chrono::steady_clock;
    double frame_ms[10] = {0};
    auto fps = [&](int frame, double ms) {
        frame_ms[frame % 10] = ms;
        int k = std::min(frame + 1, 10); double avg = 0;
        for (int i = 0; i < k; i++) avg += frame_ms[i] / k;
        return (int)(1000 / avg);
    };
#ifdef USE_SDL
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* win = SDL_CreateWindow("gravity 3d", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, W, H, 0);
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    SDL_Texture* tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, W, H);
    bool dragging = false;
    for (int frame = 0, running = 1; running; frame++) {
        auto t0 = clk::now();
        for (SDL_Event e; SDL_PollEvent(&e);) {
            if (e.type == SDL_QUIT) running = 0;
            else if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) dragging = true;
            else if (e.type == SDL_MOUSEBUTTONUP && e.button.button == SDL_BUTTON_LEFT) dragging = false;
            else if (e.type == SDL_MOUSEMOTION && dragging) {
                yaw -= e.motion.xrel * 0.005;
                pitch = std::clamp(pitch + e.motion.yrel * 0.005, -1.5, 1.5);
            } else if (e.type == SDL_MOUSEWHEEL)
                dist = std::clamp(dist * std::pow(0.9, e.wheel.y), 300.0, 4000.0);
        }
        int mx, my; SDL_GetMouseState(&mx, &my);
        camera();
        if (SDL_GetKeyboardState(nullptr)[SDL_SCANCODE_3]) generate_cloud(mx, my);
        step_and_draw();
        int f = fps(frame, std::chrono::duration<double, std::milli>(clk::now() - t0).count());
        SDL_UpdateTexture(tex, nullptr, screen.data(), W * 4);
        SDL_RenderCopy(ren, tex, nullptr, nullptr);
        SDL_RenderPresent(ren);
        char title[80];
        snprintf(title, sizeof title, "particles : %zu   Fps : %d", particles.size(), f);
        SDL_SetWindowTitle(win, title);
    }
    SDL_Quit();
#else
    // headless: one line of input per frame "mouse_x mouse_y left_button key_3 wheel",
    // raw RGB frames to stdout, "frame particles fps" to stderr
    FILE* in = fopen(argv[1], "r");
    std::vector<uint8_t> rgb(W * H * 3);
    int mx, my, down, key3, wheel, pmx = -1, pmy = -1;
    for (int frame = 0; fscanf(in, "%d %d %d %d %d", &mx, &my, &down, &key3, &wheel) == 5; frame++) {
        auto t0 = clk::now();
        if (down && pmx >= 0) {
            yaw -= (mx - pmx) * 0.005;
            pitch = std::clamp(pitch + (my - pmy) * 0.005, -1.5, 1.5);
        }
        if (wheel) dist = std::clamp(dist * std::pow(0.9, wheel), 300.0, 4000.0);
        pmx = mx; pmy = my;
        camera();
        if (key3) generate_cloud(mx, my);
        step_and_draw();
        int f = fps(frame, std::chrono::duration<double, std::milli>(clk::now() - t0).count());
        fprintf(stderr, "%d %zu %d\n", frame, particles.size(), f);
        for (int i = 0; i < W * H; i++) {
            rgb[3 * i] = screen[i] >> 16; rgb[3 * i + 1] = screen[i] >> 8; rgb[3 * i + 2] = screen[i];
        }
        fwrite(rgb.data(), 1, rgb.size(), stdout);
    }
#endif
}
