# scrapers/nlnet.py
import re, asyncio, httpx, html
from datetime import datetime, date
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

BASE = "https://nlnet.nl"
URL  = f"{BASE}/propose/"
HEADERS = {
    "User-Agent": "GrantRadarBot/0.1 (+https://github.com/lere01; contact=aduralereo@icloud.com)"
}

amount_min = 5_000
amount_max = 50_000
currency   = "EUR"
tags       = ["open-source", "internet", "R&D"]

deadline_re = re.compile(r"Next deadline:\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})", re.I)
href_re     = re.compile(r"^/.*")                 # relative link

async def fetch_nlnet() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            html_text = (await c.get(URL)).text

        soup = BeautifulSoup(html_text, "html.parser")

        # 1️⃣  Extract next deadline (single date for all NLnet calls)
        raw_deadline = None
        h2 = soup.find("h2", string=deadline_re)
        if h2:
            m = deadline_re.search(h2.get_text(" ", strip=True))
            if m:
                raw_deadline = datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()

        # 2️⃣  Find the bullet list under “Currently open for proposals:”
        open_calls_header = soup.find(string=re.compile("Currently open for proposals", re.I))
        if not open_calls_header:
            return []                    # layout changed? fail gracefully

        ul = open_calls_header.find_next("ul")
        calls = ul.find_all("a", href=href_re) if ul else []

        grants = []
        today  = date.today().isoformat()

        for a in calls:
            name_text = html.unescape(a.get_text(" ", strip=True))
            href      = a["href"]
            full_url  = href if href.startswith("http") else f"{BASE}{href}"
            slug      = re.sub(r"[^a-z0-9]+", "-", name_text.lower()).strip("-")

            grants.append(
                Grant(
                    id          = f"nlnet-{slug}",
                    name        = f"NLnet – {name_text}",
                    funder      = "NLnet Foundation",
                    url         = full_url,
                    amount_min  = amount_min,
                    amount_max  = amount_max,
                    currency    = currency,
                    region      = "EU",
                    deadline    = raw_deadline,
                    recurring   = True,                   # rolling calls until 2027
                    tags        = tags,
                    description = (
                        "Small and medium-size R&D grants (€5 k – €50 k) "
                        "with support services via NGI Zero."
                    ),
                    retrieved_at= today,
                )
            )

        return ScrapeResult(
            name="fetch_nlnet",
            grants=grants
        )
    except Exception as e:
        return ScrapeResult(
            name="fetch_nlnet",
            grants=[],
            error=str(e)
        )