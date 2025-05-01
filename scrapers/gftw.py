import asyncio, httpx, re, calendar
from datetime import date
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

URL = "https://grantfortheweb.org/financial-services"
HEADERS = {"User-Agent": "GrantRadarBot/0.2 (+https://github.com/lere01)"}
AMT_MIN, AMT_MAX, CURRENCY = 25_000, 250_000, "USD"

_next_cycle_re = re.compile(r"next cycle will open in (\w+)\s(\d{4})", re.I)

async def fetch_gftw() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            text = (await c.get(URL)).text

        if "Financial Services" not in text:
            return []

        # Parse “next cycle will open in July 2025”
        m = _next_cycle_re.search(text)
        deadline = None
        if m:
            month_name, year = m.groups()
            try:
                month_num = list(calendar.month_name).index(month_name.capitalize())
                deadline = f"{year}-{month_num:02d}-01"   # pseudo‑deadline for sorting
            except ValueError:
                pass  # leave as None if month name unrecognised

        grants = [
            Grant(
                id="interledger-financial-services",
                name="Interledger Foundation – Financial Services Grants",
                funder="Interledger Foundation",
                url=URL,
                amount_min=AMT_MIN,
                amount_max=AMT_MAX,
                currency=CURRENCY,
                region="Global",
                deadline=deadline,
                recurring=True,
                tags=["payments", "open-standards", "financial-inclusion"],
                description="Inclusive-payments grants ($25k–$250k). Next cycle text scraped from page.",
                retrieved_at=date.today().isoformat(),
            )
        ]

        return ScrapeResult(
            name="fetch_gftw",
            grants=grants,
            error=None
        )
    except Exception as e:
        return ScrapeResult(
            name="fetch_gftw",
            grants=[],
            error=str(e)
        )