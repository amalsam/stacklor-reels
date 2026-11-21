// 1,000,000-particle gravity benchmark - Java
public class Gravity {
    static final int W = 1500, H = 800;
    static final double G = 0.1, M = 1e8, MASS = 2, DT = 0.001, CX = W / 2.0, CY = H / 2.0;
    static final int BG = 0x141414, FG = 0xFFFFFF;
    static int N;
    static double[] xs, ys, pxs, pys;
    static int[] fb = new int[W * H];
    static int s = (int) 2463534242L;

    static double rnd() {
        s ^= s << 13; s ^= s >>> 17; s ^= s << 5;
        return (s & 0xFFFFFFFFL) / 4294967296.0;
    }

    static void frame() {
        final double k = G * MASS * M;
        java.util.Arrays.fill(fb, BG);
        for (int i = 0; i < N; i++) {
            double x = xs[i], y = ys[i];
            double dx = x - CX, dy = y - CY;
            double hyp = Math.sqrt(dx * dx + dy * dy);
            if (hyp >= 1) {
                double theta = Math.atan2(CY - y, CX - x);
                double force = k / hyp;
                double px = pxs[i] + force * Math.cos(theta) * DT;
                double py = pys[i] + force * Math.sin(theta) * DT;
                pxs[i] = px; pys[i] = py;
                x += px / MASS * DT; y += py / MASS * DT;
                xs[i] = x; ys[i] = y;
            }
            int ix = (int) x, iy = (int) y;
            if (ix >= 0 && ix < W && iy >= 0 && iy < H) fb[iy * W + ix] = FG;
        }
    }

    public static void main(String[] a) {
        int frames = a.length > 0 ? Integer.parseInt(a[0]) : 100;
        N = a.length > 1 ? Integer.parseInt(a[1]) : 1_000_000;
        xs = new double[N]; ys = new double[N]; pxs = new double[N]; pys = new double[N];
        for (int i = 0; i < N; i++) { xs[i] = rnd() * W; ys[i] = rnd() * H; pxs[i] = 500; pys[i] = 500; }
        frame(); frame(); frame();
        long t0 = System.nanoTime();
        for (int f = 0; f < frames; f++) frame();
        double ms = (System.nanoTime() - t0) / 1e6 / frames;
        double sum = 0; for (int i = 0; i < N; i++) sum += xs[i] + ys[i];
        System.out.printf("java frames=%d ms=%.3f fps=%.3f check=%.6f%n", frames, ms, 1000 / ms, sum / N);
    }
}
