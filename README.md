# earnings-calendar

US earnings calendar, refreshed daily by GitHub Actions.

**Always-fresh URL (use this for ChatGPT / external agents):**

```
https://cdn.jsdelivr.net/gh/robertsben333-cmyk/earnings-calendar@main/earnings.json
```

Mirror of the raw GitHub file via jsDelivr — picked because some agent platforms
(ChatGPT included) block `raw.githubusercontent.com` due to its sandbox CSP.
The workflow purges jsDelivr's edge cache after each refresh so propagation
is near-instant.

**Direct raw URL** (works for most clients, blocked by some agents):

```
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
