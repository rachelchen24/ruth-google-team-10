"""Build the seed dataset.

  py -m scrapers.run                       # all sources -> data/listings.json
  py -m scrapers.run --sources mlh devpost # structured sources only, no LLM key needed
  py -m scrapers.run --limit 20            # cap LLM-extracted records per source (cheap test)
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

from .adapters import careeronestop, devpost, mlh, pages, pathways
from .dedupe import dedupe, drop_expired
from .geo import fill_coords
from .schema import Listing

DATA = Path(__file__).resolve().parent.parent / "data"
STRUCTURED = {"mlh": mlh.fetch_listings, "devpost": devpost.fetch_listings}
RAW = {"pathways": pathways.fetch_raw, "careeronestop": careeronestop.fetch_raw, "pages": pages.fetch_raw}
NO_LLM = {"pathways": pathways.to_listing}  # fallback parsers when there's no LLM key


def load_manual() -> list[Listing]:
    path = DATA / "manual_listings.json"
    if not path.exists():
        return []
    return [Listing(**d).finalize() for d in json.loads(path.read_text(encoding="utf-8"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="*", default=[*STRUCTURED, *RAW, "manual"])
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(DATA / "listings.json"))
    args = ap.parse_args()

    listings: list[Listing] = []
    for name in args.sources:
        if name in STRUCTURED:
            got = STRUCTURED[name]()
        elif name in RAW:
            raws = RAW[name]()[: args.limit]
            (DATA / "raw").mkdir(parents=True, exist_ok=True)
            (DATA / "raw" / f"{name}.jsonl").write_text(
                "\n".join(r.model_dump_json() for r in raws), encoding="utf-8")
            if os.environ.get("LLM_API_KEY"):
                from .extract import extract  # imported lazily so no-LLM runs don't need the SDK
                got = [l for r in raws for l in extract(r)]
            elif name in NO_LLM:
                got = [NO_LLM[name](r) for r in raws]
            else:
                print(f"{name}: no LLM_API_KEY, skipping extraction")
                got = []
        elif name == "manual":
            got = load_manual()
        else:
            raise SystemExit(f"unknown source {name}")
        print(f"{name}: {len(got)}")
        listings += got

    final = [fill_coords(l) for l in dedupe(drop_expired(listings))]
    Path(args.out).write_text(
        json.dumps([l.model_dump(mode="json") for l in final], indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(final)} listings -> {args.out}", dict(Counter(l.kind for l in final)))


if __name__ == "__main__":
    main()
