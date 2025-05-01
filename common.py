from datetime import date
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class Grant(BaseModel):
    id: str                     # unique slug: "<source>-<slug>"
    name: str
    funder: str
    url:  HttpUrl
    amount_min: float
    amount_max: float
    currency: str = Field(..., pattern=r"^[A-Z]{3}$")   # ISO 4217
    region: str                 # "Global", "EU", "US-CA", …
    deadline: Optional[str]     # ISO-date "2025-06-30" or None
    recurring: bool
    tags: List[str]             # ["open-source", "hardware"]
    description: Optional[str]  # one-sentence summary
    retrieved_at: str           # ISO-date of scrape (today)

    model_config = ConfigDict(frozen=True) # make immutable



@dataclass(frozen=True)
class ScrapeResult:
    name: str                # e.g. "fetch_moss"
    grants: List[Grant]
    error: Optional[str] = None  