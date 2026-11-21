// 1,000,000-particle gravity benchmark - Go
package main

import (
	"fmt"
	"math"
	"os"
	"strconv"
	"time"
)

const (
	W, H           = 1500, 800
	G, M, MASS, DT = 0.1, 1e8, 2.0, 0.001
	CX, CY         = W / 2.0, H / 2.0
	BG, FG         = 0x141414, 0xFFFFFF
)

var s uint32 = 2463534242

func rnd() float64 {
	s ^= s << 13
	s ^= s >> 17
	s ^= s << 5
	return float64(s) / 4294967296.0
}

func main() {
	frames, n := 100, 1000000
	if len(os.Args) > 1 { frames, _ = strconv.Atoi(os.Args[1]) }
	if len(os.Args) > 2 { n, _ = strconv.Atoi(os.Args[2]) }
	xs, ys := make([]float64, n), make([]float64, n)
	pxs, pys := make([]float64, n), make([]float64, n)
	for i := 0; i < n; i++ {
		xs[i] = rnd() * W
		ys[i] = rnd() * H
		pxs[i], pys[i] = 500, 500
	}
	fb := make([]uint32, W*H)
	frame := func() {
		const k = G * MASS * M
		for i := range fb { fb[i] = BG }
		for i := 0; i < n; i++ {
			x, y := xs[i], ys[i]
			dx, dy := x-CX, y-CY
			hyp := math.Sqrt(dx*dx + dy*dy)
			if hyp >= 1 {
				theta := math.Atan2(CY-y, CX-x)
				force := k / hyp
				px := pxs[i] + force*math.Cos(theta)*DT
				py := pys[i] + force*math.Sin(theta)*DT
				pxs[i], pys[i] = px, py
				x += px / MASS * DT
				y += py / MASS * DT
				xs[i], ys[i] = x, y
			}
			ix, iy := int(x), int(y)
			if ix >= 0 && ix < W && iy >= 0 && iy < H { fb[iy*W+ix] = FG }
		}
	}
	frame(); frame(); frame()
	t0 := time.Now()
	for f := 0; f < frames; f++ { frame() }
	ms := float64(time.Since(t0).Nanoseconds()) / 1e6 / float64(frames)
	sum := 0.0
	for i := 0; i < n; i++ { sum += xs[i] + ys[i] }
	fmt.Printf("go frames=%d ms=%.3f fps=%.3f check=%.6f\n", frames, ms, 1000/ms, sum/float64(n))
}
