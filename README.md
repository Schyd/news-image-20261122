# Today in the World — 22 November 2026

One image that sums up the world news of **Sunday, 22 November 2026**,
drawn by `main.py` (Python 3, standard library only) as a classic
cream-paper newspaper front page.

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/Schyd/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/Schyd/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

- Bounty: https://make.fun/bounty/news-image-20261122
- Entry: `main.py` writes `entry.png` (1024x1024, under 1 MiB) into
  `$MAKEFUN_OUTPUT_DIR` (default `out/`). It runs offline, is fully
  deterministic (two runs produce byte-identical output), and only
  creates the output directory.

## What is on the page

- **50 stories in three layers**: 4 illustrated leads, 10 pictured
  stories, 36 briefs in "ALSO ON SUNDAY 22 NOVEMBER" — every story
  numbered 1–50, each with a source and a confidence tag.
- **Region strip**: ASIA 11, MIDDLE EAST 7, EUROPE 10, AMERICAS 2,
  AFRICA 13, OCEANIA 4, GLOBAL 3 — 50 in total, across 9 fields.
- **THE DAY IN UTC**: seven moments from the day, 00 to 24 UTC.
- **WHERE IT HAPPENED**: a numbered world map (pins 1–14, dots 15–52).
- **DATE CHECK**: a two-way check — what was left out as earlier news,
  and what has not happened yet.
- **HOW SURE**: CONFIRMED = 2+ independent media, OFFICIAL = an
  official body, CLAIM = one party only, FORECAST = prediction.
- **THE DAY IN NUMBERS**: 723 seats in Hong Kong, 176 runs, 4.1
  magnitude, 152 homes, 856 candidates, 10,000 forest staff.

## Sources

Reuters, AP, AFP, BBC, ANI, NCS, WAM, USGS, Peru's Geophysical
Institute, China Daily, Cricbuzz and the day's wire digests. Disputed
or one-sided reports are tagged CLAIM, never presented as settled fact.

## Build notes

The drawing uses only the Python standard library: a hand-made 5x7
bitmap font and a hand-written PNG encoder. No network, no fonts, no
randomness — the same command always writes the same bytes.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.

