#!/usr/bin/env python3
"""
Refresh earnings.json for the next two US market sessions:
  - after close today
  - before open on the next trading day

Source: Nasdaq public earnings calendar (no API key required).
Writes earnings.json in the repo root with a summary block that is
easy for an LLM agent to read.
"""

import calendar
import json
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

OUT_FILE = Path(__file__).parent / "earnings.json"


# ── NYSE holiday logic ───────────────────────────────────────────────────────

def _easter(year):
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo = (h + l - 7 * m + 114) // 31
    dy = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, mo, dy)


def _observed(d):
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def _nth_weekday(year, month, n, wd):
    if n > 0:
        first = date(year, month, 1)
        offset = (wd - first.weekday()) % 7
        return first + timedelta(days=offset + 7 * (n - 1))
    last_day = calendar.monthrange(year, month)[1]
    last = date(year, month, last_day)
    offset = (last.weekday() - wd) % 7
    return last - timedelta(days=offset)


def nyse_holidays(year):
    MON, THU = 0, 3
    h = {
        _observed(date(year, 1, 1)),
        _nth_weekday(year, 1, 3, MON),
        _nth_weekday(year, 2, 3, MON),
        _easter(year) - timedelta(days=2),
        _nth_weekday(year, 5, -1, MON),
        _observed(date(year, 7, 4)),
        _nth_weekday(year, 9, 1, MON),
        _nth_weekday(year, 11, 4, THU),
        _observed(date(year, 12, 25)),
    }
    if year >= 2022:
        h.add(_observed(date(year, 6, 19)))
    return h


def next_trading_day(today):
    d = today + timedelta(days=1)
    holidays = nyse_holidays(d.year)
    while True:
        if d.month == 1 and d.day <= 2:
            holidays = nyse_holidays(d.year)
        if d.weekday() < 5 and d not in holidays:
            return d
        d += timedelta(days=1)


# ── Nasdaq fetch ─────────────────────────────────────────────────────────────

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nasdaq.com/",
}


def fetch_earnings(d):
    url = "https://api.nasdaq.com/api/calendar/earnings"
    params = {"date": d.strftime("%Y-%m-%d"), "offset": 0, "size": 500}
    r = requests.get(url, params=params, headers=_HEADERS, timeout=20)
    r.raise_for_status()
    return (r.json().get("data") or {}).get("rows") or []


# ── Main ─────────────────────────────────────────────────────────────────────

def slim(rows):
    return [
        {
            "symbol": r.get("symbol"),
            "name": r.get("name"),
            "marketCap": r.get("marketCap"),
            "epsForecast": r.get("epsForecast"),
            "fiscalQuarterEnding": r.get("fiscalQuarterEnding"),
        }
        for r in rows
    ]


def main():
    override = os.environ.get("EARNINGS_REFERENCE_DATE", "").strip()
    if override:
        today = date.fromisoformat(override)
        print(f"Reference date overridden via EARNINGS_REFERENCE_DATE -> {today}")
    else:
        today = datetime.now(timezone.utc).date()
    next_td = next_trading_day(today)

    today_rows = fetch_earnings(today)
    next_rows = fetch_earnings(next_td)

    after_close = [r for r in today_rows if r.get("time") == "time-after-hours"]
    before_open = [r for r in next_rows if r.get("time") == "time-pre-market"]

    out = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "https://api.nasdaq.com/api/calendar/earnings",
        "reference_date": today.isoformat(),
        "next_trading_day": next_td.isoformat(),
        "summary": {
            "after_close_today": {
                "date": today.isoformat(),
                "count": len(after_close),
                "tickers": [r["symbol"] for r in after_close],
                "rows": slim(after_close),
            },
            "before_open_next_trading_day": {
                "date": next_td.isoformat(),
                "count": len(before_open),
                "tickers": [r["symbol"] for r in before_open],
                "rows": slim(before_open),
            },
        },
        "after_close": after_close,
        "before_open": before_open,
    }

    OUT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_FILE}")
    print(f"  after_close ({today}): {len(after_close)} -> {[r['symbol'] for r in after_close]}")
    print(f"  before_open ({next_td}): {len(before_open)} -> {[r['symbol'] for r in before_open]}")


if __name__ == "__main__":
    main()
