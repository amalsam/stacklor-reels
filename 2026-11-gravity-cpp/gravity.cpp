// Gravity particle simulation - C++ port of gravity.py
// Same physics, same controls: hold 1 / 2 / 3 or Left Ctrl to spawn particles.
//
// Window build (needs SDL2):   g++ -O3 -march=native -DUSE_SDL gravity.cpp -o gravity -lSDL2
// Headless build (raw frames): g++ -O3 -march=native gravity.cpp -o gravity
//                              ./gravity | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1500x800 -r 60 -i - out.mp4
#include <cmath>
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <chrono>
#include <random>
#include <vector>
#ifdef USE_SDL
#include <SDL2/SDL.h>
#endif

const int WIDTH = 1500;
const int HEIGHT = 800;
const double G = 0.1;
const double M = 10e7;

struct Particle {
    double x, y;
    double momentum_x = 500, momentum_y = 500;
    double mass = 2, dt = 0.001;
};

std::vector<Particle> particles;
std::vector<uint32_t> screen(WIDTH * HEIGHT);
std::mt19937 rng(42);

// one step of gravity toward (x2, y2) - same math as move_numba()
inline void move(Particle& p, double x2, double y2) {
    double hyp = std::sqrt((p.x - x2) * (p.x - x2) + (p.y - y2) * (p.y - y2));
    if (hyp < 1) return;
    double theta = std::atan2(y2 - p.y, x2 - p.x);
    double force = (G * p.mass * M) / hyp;
    p.momentum_x += force * std::cos(theta) * p.dt;
    p.momentum_y += force * std::sin(theta) * p.dt;
    p.x += p.momentum_x / p.mass * p.dt;
    p.y += p.momentum_y / p.mass * p.dt;
}

void generate_circle(double cx, double cy) {
    std::uniform_real_distribution<double> u(0, 1);
    for (int i = 0; i < 100; i++) {
        double ang = u(rng) * 2 * M_PI, hyp = std::sqrt(u(rng)) * 50;
        particles.push_back({cx + std::cos(ang) * hyp, cy + std::sin(ang) * hyp});
    }
}
void generate_line(double y) {
    std::uniform_int_distribution<int> rx(0, WIDTH - 1);
    for (int i = 0; i < 100; i++) particles.push_back({(double)rx(rng), y});
}
void generate_line2(double x) {
    std::uniform_int_distribution<int> ry(0, HEIGHT - 1);
    for (int i = 0; i < 100; i++) particles.push_back({x, (double)ry(rng)});
}

inline void plot(int x, int y, uint32_t c) {
    if (x > 0 && x < WIDTH - 1 && y > 0 && y < HEIGHT - 1) {
        uint32_t* px = &screen[y * WIDTH + x];
        px[0] = px[-1] = px[1] = px[-WIDTH] = px[WIDTH] = c;
    }
}

void draw(double cx, double cy) {
    std::fill(screen.begin(), screen.end(), 0x141414);
    for (auto& p : particles) {
        move(p, cx, cy);
        plot((int)p.x, (int)p.y, 0xFFFFFF);
    }
    for (int dy = -15; dy <= 15; dy++)          // central mass
        for (int dx = -15; dx <= 15; dx++)
            if (dx * dx + dy * dy <= 225) screen[(int(cy) + dy) * WIDTH + int(cx) + dx] = 0xFFFF00;
}

int main(int argc, char** argv) {
    const double cx = WIDTH / 2, cy = HEIGHT / 2;
    using clk = std::chrono::steady_clock;
    double frame_ms[10] = {0};
    int frame = 0;
#ifdef USE_SDL
    SDL_Init(SDL_INIT_VIDEO);
    SDL_Window* win = SDL_CreateWindow("gravity", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, WIDTH, HEIGHT, 0);
    SDL_Renderer* ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
    SDL_Texture* tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING, WIDTH, HEIGHT);
    for (bool running = true; running; frame++) {
        auto t0 = clk::now();
        for (SDL_Event e; SDL_PollEvent(&e);) if (e.type == SDL_QUIT) running = false;
        const Uint8* key = SDL_GetKeyboardState(nullptr);
        int mx, my; SDL_GetMouseState(&mx, &my);
        if (key[SDL_SCANCODE_LCTRL]) particles.push_back({(double)mx, (double)my});
        if (key[SDL_SCANCODE_1]) generate_line(my);
        if (key[SDL_SCANCODE_2]) generate_circle(mx, my);
        if (key[SDL_SCANCODE_3]) generate_line2(mx);
        draw(cx, cy);
        SDL_UpdateTexture(tex, nullptr, screen.data(), WIDTH * 4);
        SDL_RenderCopy(ren, tex, nullptr, nullptr);
        SDL_RenderPresent(ren);
        frame_ms[frame % 10] = std::chrono::duration<double, std::milli>(clk::now() - t0).count();
        double avg = 0; for (double f : frame_ms) avg += f / 10;
        char title[64];
        snprintf(title, sizeof title, "particles : %zu   Fps : %d", particles.size(), (int)(1000 / avg));
        SDL_SetWindowTitle(win, title);
    }
    SDL_Quit();
#else
    // headless: scripted input (hold "3" at x=450 for 300 frames), raw RGB frames to stdout,
    // "frame particles fps" stats to stderr
    int total = argc > 1 ? atoi(argv[1]) : 840;
    std::vector<uint8_t> rgb(WIDTH * HEIGHT * 3);
    for (; frame < total; frame++) {
        auto t0 = clk::now();
        if (frame >= 10 && frame < 310) generate_line2(450);
        draw(cx, cy);
        frame_ms[frame % 10] = std::chrono::duration<double, std::milli>(clk::now() - t0).count();
        int n = frame < 9 ? frame + 1 : 10;
        double avg = 0; for (int i = 0; i < n; i++) avg += frame_ms[i] / n;
        fprintf(stderr, "%d %zu %d\n", frame, particles.size(), (int)(1000 / avg));
        for (int i = 0; i < WIDTH * HEIGHT; i++) {
            rgb[3 * i] = screen[i] >> 16; rgb[3 * i + 1] = screen[i] >> 8; rgb[3 * i + 2] = screen[i];
        }
        fwrite(rgb.data(), 1, rgb.size(), stdout);
    }
#endif
}
