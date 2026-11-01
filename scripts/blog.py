#!/usr/bin/env python3
"""Create, classify, preview and check Hugo posts from one entry point."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

from content_model import ROOT, SLUG, ContentError, catalog, read_post, validate_sources, write_post


def choose(prompt, entries):
    print(f"\n{prompt}")
    for number, (_, title) in enumerate(entries, 1):
        print(f"  {number}. {title}")
    while True:
        value = input("번호: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(entries):
            return entries[int(value) - 1][0]
        print("목록의 번호를 입력하세요.")


def required(prompt, value=None):
    while not value or not value.strip():
        value = input(f"{prompt}: ").strip()
    return value.strip()


def next_order(root, series_id, exclude=None):
    orders = []
    for path in (root / "content/posts").glob("*/index.md"):
        if path == exclude:
            continue
        metadata, _ = read_post(path)
        if metadata.get("collection") == "series" and metadata.get("seriesId") == series_id:
            order = metadata.get("seriesOrder")
            if type(order) is int:
                orders.append(order)
    return max(orders, default=0) + 10


def select_classification(root, collection=None, category=None, series=None, order=None, exclude=None):
    data = catalog(root)
    collection = collection or choose("Docs와 Series 중 어디에 넣을까요?", [("docs", "Docs"), ("series", "Series")])
    if collection == "docs":
        if series is not None or order is not None:
            raise ContentError("Docs에는 --series와 --order를 지정하지 않습니다.")
        category = category or choose("Docs의 문서 분류를 선택하세요.", [(item["id"], item["title"]) for item in data["docs"]])
        if category not in {item["id"] for item in data["docs"]}:
            raise ContentError("존재하지 않는 Docs 분류입니다.")
        return {"collection": "docs", "docCategory": category}
    if collection != "series" or category is not None:
        raise ContentError("collection을 확인하세요. Series에는 --category를 지정하지 않습니다.")
    if not series:
        entries = [(item["id"], item["title"]) for item in data["series"]] + [("__new__", "새 시리즈 만들기")]
        series = choose("어떤 시리즈에 넣을까요?", entries)
        if series == "__new__":
            series = add_series(root)
            data = catalog(root)
    if series not in {item["id"] for item in data["series"]}:
        raise ContentError("시리즈가 없습니다. ./blog series-add로 먼저 등록하세요.")
    suggested = next_order(root, series, exclude)
    if order is None:
        if sys.stdin.isatty():
            value = input(f"시리즈 순서 [마지막에 추가: {suggested}]: ").strip()
            try:
                order = int(value) if value else suggested
            except ValueError:
                raise ContentError("시리즈 순서는 정수로 입력하세요.")
        else:
            order = suggested
    if type(order) is not int or order <= 0:
        raise ContentError("시리즈 순서는 0보다 큰 정수여야 합니다.")
    for path in (root / "content/posts").glob("*/index.md"):
        if path == exclude:
            continue
        metadata, _ = read_post(path)
        if metadata.get("collection") == "series" and metadata.get("seriesId") == series and metadata.get("seriesOrder") == order:
            raise ContentError(f"순서 {order}는 {path.parent.name}에서 이미 사용 중입니다.")
    return {"collection": "series", "seriesId": series, "seriesOrder": order}


def new_post(root=ROOT, *, title=None, slug=None, collection=None, category=None, series=None, order=None, tags=None):
    title = required("게시물 제목", title)
    slug = required("저장할 영문 이름 (예: oke-cluster)", slug)
    if not SLUG.fullmatch(slug):
        raise ContentError("영문 이름에는 소문자, 숫자와 단어 사이의 하이픈만 사용하세요.")
    path = root / "content/posts" / slug / "index.md"
    if path.parent.exists():
        raise ContentError(f"이미 존재하는 게시물 폴더입니다: {path.parent}")
    classification = select_classification(root, collection, category, series, order)
    metadata = {"title": title, "date": dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec="seconds"), "draft": True, **classification, "tags": tags or []}
    body = "\n## 1. 개요\n\n글의 목적과 전제 조건을 작성합니다.\n\n## 2. 내용\n\n본문을 작성합니다.\n\n## 3. 정리\n\n결과와 참고 자료를 작성합니다.\n"
    path.parent.mkdir(parents=True, exist_ok=False)
    write_post(path, metadata, body)
    print(f"\n초안을 만들었습니다: {path}\n이미지는 같은 폴더에 넣으세요. 미리보기: ./blog preview")
    return path


def reclassify(root, slug, **options):
    if not SLUG.fullmatch(slug):
        raise ContentError("게시물의 영문 이름을 입력하세요.")
    path = root / "content/posts" / slug / "index.md"
    metadata, body = read_post(path)
    classification = select_classification(root, exclude=path, **options)
    for key in ("collection", "docCategory", "seriesId", "seriesOrder"):
        metadata.pop(key, None)
    metadata.update(classification)
    write_post(path, metadata, body)
    print(f"분류를 변경했습니다: {path}\n파일 위치와 본문은 유지됩니다.")


def add_series(root=ROOT, series_id=None, title=None, description=None):
    data = catalog(root)
    series_id = required("시리즈 영문 ID (예: oke-operations)", series_id)
    if not SLUG.fullmatch(series_id) or series_id in {item["id"] for item in data["series"]}:
        raise ContentError("시리즈 ID가 올바르지 않거나 이미 존재합니다.")
    title = required("시리즈 표시 이름", title)
    if description is None:
        description = input("시리즈 소개 (생략 가능): ").strip()
    data["series"].append({"id": series_id, "title": title, "description": description})
    (root / "data/navigation.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"시리즈를 등록했습니다: {title} ({series_id})\n목록과 메뉴는 다음 Hugo 빌드에서 자동 생성됩니다.")
    return series_id


def list_posts(root, search=""):
    data, posts = validate_sources(root)
    names = {item["id"]: item["title"] for item in data["docs"] + data["series"]}
    for path, metadata, _ in posts:
        if search.lower() not in (metadata["title"] + " " + path.parent.name).lower():
            continue
        group = metadata.get("docCategory", metadata.get("seriesId"))
        state = "초안" if metadata["draft"] else "공개 대상"
        print(f"{path.parent.name}\n  {metadata['title']} | {metadata['collection']} / {names[group]} | {state}")


def hugo(root=ROOT, preview=False, include_drafts=False):
    native = shutil.which("hugo")
    args = ["server", "--buildDrafts", "--navigateToChanged", "--disableFastRender"] if preview else ["--gc", "--minify", "--cleanDestinationDir", "--printPathWarnings"]
    if include_drafts and not preview:
        args.append("--buildDrafts")
    if native:
        subprocess.run([native, *args], cwd=root, check=True)
        return
    docker = shutil.which("docker")
    if not docker:
        raise ContentError("Hugo와 Go 또는 Docker Desktop을 설치하세요. AUTHORING.md의 환경 준비를 확인하세요.")
    if subprocess.run([docker, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        raise ContentError("Docker Desktop을 실행한 다음 다시 시도하세요.")
    image = "haksuperman-hugo-verify:0.156.0"
    if subprocess.run([docker, "image", "inspect", image], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        subprocess.run([docker, "build", "-f", "Dockerfile.verify", "-t", image, "."], cwd=root, check=True)
    command = [docker, "run", "--rm", "-v", f"{root}:/src", "-v", "haksuperman-hugo-cache:/tmp/hugo_cache"]
    if preview:
        command += ["-p", "127.0.0.1:1313:1313"]
        args += ["--bind", "0.0.0.0", "--baseURL", "http://localhost:1313/", "--poll", "1s"]
    subprocess.run([*command, image, *args], cwd=root, check=True)


def check(root=ROOT):
    validate_sources(root)
    hugo(root)
    from validate_build import validate
    result = validate(root)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def menu(root=ROOT):
    while True:
        action = choose("블로그 관리", [("new", "새 글 만들기"), ("list", "기존 글 찾기"), ("classify", "게시물 분류 / 시리즈 순서 변경"), ("series", "새 시리즈 만들기"), ("preview", "미리보기"), ("check", "게시 전 확인"), ("exit", "종료")])
        try:
            if action == "exit":
                return
            if action == "new":
                new_post(root)
            elif action == "list":
                list_posts(root, input("제목 또는 영문 이름 검색 (전체: Enter): "))
                print("표시된 영문 이름의 content/posts/<이름>/index.md를 편집기로 여세요.")
            elif action == "classify":
                reclassify(root, required("변경할 게시물 영문 이름"))
            elif action == "series":
                add_series(root)
            elif action == "preview":
                validate_sources(root)
                hugo(root, preview=True)
            else:
                check(root)
        except (ContentError, OSError, subprocess.CalledProcessError) as error:
            print(f"\n확인해 주세요: {error}", file=sys.stderr)
        except KeyboardInterrupt:
            print("\n메뉴로 돌아갑니다.")


def main():
    parser = argparse.ArgumentParser(description="Hugo 게시물 등록과 운영")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("menu", help="번호로 선택하는 운영 메뉴")
    for name in ("new", "classify"):
        command = commands.add_parser(name)
        if name == "new":
            command.add_argument("--title")
            command.add_argument("--slug")
            command.add_argument("--tags", nargs="*", default=[])
        else:
            command.add_argument("slug")
        command.add_argument("--collection", choices=("docs", "series"))
        command.add_argument("--category")
        command.add_argument("--series")
        command.add_argument("--order", type=int)
    command = commands.add_parser("series-add")
    command.add_argument("--id", dest="series_id")
    command.add_argument("--title")
    command.add_argument("--description")
    command = commands.add_parser("list")
    command.add_argument("--search", default="")
    commands.add_parser("preview")
    commands.add_parser("check")
    args = vars(parser.parse_args())
    command = args.pop("command") or "menu"
    try:
        if command == "menu":
            menu()
        elif command == "new":
            new_post(**args)
        elif command == "classify":
            reclassify(ROOT, **args)
        elif command == "series-add":
            add_series(**args)
        elif command == "list":
            list_posts(ROOT, **args)
        elif command == "preview":
            validate_sources()
            hugo(preview=True)
        else:
            check()
    except (ContentError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"확인해 주세요: {error}\n")
    except (KeyboardInterrupt, EOFError):
        parser.exit(0, "\n종료했습니다.\n")


if __name__ == "__main__":
    main()
