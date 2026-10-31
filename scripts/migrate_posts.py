#!/usr/bin/env python3
"""Convert selected Jekyll posts into Hugo page bundles."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path


FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
IMAGE = re.compile(r"/assets/img/posts/([^/]+)/([^\s)\]]+)")
SQUARE_IMAGE = re.compile(r"!\[([^\]]*)\]\[(/assets/img/posts/[^\]]+)\]")
PROMPT = re.compile(
    r"^\s*(?:\{:\s*|:\{\s*)\.prompt-(info|warning|danger|tip)\s*\}\s*$"
)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
PRE_SHARED_KEY_VALUE = re.compile(
    r"(?im)^(\s*-\s*Pre-Shared Key\s*:\s*)\S+\s*$"
)
LEGACY_POST_URL = re.compile(
    r"(?:https?://haksuperman\.github\.io)?/posts/(?P<slug>[a-z0-9-]+)(?:\.md)?/?",
    re.I,
)
SENSITIVE_IMAGE_REPLACEMENTS = {
    "![image](/assets/img/posts/AWS/AWS02_57.png)": (
        '{{< callout type="warning" >}}\n'
        "원문 이미지에는 교육용 데이터베이스 계정 비밀번호가 표시되어 있어 공개본에서 제외했습니다.\n"
        "{{< /callout >}}"
    ),
    "![image](/assets/img/posts/Network/Network09_04.png)": (
        '{{< callout type="warning" >}}\n'
        "원문 이미지에는 교육용 네트워크 장비 계정과 비밀번호가 표시되어 있어 공개본에서 제외했습니다.\n"
        "{{< /callout >}}"
    ),
}
SENSITIVE_TEXT_REPLACEMENTS = {
    "ubuntu:hackers": "ubuntu:REDACTED_LAB_PASSWORD",
    "패스워드를 hackers로": "패스워드를 `REDACTED_LAB_PASSWORD`로",
    "-phackers": "-pREDACTED_DB_PASSWORD",
    "enable secret ciscosec": "enable secret REDACTED_LAB_SECRET",
    "username root password toor": "username root password REDACTED_LAB_PASSWORD",
    "' dkagh1. '": "`REDACTED_PERSONAL_PASSWORD`",
}


def field(front: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.*?)(?:\s+#.*)?$", front, re.M)
    return match.group(1).strip() if match else ""


def parse_list(value: str) -> list[str]:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
    return []


def quoted(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalize_date(value: str) -> str:
    value = value.strip().strip("\"'")
    match = re.match(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+([+-]\d{2})(\d{2})", value)
    if match:
        return f"{match.group(1)}T{match.group(2)}{match.group(3)}:{match.group(4)}"
    return value


def convert_prompts(body: str) -> str:
    lines = body.splitlines()
    output: list[str] = []
    for line in lines:
        match = PROMPT.match(line)
        if not match:
            output.append(line)
            continue

        start = len(output)
        while start > 0 and (output[start - 1].lstrip().startswith(">") or not output[start - 1].strip()):
            start -= 1
        quote = output[start:]
        del output[start:]
        while quote and not quote[0].strip():
            quote.pop(0)
        while quote and not quote[-1].strip():
            quote.pop()
        cleaned = [re.sub(r"^\s*>\s?", "", item) for item in quote]
        kind = "error" if match.group(1) == "danger" else match.group(1)
        output.extend([f'{{{{< callout type="{kind}" >}}}}', *cleaned, "{{< /callout >}}"])
    return "\n".join(output) + "\n"


def convert_body(body: str, legacy_links: dict[str, str]) -> str:
    for original, replacement in SENSITIVE_IMAGE_REPLACEMENTS.items():
        body = body.replace(original, replacement)
    for original, replacement in SENSITIVE_TEXT_REPLACEMENTS.items():
        body = body.replace(original, replacement)
    output: list[str] = []
    fence_marker: str | None = None
    for line in body.splitlines():
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)[0]
            if fence_marker is None:
                fence_marker = marker
            elif fence_marker == marker:
                fence_marker = None
            output.append(line)
            continue

        if fence_marker is None:
            line = re.sub(r"^# (.+)$", r"## \1", line)
            line = re.sub(r"^(#{2,6}\s+\d+)\\\.", r"\1.", line)
        output.append(line)
    converted = convert_prompts("\n".join(output) + "\n")
    converted = SQUARE_IMAGE.sub(r"![\1](\2)", converted)
    converted = PRE_SHARED_KEY_VALUE.sub(r"\1<REDACTED — 새 PSK 사용>", converted)
    converted = converted.replace("<K8s123!@#>", "<강력한 비밀번호>")
    converted = LEGACY_POST_URL.sub(
        lambda match: legacy_links.get(match.group("slug").lower(), match.group(0)),
        converted,
    )
    return converted


def migrate(
    source_root: Path,
    target_root: Path,
    item: dict[str, object],
    legacy_links: dict[str, str],
) -> dict[str, object]:
    source = source_root / str(item["source"])
    source_bytes = source.read_bytes()
    expected_hash = item.get("source_sha256")
    actual_hash = hashlib.sha256(source_bytes).hexdigest()
    if expected_hash and actual_hash != expected_hash:
        raise ValueError(f"source changed since planning: {source}")
    text = source_bytes.decode("utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"Front matter not found: {source}")

    front = match.group(1)
    body = convert_body(text[match.end():], legacy_links)
    date = normalize_date(field(front, "date"))
    tags = parse_list(field(front, "tags"))
    categories = parse_list(field(front, "categories"))
    legacy_slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", source.stem).lower()
    destination = (target_root / str(item["destination"])).resolve()
    if target_root != destination and target_root not in destination.parents:
        raise ValueError(f"destination escapes target root: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    copied_images: list[str] = []
    for category, filename in sorted(set(IMAGE.findall(body))):
        image_source = source_root / "assets" / "img" / "posts" / category / filename
        if not image_source.exists():
            raise FileNotFoundError(image_source)
        image_destination = destination.parent / filename
        shutil.copyfile(image_source, image_destination)
        image_destination.chmod(0o644)
        copied_images.append(filename)
        body = body.replace(f"/assets/img/posts/{category}/{filename}", filename)

    legacy_url = str(item.get("legacy_url") or f"/posts/{legacy_slug}/")
    if legacy_url != f"/posts/{legacy_slug}/":
        raise ValueError(f"legacy URL mismatch: {source} -> {legacy_url}")

    aliases = [legacy_url]
    canonical_url = destination_permalink(str(item["destination"]))
    if canonical_url.startswith("/series/"):
        aliases.append(canonical_url.replace("/series/", "/study/", 1))

    yaml = [
        "---",
        f'title: {quoted(str(item["title"]))}',
        f'linkTitle: {quoted(str(item["linkTitle"]))}',
        f"date: {quoted(date)}",
        f"lastmod: {quoted(date)}",
        f"aliases: [{', '.join(quoted(alias) for alias in aliases)}]",
        "tags:",
        *[f"  - {quoted(tag)}" for tag in tags],
        "categories:",
        *[f"  - {quoted(category)}" for category in categories],
    ]
    if "weight" in item:
        yaml.append(f'weight: {int(item["weight"])}')
    if item.get("sourceStatus"):
        yaml.append(f'sourceStatus: {quoted(str(item["sourceStatus"]))}')
    yaml.extend(["---", ""])
    destination.write_text("\n".join(yaml) + body, encoding="utf-8")
    return {
        "source": str(item["source"]),
        "destination": str(item["destination"]),
        "legacy_url": legacy_url,
        "title": str(item["title"]),
        "section": str(item["section"]),
        "images": len(copied_images),
    }


def write_inventory(source_root: Path, target_root: Path, migrated: list[dict[str, object]]) -> None:
    migrated_by_source = {str(item["source"]): item for item in migrated}
    inventory_path = target_root / "migration" / "inventory.csv"
    existing_by_source: dict[str, dict[str, str]] = {}
    if inventory_path.exists():
        with inventory_path.open(encoding="utf-8") as handle:
            existing_by_source = {
                str(row["source"]): row for row in csv.DictReader(handle)
            }
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source", "legacy_url", "title", "categories", "tags", "status", "destination"],
            lineterminator="\n",
        )
        writer.writeheader()
        for source in sorted(source_root.glob("_posts/**/*.md")):
            text = source.read_text(encoding="utf-8")
            match = FRONT_MATTER.match(text)
            if not match:
                continue
            front = match.group(1)
            relative = str(source.relative_to(source_root))
            slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", source.stem).lower()
            migrated_item = migrated_by_source.get(relative, {})
            existing = existing_by_source.get(relative, {})
            writer.writerow(
                {
                    "source": relative,
                    "legacy_url": f"/posts/{slug}/",
                    "title": field(front, "title").strip("\"'"),
                    "categories": " | ".join(parse_list(field(front, "categories"))),
                    "tags": " | ".join(parse_list(field(front, "tags"))),
                    "status": "migrated" if migrated_item else existing.get("status", "pending"),
                    "destination": migrated_item.get(
                        "destination", existing.get("destination", "")
                    ),
                }
            )


def destination_permalink(destination: str) -> str:
    path = Path(destination)
    if path.parts[:1] != ("content",) or path.name != "index.md":
        raise ValueError(f"unsupported destination path: {destination}")
    return "/" + "/".join(path.parts[1:-1]) + "/"


def legacy_link_map(target: Path, items: list[dict[str, object]]) -> dict[str, str]:
    links: dict[str, str] = {}

    def relref(destination: str) -> str:
        permalink = destination_permalink(destination)
        return f'{{{{< relref "{permalink}" >}}}}'

    inventory_path = target / "migration" / "inventory.csv"
    if inventory_path.exists():
        with inventory_path.open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["destination"]:
                    slug = str(row["legacy_url"]).strip("/").split("/")[-1]
                    links[slug.lower()] = relref(str(row["destination"]))
    for item in items:
        legacy_url = str(item.get("legacy_url") or "")
        if not legacy_url:
            source = Path(str(item["source"]))
            legacy_url = "/posts/" + re.sub(
                r"^\d{4}-\d{2}-\d{2}-", "", source.stem
            ).lower() + "/"
        slug = legacy_url.strip("/").split("/")[-1]
        links[slug.lower()] = relref(str(item["destination"]))
    return links


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    target = args.target.resolve()
    manifest = args.manifest or target / "migration" / "sample-posts.json"
    items = json.loads(manifest.read_text(encoding="utf-8"))
    links = legacy_link_map(target, items)
    migrated = [migrate(args.source.resolve(), target, item, links) for item in items]
    write_inventory(args.source.resolve(), target, migrated)
    print(json.dumps({"migrated": migrated, "count": len(migrated)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
