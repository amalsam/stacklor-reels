// THE SONG: music bed for the voiceover recut. Every hit is read from score.js.
//   node song.js            -> out/music.wav  (bed, mastered quieter so the TTS sits on top)
//   VO=path node song.js    -> out/music.wav  with the voiceover mixed in and the music ducked under it
const path = require('path');
const { SR, Bus, reverb, pingpong } = require('./engine/audio/dsp');
const I = require('./engine/audio/instruments');
const MIX = require('./engine/audio/mix');
const Genre = require('./engine/audio/genres');
const sc = require('./score');
const { BEAT, DURATION, m, ev, clock, chordAt } = sc;

const N = Math.ceil(DURATION * SR);
const bus = () => new Bus(N);
const drums = bus(), bass = bus(), pad = bus(), keys = bus(), fx = bus(), verb = bus(), dly = bus();
const B = { drums, bass, pad, keys };
const kicks = [];
const play = (from, to, o = {}) => Genre.play('edm', { clock, from, to, chordAt, buses: B, kicks, ...o });
const bar = (t) => Math.round(t / 2);
const hz = (n) => 440 * Math.pow(2, (m(n) - 69) / 12);

play(0, bar(ev.go));                                    // hook + explainer
play(bar(ev.go), bar(ev.twist), { fill: [bar(ev.twist) - 1] }); // the countdown
play(bar(ev.twist), Math.ceil(ev.mtGo / 2), { drums: false, gain: 0.6 }); // nobody hit 60: drums out
play(Math.floor(ev.mtGo / 2), bar(ev.specs));            // 4 cores
play(bar(ev.specs), bar(ev.cta), { drums: false, gain: 1.2 }); // specs card
play(bar(ev.cta), Math.ceil(DURATION / 2));              // call to action
for (const b of [drums, bass]) MIX.gate(b, ev.twist, ev.mtGo - 0.01);

const CR = I.crash(18), CR2 = I.crash(21);
drums.addMono(CR, 0, 0.35); fx.addMono(I.subBoom(1.6), 0, 0.5);
fx.addMono(I.noiseSweep(0.5, 600, 6000, { pink: true }), ev.hook2 - 0.1, 0.16);
ev.chips.forEach((t, i) => { const x = I.bell(hz(['E5', 'G5', 'A5', 'C6'][i]), 0.6); keys.addMono(x, t, 0.3, (i - 1.5) * 0.3); verb.addMono(x, t, 0.2); });
fx.addMono(I.noiseSweep(1.2, 300, 5000, { pink: true, shape: (x) => x * x }), ev.four - 1.2, 0.18);
fx.addMono(I.thud(70, 0.1), ev.four, 0.6); drums.addMono(CR2, ev.four, 0.2);
ev.rules.forEach((t, i) => fx.addMono(I.pop(1 + i * 0.15), t, 0.45));
// each rank: a whoosh in, then the FPS number lands on a bell. Pitch climbs as we approach #1.
const scale = ['A4', 'C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'E6'];
ev.ranks.forEach((r, i) => {
  fx.addMono(I.noiseSweep(0.35, 500, 5000, { pink: true }), r.t - 0.3, 0.2);
  fx.addMono(I.thud(90, 0.08), r.t, 0.45);
  const x = I.bell(hz(scale[i]), 0.9); keys.addMono(x, r.land, r.place === 1 ? 0.55 : 0.38); verb.addMono(x, r.land, 0.22); dly.addMono(x, r.land, 0.06);
});
drums.addMono(CR, ev.ranks[7].land, 0.35);
fx.addMono(I.bwomp(), ev.twist, 0.45);
fx.addMono(I.noiseSweep(1.4, 200, 9000, { pink: true, shape: (x) => x * x }), ev.mtGo - 1.4, 0.3);
drums.addMono(CR, ev.mtGo, 0.45); fx.addMono(I.subBoom(2.2), ev.mtGo, 0.7);
{ const x = I.bell(hz('E6'), 1.2); keys.addMono(x, ev.mtFinish, 0.6); verb.addMono(x, ev.mtFinish, 0.3); }
fx.addMono(I.paperFwip(0.9, 7), ev.specs - 0.03, 0.3);
drums.addMono(CR, ev.cta, 0.3);

MIX.sidechain([pad, bass], kicks, { depth: 0.5 });
const stems = { drums, bass, pad, keys, fx, verb: reverb(verb, { room: 0.8, damp: 0.3 }), dly: pingpong(dly, BEAT * 0.75, 0.35, 3500) };
const GAIN = { drums: 0.55, bass: 0.7, pad: 1.4, keys: 1.3, fx: 0.9, verb: 1, dly: 1 };
const out = path.join(__dirname, 'out');
const mix = MIX.mixdown(stems, GAIN, { stemDir: process.env.STEMS ? out : null });
MIX.highpass(mix, 25);
if (process.env.VO) {
  const vo = MIX.loadAudio(process.env.VO, { at: 0, gain: 1, length: DURATION });
  MIX.duck([mix], vo, { depth: 0.55 });
  vo.mixInto(mix, 1.0);
}
MIX.fadeOut(mix, DURATION - 0.8, DURATION);
const target = process.env.VO ? -14 : -19; // the bed alone sits ~5 dB under where the voice will go
const M = MIX.master(mix, 0.8, undefined, { lufs: target });
MIX.writeWav(path.join(out, process.env.VO ? 'final-mix.wav' : 'music.wav'), mix);
console.log(`wrote (${DURATION}s, ${M.lufs.toFixed(1)} LUFS)`);
