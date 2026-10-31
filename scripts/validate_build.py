#!/usr/bin/env python3
"""Validate the generated staging site without external dependencies."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
BASE_PATH = "/"
REFERENCE = re.compile(r'''(?:href|src)=["']([^"']+)["']''')
REDACTED_IMAGE_COUNTS = {
    "_posts/AWS/2024-06-09-AWS02.md": 1,
    "_posts/Network/2024-01-01-Network09.md": 1,
}


def local_target(html: Path, raw_url: str) -> Path | None:
    if raw_url.startswith(("#", "mailto:", "tel:", "data:", "javascript:")):
        return None
    parts = urlsplit(raw_url)
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    if not path:
        return None
    if path.startswith(BASE_PATH):
        candidate = PUBLIC / path.removeprefix(BASE_PATH)
    elif path.startswith("/"):
        return None
    else:
        candidate = html.parent / path
    if path.endswith("/"):
        candidate /= "index.html"
    elif not candidate.suffix and candidate.is_dir():
        candidate /= "index.html"
    return candidate


def main() -> int:
    errors: list[str] = []
    with (ROOT / "migration" / "inventory.csv").open(encoding="utf-8") as handle:
        inventory = list(csv.DictReader(handle))
    sample_manifest = json.loads(
        (ROOT / "migration" / "sample-posts.json").read_text(encoding="utf-8")
    )
    ready_manifest = json.loads(
        (ROOT / "migration" / "ready-docs.json").read_text(encoding="utf-8")
    )
    series_manifest = json.loads(
        (ROOT / "migration" / "series-posts.json").read_text(encoding="utf-8")
    )
    manifests_by_source = {
        item["source"]: item
        for item in [*sample_manifest, *ready_manifest, *series_manifest]
    }
    planned_by_source = {
        item["source"]: item
        for item in json.loads(
            (ROOT / "migration" / "full-plan.json").read_text(encoding="utf-8")
        )["items"]
    }
    migrated_inventory = {
        row["source"]: row
        for row in inventory
        if row["status"] in {"sample-migrated", "migrated"}
    }

    if len(inventory) != 132:
        errors.append(f"expected 132 inventory rows, found {len(inventory)}")
    if migrated_inventory.keys() != manifests_by_source.keys():
        errors.append("migrated inventory and manifests do not contain the same sources")
    destinations = [str(item["destination"]) for item in manifests_by_source.values()]
    if len(destinations) != len(set(destinations)):
        errors.append("migration manifests contain duplicate destinations")

    for item in manifests_by_source.values():
        destination = ROOT / item["destination"]
        if not destination.exists():
            errors.append(f"missing migrated page: {destination.relative_to(ROOT)}")
            continue
        body = destination.read_text(encoding="utf-8")
        if "/assets/img/posts/" in body:
            errors.append(f"legacy image reference remains: {destination.relative_to(ROOT)}")
        if re.search(r"(?:\{:\s*|:\{\s*)\.prompt-", body):
            errors.append(f"legacy prompt syntax remains: {destination.relative_to(ROOT)}")
        if re.search(
            r"\]\((?:https?://haksuperman\.github\.io)?/posts/", body
        ):
            errors.append(f"legacy internal link remains: {destination.relative_to(ROOT)}")
        if re.search(r"!\[[^]]*\]\[/assets/img/posts/", body):
            errors.append(f"legacy square image syntax remains: {destination.relative_to(ROOT)}")
        exposed_psk = re.search(
            r"(?im)^\s*-\s*Pre-Shared Key\s*:\s*(?!<REDACTED)[^\s<].+$", body
        )
        if exposed_psk:
            errors.append(f"unredacted pre-shared key remains: {destination.relative_to(ROOT)}")
        if re.search(r"(?i)hackers|ciscosec|\btoor\b|dkagh1", body):
            errors.append(f"known training credential remains: {destination.relative_to(ROOT)}")
        if "AWS02_57.png" in body or "Network09_04.png" in body:
            errors.append(f"credential-bearing screenshot remains: {destination.relative_to(ROOT)}")
        inventory_destination = migrated_inventory.get(item["source"], {}).get("destination")
        if inventory_destination != item["destination"]:
            errors.append(f"inventory destination mismatch: {item['source']}")
        expected_images = int(planned_by_source[item["source"]]["image_reference_count"])
        expected_images -= REDACTED_IMAGE_COUNTS.get(item["source"], 0)
        copied_images = len(
            [path for path in destination.parent.iterdir() if path.name != "index.md"]
        )
        if copied_images != expected_images:
            errors.append(
                f"image count mismatch: {item['source']} "
                f"expected {expected_images}, found {copied_images}"
            )

    for html in PUBLIC.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        for raw_url in REFERENCE.findall(text):
            target = local_target(html, raw_url)
            if target is not None and not target.exists():
                errors.append(
                    f"broken local reference: {html.relative_to(PUBLIC)} -> {raw_url}"
                )

    aliases = list((PUBLIC / "posts").glob("*/index.html"))
    if len(aliases) != len(manifests_by_source):
        errors.append(
            f"expected {len(manifests_by_source)} legacy aliases, found {len(aliases)}"
        )

    series_sources = list((ROOT / "content" / "series").rglob("*.md"))
    series_aliases: list[Path] = []
    for source in series_sources:
        relative = source.relative_to(ROOT / "content" / "series")
        page_path = relative.parent
        canonical = PUBLIC / "series" / page_path / "index.html"
        legacy_alias = PUBLIC / "study" / page_path / "index.html"
        if not canonical.exists():
            errors.append(f"missing Series page: {canonical.relative_to(PUBLIC)}")
        if not legacy_alias.exists():
            errors.append(
                f"missing legacy Study alias: {legacy_alias.relative_to(PUBLIC)}"
            )
        series_aliases.append(legacy_alias)

    if errors:
        print("\n".join(errors))
        return 1

    print(
        json.dumps(
            {
                "inventory": len(inventory),
                "migrated_posts": len(manifests_by_source),
                "legacy_aliases": len(aliases),
                "series_legacy_aliases": len(series_aliases),
                "html_pages_checked": len(list(PUBLIC.rglob("*.html"))),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
