"""Shared post metadata rules for authoring and publication checks."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("먼저 가이드의 환경 준비를 실행하세요: python3 -m pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DOC_IDS = {"theory-reference", "command-tool", "guide-lab", "issue-troubleshooting"}


class ContentError(ValueError):
    pass


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate keys rather than silently discarding a classification."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ContentError(f"중복된 항목: {key}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def catalog(root=ROOT):
    try:
        data = json.loads((root / "data/navigation.json").read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ContentError("분류 정의는 JSON 객체여야 합니다.")
        for group in ("docs", "series"):
            items = data.get(group)
            if not isinstance(items, list):
                raise ContentError(f"{group}: 분류 목록이 필요합니다.")
            seen = set()
            for item in items:
                if not isinstance(item, dict):
                    raise ContentError(f"{group}: 각 분류는 객체여야 합니다.")
                key = item.get("id", "")
                if not isinstance(key, str) or not SLUG.fullmatch(key) or key in seen:
                    raise ContentError(f"{group}: 올바르지 않거나 중복된 ID: {key}")
                seen.add(key)
                if not isinstance(item.get("title"), str) or not item["title"].strip():
                    raise ContentError(f"{key}: 표시 이름이 필요합니다.")
                if not isinstance(item.get("description", ""), str):
                    raise ContentError(f"{key}: 설명은 문자열이어야 합니다.")
        if {item["id"] for item in data["docs"]} != DOC_IDS:
            raise ContentError("Docs의 네 가지 분류 ID는 변경할 수 없습니다. 표시 이름은 수정할 수 있습니다.")
        return data
    except (OSError, ValueError, TypeError) as error:
        raise ContentError(f"data/navigation.json: {error}") from error


def read_post(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        raise ContentError(f"{path}: 글 상단의 --- 사이에 YAML 정보를 작성하세요.")
    try:
        metadata = yaml.load(match.group(1), Loader=UniqueLoader)
        if not isinstance(metadata, dict):
            raise ContentError("게시물 정보는 항목과 값으로 작성하세요.")
        return metadata, text[match.end():]
    except (yaml.YAMLError, ValueError, TypeError) as error:
        raise ContentError(f"{path}: {error}") from error


def write_post(path, metadata, body):
    front = yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False, width=100)
    path.write_text(f"---\n{front}---\n{body}", encoding="utf-8")


def as_time(value):
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=value.tzinfo or dt.timezone(dt.timedelta(hours=9)))
    if isinstance(value, dt.date):
        return dt.datetime.combine(value, dt.time(), dt.timezone(dt.timedelta(hours=9)))
    if isinstance(value, str):
        return as_time(dt.datetime.fromisoformat(value.replace("Z", "+00:00")))
    raise ValueError("날짜 형식이 올바르지 않습니다.")


def is_published(metadata, include_drafts=False, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    if metadata.get("draft", False) and not include_drafts:
        return False
    return (as_time(metadata.get("publishDate", metadata["date"])) <= now
            and (not metadata.get("expiryDate") or as_time(metadata["expiryDate"]) > now))


def validate_sources(root=ROOT):
    """Validate drafts too; publication and historical inventory are independent."""
    data = catalog(root)
    errors, posts, positions = [], [], {}
    series_ids = {item["id"] for item in data["series"]}
    for path in sorted((root / "content/posts").rglob("*.md")):
        if path.name == "_index.md":
            continue
        label = str(path.relative_to(root))
        try:
            metadata, body = read_post(path)
            if path.name != "index.md" or path.parent.parent != root / "content/posts" or not SLUG.fullmatch(path.parent.name):
                raise ContentError("게시물은 content/posts/<영문-이름>/index.md에 저장하세요.")
            if not isinstance(metadata.get("title"), str) or not metadata["title"].strip():
                raise ContentError("title에 제목을 입력하세요.")
            if type(metadata.get("draft")) is not bool:
                raise ContentError("draft는 따옴표 없이 true 또는 false로 입력하세요.")
            for key in ("date", "publishDate", "expiryDate", "lastmod"):
                if key == "date" or key in metadata:
                    try:
                        as_time(metadata.get(key))
                    except (ValueError, TypeError):
                        raise ContentError(f"{key}에 올바른 날짜를 입력하세요.")
            if not isinstance(metadata.get("tags", []), list) or any(not isinstance(tag, str) for tag in metadata.get("tags", [])):
                raise ContentError("tags는 문자열 목록으로 입력하세요.")
            for key in ("url", "slug", "type", "layout", "weight", "categories", "params", "_build", "build"):
                if key in metadata:
                    raise ContentError(f"{key}는 게시물에서 사용하지 않습니다. 분류는 collection과 세부 항목으로 지정하세요.")
            collection = metadata.get("collection")
            if collection == "docs":
                if not isinstance(metadata.get("docCategory"), str) or metadata["docCategory"] not in DOC_IDS:
                    raise ContentError("docCategory에 Docs의 네 가지 분류 중 하나를 지정하세요.")
                if "seriesId" in metadata or "seriesOrder" in metadata:
                    raise ContentError("Docs 글에서는 seriesId와 seriesOrder를 제거하세요.")
            elif collection == "series":
                if "docCategory" in metadata:
                    raise ContentError("Series 글에서는 docCategory를 제거하세요.")
                if not isinstance(metadata.get("seriesId"), str) or metadata["seriesId"] not in series_ids:
                    raise ContentError("seriesId가 존재하지 않습니다. 먼저 시리즈를 등록하세요.")
                order = metadata.get("seriesOrder")
                if type(order) is not int or order <= 0:
                    raise ContentError("seriesOrder는 0보다 큰 정수로 입력하세요.")
                position = (metadata["seriesId"], order)
                if position in positions:
                    raise ContentError(f"시리즈 순서 {order}가 {positions[position]}와 중복됩니다.")
                positions[position] = label
            else:
                raise ContentError("collection은 docs 또는 series로 입력하세요.")
            if not body.strip():
                raise ContentError("본문을 작성하세요.")
            posts.append((path, metadata, body))
        except (ContentError, OSError) as error:
            errors.append(f"{label}: {error}")
    # Files left outside the uniform post location must not silently disappear from menus.
    for group in ("docs", "series"):
        if any(path.name != "_index.md" for path in (root / f"content/{group}").rglob("*.md")):
            errors.append(f"content/{group}: 게시물은 content/posts/<이름>/index.md에 저장하세요.")
    if errors:
        raise ContentError("\n".join(errors))
    alias_routes(root, data, posts)
    return data, posts


def alias_routes(root, data, posts):
    """Known published addresses use native Hugo aliases; no historical inventory is needed."""
    targets = {"/", "/docs/", "/series/", "/posts/", "/about/", "/tags/"}
    entries = []
    for path, metadata, _ in posts:
        target = f"/posts/{path.parent.name}/"
        targets.add(target)
        entries.append((str(path.relative_to(root)), target, metadata.get("aliases", [])))
    for collection in ("docs", "series"):
        for group in data[collection]:
            target = f"/{collection}/{group['id']}/"
            targets.add(target)
            entries.append((f"data/navigation.json: {group['id']}", target, group.get("aliases", [])))
    for path in (root / "content").rglob("_index.md"):
        metadata, _ = read_post(path)
        relative = path.parent.relative_to(root / "content").as_posix()
        target = "/" if relative == "." else f"/{relative}/"
        targets.add(target)
        entries.append((str(path.relative_to(root)), target, metadata.get("aliases", [])))
    routes, owners = {}, {}
    for label, target, aliases in entries:
        if not isinstance(aliases, list):
            raise ContentError(f"{label}: aliases는 이전 주소의 목록으로 입력하세요.")
        for alias in aliases:
            if not isinstance(alias, str) or not re.fullmatch(r"/(?:[a-z0-9]+(?:-[a-z0-9]+)*/)+", alias):
                raise ContentError(f"{label}: aliases에는 /로 시작하고 끝나는 영문 경로를 입력하세요.")
            if alias in targets or alias.startswith(("/tags/", "/images/")):
                raise ContentError(f"{label}: 이전 주소가 현재 경로와 충돌합니다: {alias}")
            if alias in routes:
                raise ContentError(f"{label}: 이전 주소가 {owners[alias]}와 중복됩니다: {alias}")
            routes[alias] = target
            owners[alias] = label
    return routes
