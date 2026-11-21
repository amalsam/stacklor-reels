// THE EXPLAINER: what one frame of the benchmark costs, then the rules and the countdown.
// Drawn only for t in [explain, go); the rest of the reel is composed from real simulation frames.
(function () {
  const U = globalThis.U, G = globalThis.G, S = globalThis.SCORE, Studio = globalThis.Studio, Data = globalThis.Data;
  const { ev, BEAT } = S;
  const { clamp, lerp, ease, pulse } = U;
  const W = G.W, H = G.H, SA = G.SAFE;
  const CX = SA.x + SA.w / 2;
  const BG = '#0B0C10', YEL = '#FFD23F', ORG = '#FF8A3D', CYAN = '#4CE0FF', PINK = '#FF5C8A', WHITE = '#F4F6FB';
  const pop = (t, t0, d = 0.22) => ease.outBack(clamp((t - t0) / d), 2.2);
  const fade = (t, t0, t1, d = 0.2) => clamp((t - t0) / d) * clamp((t1 - t) / d);

  function title(ctx, str, y, t, t0, t1, color = WHITE, size = 64) {
    const a = fade(t, t0, t1, 0.15);
    if (a <= 0) return;
    G.text(ctx, str, CX, y + (1 - pop(t, t0, 0.25)) * 30, { size, fam: 'Bungee', color, align: 'center', alpha: a });
  }

  // a particle being pulled into the central mass: the thing every line of code is doing
  function orbit(ctx, t, cy, alpha) {
    if (alpha <= 0) return;
    ctx.save(); ctx.globalAlpha = alpha;
    const mx = CX, my = cy;
    const g = ctx.createRadialGradient(mx, my, 0, mx, my, 110);
    g.addColorStop(0, 'rgba(255,210,63,0.9)'); g.addColorStop(1, 'rgba(255,210,63,0)');
    ctx.fillStyle = g; ctx.fillRect(mx - 110, my - 110, 220, 220);
    G.ellipse(ctx, mx, my, 34, 34, { fill: YEL, seed: 2 });
    const a = (t - ev.explain) * 2.2;
    const r = 230 - 40 * Math.sin(a * 0.7);
    const px = mx + Math.cos(a) * r * 1.25, py = my + Math.sin(a) * r * 0.75;
    for (let k = 1; k < 18; k++) { const b = a - k * 0.06, rr = 230 - 40 * Math.sin(b * 0.7); ctx.fillStyle = `rgba(244,246,251,${0.5 * (1 - k / 18)})`; ctx.beginPath(); ctx.arc(mx + Math.cos(b) * rr * 1.25, my + Math.sin(b) * rr * 0.75, 7 * (1 - k / 22), 0, 7); ctx.fill(); }
    ctx.fillStyle = WHITE; ctx.beginPath(); ctx.arc(px, py, 11, 0, 7); ctx.fill();
    // the pull: a dashed line from particle to mass
    ctx.setLineDash([12, 10]); ctx.strokeStyle = 'rgba(76,224,255,0.8)'; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(mx, my); ctx.stroke(); ctx.setLineDash([]);
    ctx.restore();
  }

  const CHIPS = ['sqrt()', 'atan2()', 'cos()', 'sin()'];
  function chips(ctx, t) {
    // A: a 2x2 grid; B: shrink into a row under the counter
    const toRow = ease.inOutCubic(clamp((t - ev.times) / 0.35));
    const out = fade(t, ev.chips[0], ev.sixty, 0.2);
    if (out <= 0) return;
    CHIPS.forEach((c, i) => {
      const p = pop(t, ev.chips[i]);
      if (p <= 0) return;
      const gx = CX + (i % 2 ? 1 : -1) * 225, gy = SA.y + 860 + Math.floor(i / 2) * 170;
      const rx = CX + (i - 1.5) * 225, ry = SA.y + 330;
      const x = lerp(gx, rx, toRow), y = lerp(gy, ry, toRow);
      const s = lerp(1, 0.5, toRow) * p;
      const w = 400 * s, h = 130 * s;
      const flash = pulse(t, ev.chips[i], 8);
      ctx.save(); ctx.globalAlpha = out;
      G.rrect(ctx, x - w / 2, y - h / 2, w, h, 22 * s, { fill: flash > 0.05 ? G.tint('#1C2233', flash * 0.6) : '#161B28', stroke: [CYAN, YEL, ORG, PINK][i], lw: 5, seed: 10 + i });
      G.text(ctx, c, x, y + 20 * s, { size: 64 * s, fam: 'Inter', weight: 800, color: [CYAN, YEL, ORG, PINK][i], align: 'center' });
      ctx.restore();
    });
  }

  function counters(ctx, t) {
    // B: x 1,000,000 -> 4,000,000 per frame
    const aB = fade(t, ev.times, ev.sixty, 0.2);
    if (aB > 0) {
      ctx.save(); ctx.globalAlpha = aB;
      G.text(ctx, 'x', CX - 370, SA.y + 600, { size: 90, fam: 'Bungee', color: CYAN, align: 'center' });
      Data.counter(ctx, { x: CX + 40, y: SA.y + 600, from: 0, to: 1000000, t, t0: ev.times, t1: ev.four - 0.1, size: 96, color: WHITE, align: 'center', fam: 'Bungee' });
      G.text(ctx, 'particles', CX, SA.y + 690, { size: 50, fam: 'Inter', weight: 700, color: '#9AA3B8', align: 'center' });
      if (t >= ev.four) {
        const s = 1 + 0.6 * Math.exp(-(t - ev.four) * 10);
        G.text(ctx, '= 4,000,000', CX, SA.y + 880, { size: 118 * s, fam: 'Bungee', color: YEL, align: 'center' });
        G.text(ctx, 'math calls. per frame.', CX, SA.y + 970, { size: 56, fam: 'Inter', weight: 800, color: WHITE, align: 'center' });
      }
      ctx.restore();
    }
    // C: 60 FPS -> 240,000,000 per second
    const aC = fade(t, ev.sixty, ev.rules[0], 0.2);
    if (aC > 0) {
      ctx.save(); ctx.globalAlpha = aC;
      G.text(ctx, 'to hit 60 FPS', CX, SA.y + 380 + (1 - pop(t, ev.sixty)) * 40, { size: 84, fam: 'Bungee', color: CYAN, align: 'center' });
      Data.counter(ctx, { x: CX, y: SA.y + 640, from: 0, to: 240000000, t, t0: ev.sixty + 0.1, t1: ev.big - 0.05, size: 104, color: t >= ev.big ? PINK : WHITE, align: 'center', fam: 'Bungee' });
      if (t >= ev.big) {
        const s = 1 + 0.5 * Math.exp(-(t - ev.big) * 10);
        G.text(ctx, 'every second', CX, SA.y + 760, { size: 70 * s, fam: 'Inter', weight: 800, color: WHITE, align: 'center' });
        G.text(ctx, 'on ONE cpu core', CX, SA.y + 860, { size: 56, fam: 'Inter', weight: 700, color: '#9AA3B8', align: 'center', alpha: clamp((t - ev.big - 0.15) / 0.2) });
      }
      ctx.restore();
    }
  }

  const RULES = ['1 CPU core each', 'same seed, same start', 'checksums must match'];
  function rules(ctx, t) {
    const a = fade(t, ev.rules[0], ev.count[0], 0.15);
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha = a;
    G.text(ctx, 'THE RULES', CX, SA.y + 330, { size: 90, fam: 'Bungee', color: YEL, align: 'center' });
    RULES.forEach((r, i) => {
      const p = pop(t, ev.rules[i]);
      if (p <= 0) return;
      const y = SA.y + 520 + i * 190;
      const x0 = SA.x + 70;
      ctx.save(); ctx.translate(x0 + 45, y - 22); ctx.scale(p, p);
      G.ellipse(ctx, 0, 0, 45, 45, { fill: '#1E3B2B', stroke: '#5BEA8C', lw: 5, seed: 30 + i });
      G.line(ctx, [[-20, 2], [-5, 18], [22, -16]], { color: '#5BEA8C', lw: 9, seed: 40 + i });
      ctx.restore();
      G.text(ctx, r, x0 + 120, y, { size: 60, fam: 'Inter', weight: 800, color: WHITE, alpha: clamp(p) });
    });
    ctx.restore();
  }

  function countdown(ctx, t) {
    if (t < ev.count[0] || t >= ev.go) return;
    G.text(ctx, 'FIRST TO 150 FRAMES', CX, SA.y + 330, { size: 70, fam: 'Bungee', color: WHITE, align: 'center' });
    G.text(ctx, '8 languages. 1 core each.', CX, SA.y + 420, { size: 48, fam: 'Inter', weight: 700, color: '#9AA3B8', align: 'center' });
    const i = ev.count.findIndex((c, k) => t >= c && (k === 2 || t < ev.count[k + 1]));
    const k = t - ev.count[i];
    const s = 1.6 - 0.6 * ease.outCubic(clamp(k / 0.18));
    const col = [PINK, ORG, YEL][i];
    ctx.save(); ctx.translate(CX, SA.y + 820); ctx.scale(s, s);
    G.ellipse(ctx, 0, 0, 230, 230, { stroke: col, lw: 10, seed: 50 + i });
    G.text(ctx, String(3 - i), 0, 110, { size: 320, fam: 'Bungee', color: col, align: 'center' });
    ctx.restore();
  }

  Studio.film({
    draw(ctx, t) {
      ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
      if (t < ev.explain || t >= ev.go) return;
      // faint grid: graph paper of a physics sim
      ctx.strokeStyle = 'rgba(76,224,255,0.06)'; ctx.lineWidth = 2;
      for (let x = 0; x < W; x += 90) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
      for (let y = 0; y < H; y += 90) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
      title(ctx, 'EVERY FRAME,', SA.y + 170, t, ev.explain, ev.times);
      title(ctx, 'EVERY PARTICLE:', SA.y + 250, t, ev.explain + 0.12, ev.times, YEL);
      orbit(ctx, t, SA.y + 520, fade(t, ev.explain, ev.times, 0.2));
      chips(ctx, t);
      counters(ctx, t);
      rules(ctx, t);
      countdown(ctx, t);
    },
    post: { paper: 0, vignette: 0.3, grain: 0.03, bloom: 0.35 },
    fadeOut: 0,
  });
})();
