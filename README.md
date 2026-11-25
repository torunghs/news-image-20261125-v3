# news-image-20261125-v3 — GLOBAL DAILY front page

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/torunghs/news-image-20261125-v3/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/torunghs/news-image-20261125-v3/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Entry for the make.fun `news-image-20261125` competition: a program that
renders a 1024x1024 newspaper front page for Wednesday 25 November 2026
and writes it as `entry.png`.

## What it draws

- Masthead **GLOBAL DAILY**, dated Wednesday 25 November 2026.
- Hero panel: a night sky with stars, the moon, a rocket lifting off its
  pad (Shenzhou-24, Jiuquan) and a space station in orbit.
- Headline: **FIRST FOREIGN ASTRONAUT FLIES TO TIANGONG** — Pakistan's
  Muhammad Zeeshan Ali, 40, joins the Shenzhou-24 crew, the first
  Pakistani in orbit and the first foreign astronaut aboard Tiangong.
- Second story: **US SPY AGENCIES HACKED** — the unclassified networks of
  the CIA and the ODNI were breached; no classified data was exposed.
- Three cards: Riyadh drone strike, Ebola evacuation, Ukraine strikes
  at sea.
- An "Also today" strip (Huawei, Nepal quake, Giuliani, Sarkozy, NVIDIA)
  and a page footer.

## How it works

`main.py` is a single self-contained program using only the Python
standard library. It paints into an RGB canvas with small shape helpers
(rectangles, discs, triangles), sets the lettering with a hand-drawn 5x7
bitmap font defined in the file, and writes the PNG with a hand-rolled
encoder (`zlib` + `struct`). There is no clock, no randomness, no network
access and no sibling import, so every run produces byte-identical output.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=/tmp/out python3 -P -s main.py
# writes /tmp/out/entry.png (1024x1024)
```

## Verification

Two runs with different output directories (`TZ=UTC`,
`PYTHONHASHSEED=0`) both exit 0 and produce byte-identical PNGs:

- size: 17,041 bytes, 1024x1024
- sha256: `4d2619f9e5d643963cad0357551a0f12ace077bed702fe68ff78659a07235e81`

## License

MIT — see `LICENSE`.
