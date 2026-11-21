// THE SCORE: single source of truth for the whole reel (music, explainer animation AND the Python compositor,
// which reads `node -e "console.log(JSON.stringify(require('./score')))"`).
(function () {
  const node = typeof require !== 'undefined';
  const U = node ? require('./engine/util') : globalThis.U;
  const MU = node ? require('./engine/music') : globalThis.MUSIC;
  const { m, makeClock, makeChords } = MU;

  const FPS = 30;
  const FORMAT = U.pickFormat('9:16');
  const STYLE = 'neon';
  const [W, H] = U.formatSize(FORMAT);
  const SAFE = U.safeArea(W, H);
  const clock = makeClock({ bpm: 120, offset: 0 }); // 1 beat = 0.5 s, 1 bar = 2 s
  const { T, BEAT } = clock;
  const DURATION = 72.2;

  // ---- measured results (median of 3 runs, 1,000,000 particles, see bench/results/raw.txt) ----
  const RESULTS = [
    { id: 'python', name: 'Python', sub: 'pure, 3.13', ms: 467.689, color: '#4B8BBE' },
    { id: 'numpy', name: 'NumPy', sub: 'Python + NumPy', ms: 60.085, color: '#4DABCF' },
    { id: 'js', name: 'JavaScript', sub: 'Node 22', ms: 54.553, color: '#F7DF1E' },
    { id: 'java', name: 'Java', sub: 'OpenJDK 21', ms: 49.143, color: '#F89820' },
    { id: 'go', name: 'Go', sub: 'Go 1.24', ms: 42.330, color: '#00ADD8' },
    { id: 'rust', name: 'Rust', sub: 'rustc 1.97', ms: 45.645, color: '#DEA584' },
    { id: 'c', name: 'C', sub: 'gcc -O3', ms: 34.864, color: '#A8B9CC' },
    { id: 'cpp', name: 'C++', sub: 'g++ -O3', ms: 39.161, color: '#659AD2' },
  ];
  const MT = { id: 'cppmt', name: 'C++ x4', sub: 'OpenMP, 4 threads', ms: 10.856, color: '#FF5C8A' };
  const GOAL = 150; // frames
  for (const r of [...RESULTS, MT]) { r.fps = 1000 / r.ms; r.finish = (r.ms * GOAL) / 1000; }
  const order = [...RESULTS].sort((a, b) => a.ms - b.ms);
  order.forEach((r, i) => (r.place = i + 1));

  // ---- timeline: driven by the voiceover slots (vo) ----
  const RANK0 = 16.5, RANK_LEN = 4;
  const ev = {
    hook: 0,
    hook2: 1.8,            // "#1 is not who you think"
    explain: 5.0,
    chips: [5.4, 5.9, 6.4, 6.9],
    times: 9.0,
    four: 10.2,
    sixty: 12.5, big: 12.5, // (60 FPS card dropped in the recut)
    rules: [12.7, 13.3, 13.9],
    count: [RANK0, RANK0, RANK0],   // (countdown dropped in the recut)
    go: RANK0,
    ranks: [],
    twist: RANK0 + 8 * RANK_LEN, // 48.5
    mtGo: 52.5,
    specs: 57.0,
    cta: 60.5,
    end: DURATION,
  };
  // slowest first: last place is revealed first, the winner last
  const slowFirst = [...order].reverse();
  slowFirst.forEach((r, i) => ev.ranks.push({ id: r.id, place: r.place, t: RANK0 + i * RANK_LEN, land: RANK0 + i * RANK_LEN + 1.4 }));
  ev.mtFinish = ev.mtGo + MT.finish;
  ev.mtLand = ev.mtGo + 1.0;

  // ---- voiceover script (TTS). at = slot start, end = slot end; keep each line inside its slot ----
  const vo = [
    { id: 'hook', at: 0.0, end: 5.0, text: 'Nine languages, one million particles, and number one is not who you think.' },
    { id: 'math', at: 5.0, end: 9.0, text: 'Every frame, every particle runs square root, a-tan-two, cosine and sine.' },
    { id: 'four', at: 9.0, end: 12.5, text: 'Times a million: four million math calls, every frame.' },
    { id: 'rules', at: 12.5, end: 16.5, text: 'Same code, same seed, one core each. Starting from last place.' },
    { id: 'python', text: 'Last place. Pure Python. Two FPS. You can watch it think.' },
    { id: 'numpy', text: 'NumPy pushes the math into C. Sixteen FPS. Eight times faster.' },
    { id: 'js', text: 'JavaScript on Node. Eighteen FPS. The JIT earns its keep.' },
    { id: 'java', text: 'Java. Twenty FPS. And the next one will upset Rust fans.' },
    { id: 'rust', text: 'Rust. Twenty two FPS. Yes, it finished behind Go.' },
    { id: 'go', text: 'Go takes bronze. Twenty three point six FPS.' },
    { id: 'cpp', text: 'C plus plus takes second. Twenty five FPS. Who beat it?' },
    { id: 'c', text: 'Plain old C. Twenty eight point seven. Fastest on one core.' },
    { id: 'twist', at: 48.5, end: 52.5, text: 'Nobody hit sixty. So I gave C plus plus all four cores.' },
    { id: 'mt', at: 52.5, end: 57.0, text: 'Ninety two FPS. A hundred fifty frames in one point six seconds.' },
    { id: 'specs', at: 57.0, end: 60.5, text: 'Tested on a four core cloud Xeon. Specs on screen.' },
    { id: 'cta', at: 60.5, end: 64.5, text: 'Which language should I run on a million particles next?' },
  ];
  for (const r of ev.ranks) { const v = vo.find((x) => x.id === r.id); v.at = r.t; v.end = r.t + RANK_LEN; }
  // on-screen captions use the same text, but numbers as digits
  const CAP = { hook: '9 languages, 1,000,000 particles, and #1 is not who you think.', math: 'Every frame, every particle runs sqrt, atan2, cos and sin.', four: 'Times a million: 4,000,000 math calls, every frame.', rules: 'Same code, same seed, 1 core each. Starting from last place.',
    python: 'Last place. Pure Python. 2 FPS. You can watch it think.', numpy: 'NumPy pushes the math into C. 16 FPS. 8x faster.',
    js: 'JavaScript on Node. 18 FPS. The JIT earns its keep.', java: 'Java. 20 FPS. And the next one will upset Rust fans.',
    rust: 'Rust. 22 FPS. Yes, it finished behind Go.', go: 'Go takes bronze. 23.6 FPS.', cpp: 'C++ takes second. 25 FPS. Who beat it?',
    c: 'Plain old C. 28.7 FPS. Fastest on one core.', twist: 'Nobody hit 60. So I gave C++ all 4 cores.',
    mt: '92 FPS. 150 frames in 1.6 seconds.', specs: 'Tested on a 4-core cloud Xeon. Specs on screen.',
    cta: 'Which language should I run on 1,000,000 particles next?' };
  for (const v of vo) v.cap = CAP[v.id] || v.text;

  // ---- synced to the recorded voiceover (out/voiceover.wav, 71.6 s; speech starts found with silencedetect) ----
  const SYNC = {
    hook: [0.0, 0.26], math: [5.3, 5.49], four: [10.5, 10.67], rules: [14.7, 14.9], python: [19.65, 19.87], numpy: [25.1, 25.32],
    js: [30.2, 30.4], java: [34.3, 34.51], rust: [38.85, 39.07], go: [43.3, 43.53], cpp: [46.8, 47.04], c: [51.4, 51.61],
    twist: [55.6, 55.8], mt: [60.2, 60.4], specs: [65.0, 65.24], cta: [68.55, 68.79],
  };
  const LAND = { python: 22.1, numpy: 27.4, js: 31.7, java: 35.2, rust: 39.8, go: 44.8, cpp: 48.7, c: 52.7 };
  vo.forEach((v, i) => { v.at = SYNC[v.id][0]; v.end = i + 1 < vo.length ? SYNC[vo[i + 1].id][0] : DURATION; });
  Object.assign(ev, {
    hook2: 2.7, explain: SYNC.math[0], chips: [7.4, 8.1, 8.8, 9.4], times: SYNC.four[0], four: 11.75,
    sixty: SYNC.rules[0], big: SYNC.rules[0], rules: [15.0, 15.8, 16.6], go: SYNC.python[0],
    twist: SYNC.twist[0], mtGo: SYNC.mt[0], specs: SYNC.specs[0], cta: SYNC.cta[0], end: DURATION,
  });
  ev.count = [ev.go, ev.go, ev.go];
  for (const r of ev.ranks) { r.t = SYNC[r.id][0]; r.land = LAND[r.id]; }
  ev.mtFinish = ev.mtGo + MT.finish;
  ev.mtLand = ev.mtGo + 0.4;

  const S = {
    hook: [0, ev.explain], explain: [ev.explain, ev.go], ranks: [ev.go, ev.twist],
    twist: [ev.twist, ev.mtGo], mt: [ev.mtGo, ev.specs], specs: [ev.specs, ev.cta], cta: [ev.cta, DURATION],
  };

  const { chords, chordAt } = makeChords(clock, {
    Am: { notes: ['A3', 'C4', 'E4'], bass: 'A1' }, F: { notes: ['A3', 'C4', 'F4'], bass: 'F1' },
    C: { notes: ['G3', 'C4', 'E4'], bass: 'C2' }, G: { notes: ['G3', 'B3', 'D4'], bass: 'G1' },
  }, Array.from({ length: 38 }, (_, b) => [b, 0, 4, ['Am', 'F', 'C', 'G'][b % 4]]));

  const markers = {
    four: { t: ev.four, sync: 'av' },
    mtGo: { t: ev.mtGo, sync: 'a' },
  };

  const SCORE = { FPS, FORMAT, STYLE, W, H, SAFE, DURATION, clock, T, BEAT, S, m, chords, chordAt, ev, vo, markers, RESULTS, MT, GOAL, order };
  if (node) module.exports = SCORE; else globalThis.SCORE = SCORE;
})();
