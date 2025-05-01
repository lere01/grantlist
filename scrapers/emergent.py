# scrapers/emergent.py  (patched)
import asyncio, httpx
from datetime import date         # <- only the class you need
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

URL     = "https://www.mercatus.org/emergent-ventures"
HEADERS = {"User-Agent": "GrantRadarBot/0.1 (+https://github.com/lere01)"}

async def fetch_emergent() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            html_text = (await c.get(URL)).text

        if "Emergent Ventures" not in html_text:
            return []

        today = date.today().isoformat()

        grants = [
            Grant(
                id="emergent-ventures",
                name="Emergent Ventures (rolling)",
                funder="Mercatus Center",
                url=URL,
                amount_min=5_000,
                amount_max=500_000,
                currency="USD",
                region="Global",
                deadline=None,
                recurring=True,
                tags=["innovation", "research", "entrepreneurship"],
                description="Fast-turnaround grants and fellowships for ambitious ideas.",
                retrieved_at=today,
            )
        ]
        return ScrapeResult(
            name = "fetch_emergent",
            grants = grants,
            error = None,
        )
    except Exception as e:
        return ScrapeResult(
            name = "fetch_emergent",
            grants = [],
            error = str(e),
        )