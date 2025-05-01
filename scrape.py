import asyncio, json, datetime
from pathlib import Path
from typing import Any
from scrapers import SCRAPERS
from common   import ScrapeResult, Grant

OUT = Path("data/grants.json")
STATUS_OUT = Path("data/scraper_status.json")

async def run_all():
    # Launch all scrapers concurrently
    tasks = [s() for s in SCRAPERS]
    results: list[ScrapeResult] = await asyncio.gather(*tasks)

    # ---------- 1️⃣  Write combined grants.json ----------
    grants: list[Grant] = []
    for res in results:
        # New scrapers return ScrapeResult, legacy ones return List[Grant]
        if isinstance(res, ScrapeResult):
            grants.extend(res.grants)
        elif isinstance(res, list):
            grants.extend(res)
        else:
            print(f"⚠️ Unexpected return type from scraper: {type(res)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps([g.model_dump(mode="json") for g in grants], indent=2, ensure_ascii=False)
    )
    print(f"✅ wrote {len(grants)} grants → {OUT}")

    # ---------- 2️⃣  Write scraper_status.json ----------
    status_payload = []
    for fn, res in zip(SCRAPERS, results):
        entry: dict[str, Any]
        if isinstance(res, ScrapeResult):
            entry = {
                "name": res.name,
                "n_grants": len(res.grants),
                "error": res.error,
            }
        else:  # legacy list
            entry = {
                "name": fn.__name__,
                "n_grants": len(res) if isinstance(res, list) else 0,
                "error": None,
            }
        entry["retrieved_at"] = datetime.datetime.utcnow().isoformat(timespec="seconds")
        status_payload.append(entry)
    STATUS_OUT.write_text(json.dumps(status_payload, indent=2, ensure_ascii=False))
    print(f"📋 wrote scraper status for {len(results)} scrapers → {STATUS_OUT}")

if __name__ == "__main__":
    asyncio.run(run_all())