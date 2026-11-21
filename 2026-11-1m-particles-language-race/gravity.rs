// 1,000,000-particle gravity benchmark - Rust (std only)
use std::time::Instant;

const W: usize = 1500;
const H: usize = 800;
const G: f64 = 0.1;
const M: f64 = 1e8;
const MASS: f64 = 2.0;
const DT: f64 = 0.001;
const CX: f64 = W as f64 / 2.0;
const CY: f64 = H as f64 / 2.0;
const BG: u32 = 0x141414;
const FG: u32 = 0xFFFFFF;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let frames: usize = args.get(1).map_or(100, |a| a.parse().unwrap());
    let n: usize = args.get(2).map_or(1_000_000, |a| a.parse().unwrap());
    let mut s: u32 = 2463534242;
    let mut rnd = || { s ^= s << 13; s ^= s >> 17; s ^= s << 5; s as f64 / 4294967296.0 };
    let (mut xs, mut ys) = (vec![0.0f64; n], vec![0.0f64; n]);
    for i in 0..n { xs[i] = rnd() * W as f64; ys[i] = rnd() * H as f64; }
    let (mut pxs, mut pys) = (vec![500.0f64; n], vec![500.0f64; n]);
    let mut fb = vec![0u32; W * H];

    let mut frame = || {
        let k = G * MASS * M;
        fb.fill(BG);
        for i in 0..n {
            let (mut x, mut y) = (xs[i], ys[i]);
            let (dx, dy) = (x - CX, y - CY);
            let hyp = (dx * dx + dy * dy).sqrt();
            if hyp >= 1.0 {
                let theta = (CY - y).atan2(CX - x);
                let force = k / hyp;
                let px = pxs[i] + force * theta.cos() * DT;
                let py = pys[i] + force * theta.sin() * DT;
                pxs[i] = px; pys[i] = py;
                x += px / MASS * DT; y += py / MASS * DT;
                xs[i] = x; ys[i] = y;
            }
            let (ix, iy) = (x as i64, y as i64);
            if ix >= 0 && ix < W as i64 && iy >= 0 && iy < H as i64 { fb[iy as usize * W + ix as usize] = FG; }
        }
    };
    frame(); frame(); frame();
    let t0 = Instant::now();
    for _ in 0..frames { frame(); }
    let ms = t0.elapsed().as_secs_f64() * 1000.0 / frames as f64;
    let sum: f64 = xs.iter().zip(&ys).map(|(a, b)| a + b).sum();
    println!("rust frames={} ms={:.3} fps={:.3} check={:.6}", frames, ms, 1000.0 / ms, sum / n as f64);
}
