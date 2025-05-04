import asyncio
import json
import datetime
from pathlib import Path
from typing import Any
from scrapers import SCRAPERS
from common import ScrapeResult, Grant

OUT = Path("data/grants.json")
STATUS_OUT = Path("data/scraper_status.json")

async def run_all():
    results: list[ScrapeResult] = []

    # Wrap each scraper to add timing and error capture
    async def run_scraper(fn):
        retrieved_at = datetime.datetime.utcnow().isoformat(timespec="seconds")
        try:
            res = await fn()

            if isinstance(res, ScrapeResult):
                # Update retrieved_at in-place
                res.retrieved_at = retrieved_at
                return res
            elif isinstance(res, list):
                return ScrapeResult(
                    name=fn.__name__,
                    grants=res,
                    error=None,
                    retrieved_at=retrieved_at,
                )
            else:
                print(f"⚠️ Unexpected return type from {fn.__name__}: {type(res)}")
                return ScrapeResult(
                    name=fn.__name__,
                    grants=[],
                    error="Invalid return type",
                    retrieved_at=retrieved_at,
                )
        except Exception as e:
            return ScrapeResult(
                name=fn.__name__,
                grants=[],
                error=str(e),
                retrieved_at=retrieved_at,
            )

    # Run all scrapers concurrently
    tasks = [run_scraper(fn) for fn in SCRAPERS]
    results = await asyncio.gather(*tasks)

    # ---------- 1️⃣ Write combined grants.json ----------
    all_grants: list[Grant] = []
    for res in results:
        all_grants.extend(res.grants)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps([g.model_dump(mode="json") for g in all_grants], indent=2, ensure_ascii=False)
    )
    print(f"✅ wrote {len(all_grants)} grants → {OUT}")

    # ---------- 2️⃣ Write scraper_status.json ----------
    status_payload = [
        {
            "name": res.name,
            "n_grants": len(res.grants),
            "error": res.error,
            "retrieved_at": res.retrieved_at,
        }
        for res in results
    ]
    STATUS_OUT.write_text(json.dumps(status_payload, indent=2, ensure_ascii=False))
    print(f"📋 wrote scraper status for {len(results)} scrapers → {STATUS_OUT}")

if __name__ == "__main__":
    asyncio.run(run_all())