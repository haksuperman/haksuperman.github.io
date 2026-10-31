#!/usr/bin/env python3
"""Build a reviewable, reproducible migration plan for every legacy post."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_REFERENCE = re.compile(r"/assets/img/posts/[^/\s)\]]+/[^\s)\]]+")
LEGACY_POST_LINK = re.compile(
    r"https?://haksuperman\.github\.io/posts/[^\s)\]\"']+"
    r"|(?<!/assets/img)/posts/[^\s)\]\"']+"
)
POST_CODE = re.compile(r"(?P<group>[A-Za-z]+)(?P<number>\d+)$")
BRACKET_PREFIX = re.compile(r"^\[[^\]]+\]\s*")

DOC_THEORY = "Theory & Reference"
DOC_COMMAND = "Command & Tool"
DOC_GUIDE = "Guide & Lab"
DOC_ISSUE = "Issue & Troubleshooting"
ALLOWED_DOC_SECTIONS = {DOC_THEORY, DOC_COMMAND, DOC_GUIDE, DOC_ISSUE}

STUDY_SPECS = [
    {
        "group": "AWS",
        "start": 2,
        "end": 2,
        "slug": "aws-technical-essentials",
        "name": "AWS Technical Essentials Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "AWS",
        "start": 4,
        "end": 41,
        "slug": "aws-security",
        "name": "AWS Security Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "Kubernetes",
        "start": 1,
        "end": 4,
        "slug": "kubernetes-cluster",
        "name": "Kubernetes Cluster Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "Linux",
        "start": 1,
        "end": 5,
        "slug": "linux-fundamentals",
        "name": "Linux Fundamentals Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "Network",
        "start": 1,
        "end": 15,
        "slug": "network-fundamentals",
        "name": "Network Fundamentals Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "NetworkSecurity",
        "start": 1,
        "end": 8,
        "slug": "network-security",
        "name": "Network Security Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "WebSecurity",
        "start": 1,
        "end": 6,
        "slug": "web-security",
        "name": "Web Security Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "Terraform",
        "start": 1,
        "end": 9,
        "slug": "terraform-infrastructure",
        "name": "Terraform Infrastructure Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
    {
        "group": "OCI",
        "start": 4,
        "end": 14,
        "slug": "oci-foundations",
        "name": "OCI Foundations Study",
        "confidence": "high",
        "review_status": "add-source-metadata",
    },
]


def git_head(repository: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def post_identity(source: str) -> tuple[str, int, str]:
    path = Path(source)
    code = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    match = POST_CODE.fullmatch(code)
    if not match:
        raise ValueError(f"unable to parse post code: {source}")
    return path.parent.name, int(match.group("number")), code


def study_spec(group: str, number: int) -> dict[str, object] | None:
    for spec in STUDY_SPECS:
        if spec["group"] == group and int(spec["start"]) <= number <= int(spec["end"]):
            return spec
    return None


def docs_section(group: str, number: int) -> str:
    if group == "AWS":
        return DOC_GUIDE
    if group == "Kubernetes":
        return DOC_COMMAND
    if group == "Linux":
        return DOC_THEORY if number == 3 else DOC_COMMAND
    if group == "MultiCloud":
        return DOC_GUIDE
    if group == "Network":
        return DOC_GUIDE if number in {3, 8, 9} else DOC_THEORY
    if group == "OCI":
        if number in {1, 3, 19, 24, 29}:
            return DOC_THEORY
        if number in {2, 16}:
            return DOC_COMMAND
        return DOC_GUIDE
    raise ValueError(f"missing Docs rule for {group}{number:02d}")


def sequence_for(group: str, number: int, title: str, target_area: str) -> str | None:
    if target_area == "Study" and group == "AWS":
        if number == 2:
            return "1"
        match = re.search(r"\]\s*(\d+(?:\.\d+)*)\.", title)
        return match.group(1) if match else str(number)
    if target_area == "Study" and group == "OCI":
        return str(number - 3)
    if target_area == "Study":
        return str(number)
    if group == "MultiCloud":
        return str(number)
    return None


def suggested_title(title: str, group: str, target_area: str) -> str:
    value = BRACKET_PREFIX.sub("", title).strip()
    if target_area == "Study" and group == "AWS":
        value = re.sub(r"^\d+(?:\.\d+)*\.\s*", "", value)
    if target_area == "Study" and group == "Kubernetes":
        value = re.sub(r"^쿠버네티스 설치\(\d+\)_?", "", value).strip()
    if group == "MultiCloud":
        value = re.sub(r"^AWS-OCI VPN tunnel 이중화 \(BGP\)_\d+\.", "", value).strip()
    return value


def docs_review_status(group: str, number: int) -> tuple[str, str, str]:
    if (group == "Linux" and number <= 5) or group == "Network" or (group == "AWS" and number == 2):
        return (
            "medium",
            "confirm-docs-or-study-based-on-origin",
            "강의·책을 따라 작성한 원고인지 확인한 뒤 Docs 또는 Study를 확정합니다.",
        )
    return "high", "ready", "독립 문서로 바로 이관할 수 있습니다."


def classify(group: str, number: int, title: str) -> dict[str, object]:
    spec = study_spec(group, number)
    if spec:
        target_area = "Study"
        target_section = None
        target_collection = str(spec["slug"])
        target_parent = f"content/study/{target_collection}/"
        confidence = str(spec["confidence"])
        review_status = str(spec["review_status"])
        if review_status == "add-source-metadata":
            review_note = "Study 분류는 명확하며 강의명·책 이름·저자·강사 등 출처 정보가 필요합니다."
        else:
            review_note = "강의·책 기반인지 확인한 뒤 Study 범위와 출처를 확정합니다."
    else:
        target_area = "Docs"
        target_section = docs_section(group, number)
        target_collection = "aws-oci-bgp-vpn" if group == "MultiCloud" else None
        section_slug = {
            DOC_THEORY: "theory-reference",
            DOC_COMMAND: "command-tool",
            DOC_GUIDE: "guide-lab",
            DOC_ISSUE: "issue-troubleshooting",
        }[target_section]
        target_parent = f"content/docs/{section_slug}/"
        confidence, review_status, review_note = docs_review_status(group, number)

    return {
        "target_area": target_area,
        "target_section": target_section,
        "target_collection": target_collection,
        "target_parent": target_parent,
        "sequence": sequence_for(group, number, title, target_area),
        "classification_confidence": confidence,
        "review_status": review_status,
        "review_note": review_note,
    }


def build_plan(source_root: Path) -> dict[str, object]:
    inventory_path = ROOT / "migration" / "inventory.csv"
    with inventory_path.open(encoding="utf-8") as handle:
        inventory = list(csv.DictReader(handle))

    items: list[dict[str, object]] = []
    for row in inventory:
        source = str(row["source"])
        source_file = source_root / source
        body = source_file.read_bytes()
        text = body.decode("utf-8")
        group, number, code = post_identity(source)
        classification = classify(group, number, str(row["title"]))
        destination = str(row["destination"] or "") or None
        if row["status"] in {"sample-migrated", "migrated"} and (
            destination is None or not (ROOT / destination).exists()
        ):
            raise ValueError(f"sample destination is missing: {source} -> {destination}")

        flags: list[str] = []
        if "_" in str(row["title"]):
            flags.append("normalize-title-separator")
        if BRACKET_PREFIX.match(str(row["title"])):
            flags.append("remove-technology-prefix")
        if destination is None:
            flags.append("choose-final-slug")

        item = {
            "source": source,
            "source_sha256": hashlib.sha256(body).hexdigest(),
            "source_group": group,
            "source_number": number,
            "source_code": code,
            "legacy_url": row["legacy_url"],
            "original_title": row["title"],
            "suggested_title": suggested_title(
                str(row["title"]), group, str(classification["target_area"])
            ),
            **classification,
            "destination": destination,
            "path_status": "fixed" if destination else "choose-final-slug",
            "migration_status": row["status"],
            "image_reference_count": len(set(IMAGE_REFERENCE.findall(text))),
            "legacy_post_link_count": len(LEGACY_POST_LINK.findall(text)),
            "title_path_flags": flags,
        }
        items.append(item)

    validate_items(items)
    return {
        "schema_version": 1,
        "source_repository": "haksuperman/haksuperman.github.io",
        "source_commit": git_head(source_root),
        "source_post_count": len(items),
        "policy": {
            "source_is_read_only": True,
            "preserve_legacy_urls": True,
            "migrate_before_editorial_merge": True,
            "study_definition": "강의나 책의 목차를 따라 학습한 기록",
            "docs_definition": "독립적으로 찾아 쓰는 기술 문서와 테스트 매뉴얼",
        },
        "items": items,
    }


def validate_items(items: list[dict[str, object]]) -> None:
    if len(items) != 132:
        raise ValueError(f"expected 132 posts, found {len(items)}")
    sources = [str(item["source"]) for item in items]
    aliases = [str(item["legacy_url"]) for item in items]
    if len(sources) != len(set(sources)):
        raise ValueError("duplicate source paths in migration plan")
    if len(aliases) != len(set(aliases)):
        raise ValueError("duplicate legacy URLs in migration plan")
    for item in items:
        if item["target_area"] == "Docs" and item["target_section"] not in ALLOWED_DOC_SECTIONS:
            raise ValueError(f"invalid Docs section: {item['source']}")
        if item["target_area"] == "Study" and not item["target_collection"]:
            raise ValueError(f"missing Study collection: {item['source']}")


def markdown_summary(plan: dict[str, object]) -> str:
    items = list(plan["items"])
    area_counts = Counter(str(item["target_area"]) for item in items)
    docs_counts = Counter(
        str(item["target_section"]) for item in items if item["target_area"] == "Docs"
    )
    study_counts = Counter(
        str(item["target_collection"]) for item in items if item["target_area"] == "Study"
    )
    review_counts = Counter(str(item["review_status"]) for item in items)
    migration_counts = Counter(str(item["migration_status"]) for item in items)

    study_names = {str(spec["slug"]): str(spec["name"]) for spec in STUDY_SPECS}
    lines = [
        "# 전체 게시물 이관 계획 요약",
        "",
        f"- 원본 저장소 커밋: `{plan['source_commit']}`",
        f"- 원본 게시물: {plan['source_post_count']}개",
        f"- Docs 제안: {area_counts['Docs']}개",
        f"- Study 제안: {area_counts['Study']}개",
        f"- 현재 이관 완료: {migration_counts['migrated']}개",
        f"- 남은 게시물: {plan['source_post_count'] - migration_counts['migrated']}개",
        "- 원본 저장소는 읽기 전용으로 유지",
        "- 실제 이관 전에 모든 기존 URL과 원문 해시를 보존",
        "",
        "## Docs 분류",
        "",
        "| 분류 | 게시물 수 |",
        "|---|---:|",
    ]
    for section in (DOC_THEORY, DOC_COMMAND, DOC_GUIDE, DOC_ISSUE):
        lines.append(f"| {section} | {docs_counts[section]} |")

    lines.extend(
        [
            "",
            "## Study 제안",
            "",
            "| Study | 게시물 수 | 검토 상태 |",
            "|---|---:|---|",
        ]
    )
    spec_by_slug = {str(spec["slug"]): spec for spec in STUDY_SPECS}
    for slug, count in sorted(study_counts.items()):
        spec = spec_by_slug[slug]
        lines.append(f"| {study_names[slug]} | {count} | {spec['review_status']} |")

    lines.extend(
        [
            "",
            "## 사용자 검토 대기열",
            "",
            "| 상태 | 게시물 수 | 의미 |",
            "|---|---:|---|",
            f"| ready | {review_counts['ready']} | 현재 분류로 바로 이관 가능 |",
            f"| add-source-metadata | {review_counts['add-source-metadata']} | Study 출처 정보 필요 |",
            f"| confirm-study-boundary-and-source | {review_counts['confirm-study-boundary-and-source']} | Study 여부와 범위 확인 필요 |",
            f"| confirm-docs-or-study-based-on-origin | {review_counts['confirm-docs-or-study-based-on-origin']} | 강의·책 기반 여부에 따라 Docs/Study 결정 |",
            "",
            "## 안전 장치",
            "",
            "- `full-plan.json`의 `source_sha256`로 이관 도중 원문 변경 여부를 감지합니다.",
            "- 모든 게시물의 `legacy_url`을 새 문서의 alias로 보존합니다.",
            "- 기존 블로그 파일은 수정하거나 삭제하지 않습니다.",
            "- 제목 통합과 문서 병합은 1:1 이관 및 검증 완료 후 별도 단계에서 수행합니다.",
            "- `destination`이 비어 있는 문서는 최종 영문 slug를 확정한 뒤에만 이관합니다.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "migration" / "full-plan.json"
    )
    parser.add_argument(
        "--summary", type=Path, default=ROOT / "migration" / "plan-summary.md"
    )
    args = parser.parse_args()

    plan = build_plan(args.source.resolve())
    args.output.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.summary.write_text(markdown_summary(plan), encoding="utf-8")
    print(markdown_summary(plan))


if __name__ == "__main__":
    main()
