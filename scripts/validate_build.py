#!/usr/bin/env python3
"""Check current Hugo content, navigation and generated local references."""
from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from content_model import ROOT, ContentError, is_published, validate_sources


class PageLinks(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.references, self.lists, self.breadcrumbs, self.pager = [], [], [], []
        self._contexts = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "nav":
            kind = ("list" if "data-content-list" in attrs else
                    "breadcrumb" if attrs.get("aria-label") == "현재 위치" else
                    "pager" if "data-series-pager" in attrs else "other")
            self._contexts.append(kind)
        for key in ("href", "src", "poster"):
            if attrs.get(key):
                self.references.append(attrs[key])
        if tag == "a" and attrs.get("href") and self._contexts:
            if self._contexts[-1] == "list":
                self.lists.append(attrs["href"])
            elif self._contexts[-1] == "breadcrumb":
                self.breadcrumbs.append(attrs["href"])
            elif self._contexts[-1] == "pager":
                self.pager.append((attrs.get("rel"), attrs["href"]))

    def handle_endtag(self, tag):
        if tag == "nav" and self._contexts:
            self._contexts.pop()


def local_target(public, html, url):
    parts = urlsplit(url)
    if not parts.path or (parts.scheme and parts.scheme not in {"http", "https"}):
        return None
    if parts.netloc and parts.netloc != "haksuperman.github.io":
        return None
    path = unquote(parts.path)
    target = public / path.lstrip("/") if path.startswith("/") else html.parent / path
    if path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def validate(root=ROOT, include_drafts=False):
    data, posts = validate_sources(root)
    public = root / "public"
    errors = []
    try:
        index = json.loads((public / "content-index.json").read_text(encoding="utf-8"))["posts"]
    except (OSError, ValueError, KeyError) as error:
        raise ContentError("Hugo 빌드 결과가 없습니다. ./blog check를 실행하세요.") from error
    expected = {f"/posts/{path.parent.name}/": metadata for path, metadata, _ in posts if is_published(metadata, include_drafts)}
    actual = {item["url"]: item for item in index}
    if len(actual) != len(index):
        errors.append("동일한 공개 주소가 여러 게시물에 사용됩니다.")
    if actual.keys() != expected.keys():
        for url in expected.keys() - actual.keys():
            errors.append(f"공개되어야 할 글이 빌드되지 않았습니다: {url}")
        for url in actual.keys() - expected.keys():
            errors.append(f"공개 대상이 아닌 글이 빌드에 포함됐습니다: {url}")
    for url in actual.keys() & expected.keys():
        metadata = expected[url]
        for field in ("collection", "docCategory", "seriesId", "seriesOrder"):
            if actual[url].get(field) != metadata.get(field, 0 if field == "seriesOrder" else ""):
                errors.append(f"{url}: 빌드된 {field}가 글 상단 정보와 다릅니다.")
    parsed = {}
    for html in public.rglob("*.html"):
        page = PageLinks(html.read_text(encoding="utf-8"))
        parsed[html] = page
        for url in page.references:
            target = local_target(public, html, url)
            if target is not None and not target.exists():
                errors.append(f"{html.relative_to(public)}: 연결 대상이 없습니다: {url}")
    for collection in ("docs", "series"):
        for group in data[collection]:
            url = f"/{collection}/{group['id']}/"
            page = parsed.get(public / url.lstrip("/") / "index.html")
            if page is None:
                errors.append(f"분류 목록이 생성되지 않았습니다: {url}")
                continue
            field = "docCategory" if collection == "docs" else "seriesId"
            selected = [link for link, metadata in expected.items() if metadata["collection"] == collection and metadata.get(field) == group["id"]]
            if set(page.lists) != set(selected) or len(page.lists) != len(selected):
                errors.append(f"{url}: 분류에 속한 글 목록이 일치하지 않습니다.")
            if collection == "series":
                selected.sort(key=lambda link: expected[link]["seriesOrder"])
                if page.lists != selected:
                    errors.append(f"{url}: 시리즈 목차 순서가 올바르지 않습니다.")
            for position, link in enumerate(selected):
                article = parsed.get(public / link.lstrip("/") / "index.html")
                if article is None:
                    errors.append(f"게시물 HTML이 없습니다: {link}")
                    continue
                if f"/{collection}/" not in article.breadcrumbs or url not in article.breadcrumbs:
                    errors.append(f"{link}: 현재 위치에 올바른 분류가 표시되지 않습니다.")
                if collection == "series":
                    neighbors = []
                    if position > 0:
                        neighbors.append(("prev", selected[position - 1]))
                    if position + 1 < len(selected):
                        neighbors.append(("next", selected[position + 1]))
                    if article.pager != neighbors:
                        errors.append(f"{link}: 시리즈 이전/다음 연결이 올바르지 않습니다.")
    if errors:
        raise ContentError("\n".join(errors))
    return {"게시물": len(posts), "공개 글": len(actual), "Docs 분류": len(data["docs"]), "시리즈": len(data["series"]), "검사한 HTML": len(parsed)}


def main():
    parser = argparse.ArgumentParser(description="Hugo 게시물과 생성 결과 검증")
    parser.add_argument("--sources-only", action="store_true", help="초안을 포함한 게시물 정보만 검사")
    parser.add_argument("--include-drafts", action="store_true", help="hugo --buildDrafts 결과 검사")
    args = parser.parse_args()
    try:
        if args.sources_only:
            _, posts = validate_sources()
            print(f"게시물 {len(posts)}개의 분류와 작성 정보를 확인했습니다.")
        else:
            print(json.dumps(validate(include_drafts=args.include_drafts), ensure_ascii=False, indent=2))
    except (ContentError, OSError) as error:
        parser.exit(1, f"확인해 주세요:\n{error}\n")


if __name__ == "__main__":
    main()
