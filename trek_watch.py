#!/usr/bin/env python3
import re, json, os, requests, pandas as pd, smtplib, ssl, pathlib
from email.message import EmailMessage
from datetime import datetime, timezone

URL = ("https://www.trekbikes.com/us/en_US/pre-owned-bikes/"
       "pre-owned-road-bikes/c/RBR200/"
       "?pageSize=72&sort=price-asc"
       "&q=%3Aprice-asc%3AsizeFrameSummarized%3AEnumSizeFrameSummarized004"
       "%3AfacetBrakes%3AfacetBrake4")
HEADERS  = {"User-Agent": "Mozilla/5.0"}
SAVEFILE = pathlib.Path(__file__).with_name("trek_seen.json")

# ── scrape ────────────────────────────────────────────────────────────
html   = requests.get(URL, headers=HEADERS, timeout=30).text
records = json.loads(re.search(r'"impressions"\s*:\s*(\[[^\]]+\])', html).group(1))
df = pd.DataFrame(records)
df["price"] = pd.to_numeric(df["price"], errors="coerce")

mask = (
    df["name"].str.contains(r"(?:\b58\s?cm\b|\bLarge\b)", case=False, regex=True) &
    ~df["name"].str.contains(r"Medium/?Large", case=False, regex=True) &
    ~df["name"].str.contains(r"Domane\+",   case=False, regex=True) &
    (df["price"] < 3499)
)
current = df.loc[mask, ["id", "name", "price"]].rename(
    columns={"id": "SKU", "name": "Bike", "price": "Price"}
)

# ── diff with previous run ────────────────────────────────────────────
seen = set(json.loads(SAVEFILE.read_text())) if SAVEFILE.exists() else set()
now  = set(current["SKU"])
new  = now - seen

if new:
    rows = current[current["SKU"].isin(new)]
    lines = [f"New Trek listings – {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}"]
    for _, r in rows.iterrows():
        lines.append(f"• {r.Bike} — ${r.Price:,.2f} (SKU {r.SKU})")
    lines.append("\n" + URL)

    msg = EmailMessage()
    msg["Subject"] = f"[Trek Watch] {len(new)} new bike(s)"
    msg["From"]    = os.environ["MAIL_FROM"]
    msg["To"]      = os.environ["MAIL_TO"]
    msg.set_content("\n".join(lines))

    host  = "smtp.gmail.com"
    port  = 465
    user = (os.getenv("SMTP_USER") or "").strip()
    pwd  = (os.getenv("SMTP_PASS") or "").strip()



    with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context()) as s:
        s.login(user, pwd)
        s.send_message(msg)

# ── save state for next time ──────────────────────────────────────────
SAVEFILE.write_text(json.dumps(sorted(now)))
