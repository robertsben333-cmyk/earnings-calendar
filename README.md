# earnings-calendar

US earnings calendar, refreshed daily by GitHub Actions.

**Canonical URL (for ChatGPT and external agents):**

```
https://robertsben333-cmyk.github.io/earnings-calendar/earnings.json
```

Served by GitHub Pages from the `main` branch. Pages rebuilds automatically
within ~30–60 seconds after every push, so the daily refresh propagates
without any extra wiring. Pages also runs under the `github.io` domain
which is on most corporate / agent allowlists, unlike `raw.githubusercontent.com`
or third-party CDNs.

**Fallback URLs** (use if the Pages URL is ever unreachable):

```
https://cdn.jsdelivr.net/gh/robertsben333-cmyk/earnings-calendar@main/earnings.json
https://raw.githack.com/robertsben333-cmyk/earnings-calendar/main/earnings.json
https://raw.githubusercontent.com/robertsben333-cmyk/earnings-calendar/main/earnings.json
```

## What it contains

For each refresh:

- `reference_date` — the day used as "today"
- `next_trading_day` — the next NYSE trading day after `reference_date`
- `summary.after_close_today` — companies reporting **after the close** on `reference_date`
- `summary.before_open_next_trading_day` — companies reporting **before the open** on `next_trading_day`
- `after_close` / `before_open` — full Nasdaq rows (market cap, EPS forecast, fiscal quarter, prior year EPS, etc.)
- `generated_at_utc` — when this file was produced

Weekends and US holidays are handled — `next_trading_day` skips them.

## Source

Public Nasdaq endpoint, no API key:
`https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD`

## Schedule

Daily at 11:00 UTC (≈ 07:00 ET, before US market open).
Also triggerable manually via the Actions tab.
