import asyncio, httpx
from datetime import date
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

URL = "https://www.mozilla.org/en-US/moss/mission-partners/"
HEADERS = {"User-Agent": "GrantRadarBot/0.2 (+https://github.com/lere01)"}

async def fetch_moss() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            html_text = (await c.get(URL)).text

        if "Mission Partners" not in html_text:   # page removed?
            return []

        soup = BeautifulSoup(html_text, "html.parser")
        h1   = soup.find("h1") or soup.title
        name = h1.get_text(" ", strip=True) if h1 else "Mozilla MOSS – Mission Partners"

        grants = [
            Grant(
                id="moss-mission-partners",
                name=name,
                funder="Mozilla Foundation",
                url=URL,
                amount_min=10_000,
                amount_max=250_000,
                currency="USD",
                region="Global",
                deadline=None,           # rolling monthly
                recurring=True,
                tags=["open-source", "internet", "privacy"],
                description="Grants ($10k–$250k) for open-source projects that advance Mozilla’s mission. Rolling review.",
                retrieved_at=date.today().isoformat(),
            )
        ]
        return ScrapeResult(
            name="fetch_moss",
            grants=grants,
        )
    except Exception as e:
        return ScrapeResult(
            name="fetch_moss",
            grants=[],
            error=str(e),
        )