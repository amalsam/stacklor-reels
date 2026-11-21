// 1,000,000-particle gravity benchmark - JavaScript (Node.js / Bun)
const W = 1500, H = 800, G = 0.1, M = 1e8, MASS = 2, DT = 0.001;
const N = +(process.argv[3] || 1000000), CX = W / 2, CY = H / 2;
const BG = 0x141414, FG = 0xFFFFFF;

let s = 2463534242;
function rnd() {
  s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0;
  return s / 4294967296;
}
const xs = new Float64Array(N), ys = new Float64Array(N);
const pxs = new Float64Array(N).fill(500), pys = new Float64Array(N).fill(500);
for (let i = 0; i < N; i++) { xs[i] = rnd() * W; ys[i] = rnd() * H; }
const fb = new Uint32Array(W * H);

function frame() {
  const k = G * MASS * M;
  fb.fill(BG);
  for (let i = 0; i < N; i++) {
    let x = xs[i], y = ys[i];
    const dx = x - CX, dy = y - CY;
    const hyp = Math.sqrt(dx * dx + dy * dy);
    if (hyp >= 1) {
      const theta = Math.atan2(CY - y, CX - x);
      const force = k / hyp;
      const px = pxs[i] + force * Math.cos(theta) * DT;
      const py = pys[i] + force * Math.sin(theta) * DT;
      pxs[i] = px; pys[i] = py;
      x += px / MASS * DT; y += py / MASS * DT;
      xs[i] = x; ys[i] = y;
    }
    const ix = Math.trunc(x), iy = Math.trunc(y);
    if (ix >= 0 && ix < W && iy >= 0 && iy < H) fb[iy * W + ix] = FG;
  }
}

const frames = +(process.argv[2] || 100);
frame(); frame(); frame();
const t0 = performance.now();
for (let f = 0; f < frames; f++) frame();
const ms = (performance.now() - t0) / frames;
let sum = 0; for (let i = 0; i < N; i++) sum += xs[i] + ys[i];
const rt = typeof Bun !== "undefined" ? "bun" : "node";
console.log(`${rt} frames=${frames} ms=${ms.toFixed(3)} fps=${(1000 / ms).toFixed(3)} check=${(sum / N).toFixed(6)}`);
