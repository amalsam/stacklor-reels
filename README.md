# Stacklor Reels

Source code for the coding and simulation reels on Instagram and YouTube. Every video gets its own folder, so the link in a caption or DM goes straight to the code you saw.

Want to play with these in the browser instead? Many have an interactive version at **[labs.stacklor.com](https://labs.stacklor.com)**.

## Reels

<!-- reels:start -->
| Date | Reel | Language | Watch | Play in browser |
| --- | --- | --- | --- | --- |
| 2026-02 | [Gravity, black hole and galaxy sims in plain Java](2026-02-java-gravity-blackhole-galaxy/) | java | – | [gravity](https://labs.stacklor.com/gravity/), [blackhole](https://labs.stacklor.com/blackhole/), [galaxy](https://labs.stacklor.com/galaxy/) |
| 2024-03 | [Self-driving car learns a track with NEAT](2024-03-self-driving-car-neat/) | python | – | – |
| 2024-02 | [Thousands of particles under gravity](2024-02-gravity-particles-pygame/) | python | – | [gravity](https://labs.stacklor.com/gravity/), [nparticle](https://labs.stacklor.com/nparticle/) |
<!-- reels:end -->

## Folder layout

```
YYYY-MM-short-name/
  README.md         what the video shows, how to run it, what to tweak
  reel.json         title, date, links to the reel and to labs
  main.py           (or index.html, *.java, ...)
  requirements.txt  for Python reels
  assets/           images and data the code needs
```

## Adding a new reel

1. Copy `_template/` to a new folder named `YYYY-MM-short-name`.
2. Put the code in, fill in `README.md` and `reel.json`.
3. Once the reel is posted, add its Instagram and YouTube links to `reel.json`.
4. Run `python scripts/build_index.py` to update the table above and `reels.json`.

Rendered videos (`.mp4`, `.mov`) stay out of the repo. Link the reel instead.

## License

MIT. Use the code for your own projects and videos. A credit or tag is appreciated.
