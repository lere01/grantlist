# scrapers/prototype_fund.py
import asyncio, httpx, re, html
from datetime import datetime, date
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

URL      = "https://prototypefund.de/en/"
HEADERS  = {"User-Agent": "GrantRadarBot/0.1 (+https://github.com/lere01)"}
AMT_MIN, AMT_MAX, CURRENCY = 5_000, 50_000, "EUR"

_deadline_re = re.compile(r"deadline(?: is|:)?\s+(\d{1,2}\.\d{1,2}\.\d{4})", re.I)

async def fetch_prototype() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            text = (await c.get(URL)).text

        soup = BeautifulSoup(text, "html.parser")

        # Extract headline (“Prototype Fund – Round 15”)
        h1  = soup.find("h1")
        if not h1:
            return []
        name_text = html.unescape(h1.get_text(" ", strip=True))

        # Parse next deadline
        deadline = None
        m = _deadline_re.search(text)
        if m:
            deadline = datetime.strptime(m.group(1), "%d.%m.%Y").date().isoformat()

        grants = [
            Grant(
                id="prototype-fund",
                name=name_text,
                funder="Prototype Fund (OKF-DE / BMBF)",
                url=URL,
                amount_min=AMT_MIN,
                amount_max=AMT_MAX,
                currency=CURRENCY,
                region="EU",
                deadline=deadline,
                recurring=True,
                tags=["open-source", "civic-tech", "research"],
                description="German Federal grant for OSS civic-tech; two rounds per year.",
                retrieved_at=date.today().isoformat(),
            )
        ]
        return ScrapeResult(name="fetch_prototype", grants=grants)
    except Exception as e:
        return ScrapeResult(name="fetch_prototype", grants=[], error=str(e))