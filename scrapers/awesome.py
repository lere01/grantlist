# scrapers/awesome.py  – revision 3
import httpx, asyncio, re, html
from bs4 import BeautifulSoup
from datetime import date
from common import Grant, ScrapeResult

BASE = "https://www.awesomefoundation.org"
URL  = f"{BASE}/en/chapters"
HEADERS = {
    # plain hyphen instead of “–”
    "User-Agent": (
        "GrantRadarBot/0.1 (contact=aduralereo@icloud.com; "
        "purpose=grant-scrape)"
    )
}

slug_re = re.compile(r"^/en/chapters/([a-z0-9\-]+)$", re.I)

async def fetch_awesome() -> list[Grant]:
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as c:
            html_text = (await c.get(URL)).text

        soup   = BeautifulSoup(html_text, "html.parser")  # std-lib parser is fine
        grants = []

        for a in soup.find_all("a", href=slug_re):
            slug        = slug_re.match(a["href"]).group(1)
            # Strip HTML entities / newlines from “Berlin, Germany”
            name_text   = html.unescape(a.get_text(" ", strip=True))
            region_text = name_text.split(",")[-1].strip() if "," in name_text else "Global"

            grants.append(
                Grant(
                    id          = f"awesome-{slug}",
                    name        = f"Awesome Foundation – {name_text}",
                    funder      = "Awesome Foundation",
                    url         = f"{BASE}{a['href']}",
                    amount_min  = 1000,
                    amount_max  = 1000,
                    currency    = "USD",          # all chapters still award $/€1 000
                    region      = region_text,
                    deadline    = None,           # rolling
                    recurring   = True,
                    tags        = ["community", "general"],
                    description = "Micro-grant of $1 000; rolling monthly.",
                    retrieved_at= date.today().isoformat(),
                )
            )

        return ScrapeResult(
            name = "fetch_awesome",
            grants = grants,
            error = None,
        )
    except Exception as e:
        return [
            ScrapeResult(
                name="fetch_awesome",
                grants=[],
                error=str(e),
            )
        ]