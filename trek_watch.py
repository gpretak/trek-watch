#!/usr/bin/env python3
import os, re, json, pathlib, ssl
from datetime import datetime, timezone
from email.message import EmailMessage

import pandas as pd
import requests, smtplib

# ── config ────────────────────────────────────────────────────────────
LISTINGS = [
    {
        "name": "Road",
        "url": (
            "https://www.trekbikes.com/us/en_US/pre-owned-bikes/"
            "pre-owned-road-bikes/c/RBR200/"
            "?pageSize=72&sort=price-asc"
            "&q=%3Aprice-asc%3AsizeFrameSummarized%3AEnumSizeFrameSummarized004"
            "%3AfacetBrakes%3AfacetBrake4"
        ),
        "price_cap": 2500,
    },
    {
        "name": "Mountain",
        "url": (
            "https://www.trekbikes.com/us/en_US/pre-owned-bikes/"
            "pre-owned-mountain-bikes/c/RBR300/"
            "?pageSize=72&sort=price-asc"
            "&q=%3Arelevance%3AsizeFrameSummarized%3AEnumSizeFrameSummarized004"
            "%3AfacetBrakes%3AfacetBrake4"
        ),
        "price_cap": 2000,
    },
]

HEADERS  = {"User-Agent": "Mozilla/5.0"}
SAVEFILE = pathlib.Path(__file__).with_name("trek_seen.json")

SIZE_RE        = re.compile(r"(?:\b58\s?cm\b|\bLarge\b)", re.I)
EXCLUDE_MODELS = re.compile(r"(Medium/?Large|Domane\+)", re.I)
JSON_RE        = re.compile(r'"impressions"\s*:\s*(\[[^\]]+\])')

# ── helper -------------------------------------------------------------
def fetch_listing(item: dict) -> pd.DataFrame:
    html = requests.get(item["url"], headers=HEADERS, timeout=30).text
    records = json.loads(JSON_RE.search(html).group(1))
    df = pd.DataFrame(records)
    df["price"] = pd.to_numeric(df["price"], errors="coerce")

    mask = (
        df["name"].str.contains(SIZE_RE) &
        ~df["name"].str.contains(EXCLUDE_MODELS) &
        (df["price"] < item["price_cap"])
    )
    return (
        df.loc[mask, ["id", "name", "price"]]
          .rename(columns={"id": "SKU", "name": "Bike", "price": "Price"})
          .assign(Category=item["name"])
    )

# ── aggregate all categories ──────────────────────────────────────────
frames = [fetch_listing(item) for item in LISTINGS]
current = pd.concat(frames, ignore_index=True)

# ── diff with previous run ────────────────────────────────────────────
seen = set(json.loads(SAVEFILE.read_text())) if SAVEFILE.exists() else set()
now  = set(current["SKU"])
new  = now - seen

if new:
    rows = current[current["SKU"].isin(new)]
    lines = [f"New Trek listings – {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}"]
    for _, r in rows.iterrows():
        lines.append(
            f"• {r.Bike} — ${r.Price:,.0f} ({r.Category}, SKU {r.SKU})"
        )
    # include the source URLs at the end
    lines.extend(["", "Sources:"] + [f"- {item['url']}" for item in LISTINGS])

    msg = EmailMessage()
    msg["Subject"] = f"[Trek Watch] {len(new)} new bike(s)"
    msg["From"]    = os.environ["MAIL_FROM"]
    msg["To"]      = os.environ["MAIL_TO"]
    msg.set_content("\n".join(lines))

    host = "smtp.gmail.com"
    port = 465
    user = (os.getenv("SMTP_USER") or "").strip()
    pwd  = (os.getenv("SMTP_PASS") or "").strip()

    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as s:
        s.login(user, pwd)
        s.send_message(msg)

# ── save state for next time ──────────────────────────────────────────
SAVEFILE.write_text(json.dumps(sorted(now)))
