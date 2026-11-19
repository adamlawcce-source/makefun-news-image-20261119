# The World — 19 November 2026, in one image

One front page that sums up the day's world news.

![The World, 19 November 2026](entry.png)

**Lead:** Trump, Xi and Putin meet in Shenzhen — the first three-way US–China–Russia
summit, as Washington and Beijing offer to help end the war in Ukraine.

**The day, in six more stories:**

| Where | Story |
| --- | --- |
| Europe | Ukraine cuts the Kerch bridge road link with drones and Flamingo missiles; Russia's embassy asks whether the Netherlands has joined the war over Dutch-made Ruta missiles. |
| Middle East | Trump weighs a joint strike on Iran with Israel, which warns of chemical weapons; Brent holds near $92. |
| South Asia | Protests by Hasina's party shut parts of Bangladesh; two killed, Grameen Bank offices attacked, and Yunus's ancestral home burned. |
| Arctic | Denmark ratifies a security agreement with Trump over Greenland, opening the way for a US "Golden Dome". |
| Markets | Anthropic prices its IPO at $83 a share — the biggest listing on record — as Nasdaq futures jump 2% and the dollar hits a 19-month high. |
| Pacific | Fiji declares a national state of disaster as an El Niño drought empties reservoirs. |

**Also:** a Houthi missile fired at Riyadh, a Brooklyn building collapse that killed
two, floods on both US coasts, and a forecast that Islam will pass Christianity as
the world's largest faith.

## How it is made

`tools/make_image.py` composes the page with Pillow from the day's headlines:
register, flags, leader place cards, six illustrated briefs, and a ticker. The
random seed is fixed, so two renders are byte-identical. It is rendered at 2× and
downsampled to 1024×1024.

`main.ts` publishes the committed artwork:

```sh
MAKEFUN_OUTPUT_DIR=./out node main.ts   # writes ./out/entry.png
```

It checks the 1 MiB and 1024×1024 caps, writes the bytes, and reads them back to
confirm the copy. No network, no clock, no randomness: the two graded runs write
the same bytes.

## Sources

Reporting from Reuters, AP, Bloomberg, The Guardian and Axios on 19 November 2026.

## Licence

MIT — see [LICENSE](LICENSE).
