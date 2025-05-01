import asyncio, httpx, re, html
from datetime import date
from bs4 import BeautifulSoup
from common import Grant, ScrapeResult

URL = "https://openai.com/form/researcher-access-program/"
HEADERS = {
    "User-Agent": "GrantRadarBot/0.2 (+https://github.com/lere01)"  # ASCII only
}

async def fetch_openai_credit() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            html_text = (await c.get(URL, follow_redirects=True)).text

        soup = BeautifulSoup(html_text, "html.parser")
        h1   = soup.find("h1")
        if not h1:                     # layout break → fail gracefully
            return []

        name = html.unescape(h1.get_text(" ", strip=True))
        # Quarterly cycles — list months present in page for info
        m    = re.search(r"(\w+,\s\w+,\s\w+).+reviewed once every 3 months", html_text, re.I | re.S)
        # They don’t publish a hard deadline — keep None
        deadline = None

        grants = [
            Grant(
                id="openai-api-credit",
                name=name,
                funder="OpenAI",
                url=URL,
                amount_min=0,            # API credit
                amount_max=0,
                currency="USD",
                region="Global",
                deadline=deadline,
                recurring=True,
                tags=["ai", "research", "api-credit"],
                description="Up to $1 000 in OpenAI API credits (reviewed quarterly).",
                retrieved_at=date.today().isoformat(),
            )
        ]
        return ScrapeResult(
            name="fetch_openai_credit",
            grants=grants,
        )
    except Exception as e:
        return ScrapeResult(
            name="fetch_openai_credit",
            grants=[],
            error=str(e),
        )