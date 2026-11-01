# Hugo 게시물 등록·수정 가이드

이 블로그는 글을 `content/posts/<영문-이름>/index.md`에 저장하고, 글 상단의 정보로 **Docs / Series와 세부 분류**를 결정합니다. 분류를 바꿀 때 파일이나 이미지를 옮기지 않습니다.

## 1. 처음 한 번 환경 준비

저장소 폴더에서 실행합니다.

```bash
cd /Users/haksu/Projects/haksuperman.github.io/site
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

사이트 생성에는 **Hugo Extended 0.156.0과 Go**, 또는 **Docker Desktop**이 필요합니다. Docker Desktop이 설치되어 있다면 먼저 실행하세요. 운영 도우미가 설치된 Hugo를 우선 사용하고, 없으면 Docker의 동일한 Hugo 버전을 사용합니다. 첫 실행에는 테마 다운로드가 필요할 수 있습니다.

## 2. 기억할 운영 흐름

**작업 브랜치 준비 → 새 글 또는 기존 글 수정 → 미리보기 → 게시 전 확인 → PR → 병합·배포 확인** 순서입니다.

터미널에서 `./blog`를 실행하거나 Finder에서 **블로그 관리.command**를 열면 번호로 선택하는 메뉴가 나옵니다.

```bash
./blog
```

| 메뉴 | 하는 일 |
| --- | --- |
| 새 글 만들기 | 제목·영문 이름을 입력하고 Docs/Series 및 세부 분류를 선택 |
| 기존 글 찾기 | 제목이나 영문 이름으로 파일을 찾음 |
| 게시물 분류 / 시리즈 순서 변경 | 파일을 옮기지 않고 소속·분류·순서를 변경 |
| 새 시리즈 만들기 | 시리즈를 등록하고 목록·메뉴 자동 생성 |
| 미리보기 | 초안까지 포함한 사이트 실행 |
| 게시 전 확인 | 모든 글의 분류, 공개 결과, 이미지·링크와 시리즈 이동 검사 |

운영 도우미는 글을 만들거나 검사합니다. 실제 공개는 GitHub의 PR을 병합한 뒤 수행됩니다. 기존 글 찾기는 파일 위치를 알려주며, 본문은 평소 사용하는 Markdown 편집기로 수정합니다.

## 3. Docs와 Series 선택 기준

**독립적으로 찾아 읽는 글이면 Docs**, **정해진 순서대로 읽는 글 묶음이면 Series**를 선택합니다.

Docs에서는 다음 네 가지 중 하나를 반드시 선택합니다.

| Docs 분류 | 글의 목적 | 저장되는 값 |
| --- | --- | --- |
| Theory & Reference | 기술 정의·원리·아키텍처·참고 자료 | `theory-reference` |
| Command & Tool | 명령어·도구 사용법 | `command-tool` |
| Guide & Lab | 설치·구축·실습·테스트 절차 | `guide-lab` |
| Issue & Troubleshooting | 문제 현상·원인·해결·재발 방지 | `issue-troubleshooting` |

Series에서는 등록된 시리즈를 선택합니다. 목록에 없다면 **새 시리즈 만들기**로 이름과 소개를 등록하세요. 글의 순서는 기본적으로 마지막 번호에 10을 더해 지정합니다. 예를 들어 10, 20, 30 순서이며, 중간에 추가할 때는 15를 사용할 수 있습니다. 초안도 순서를 예약하므로 같은 시리즈에서 중복 번호를 사용할 수 없습니다.

AWS, OCI, Kubernetes 같은 기술 키워드는 `tags`로 입력합니다. Docs의 네 가지 문서 분류와는 별개입니다.

## 4. 새 글 등록

먼저 [운영 가이드](OPERATIONS.md)의 절차로 최신 main에서 작업 브랜치를 준비합니다. `./blog`의 **새 글 만들기**를 선택하면 다음 순서로 묻습니다.

1. 게시물 제목
2. 저장할 영문 이름 — 예: `oke-cluster`
3. Docs 또는 Series
4. Docs라면 네 가지 문서 분류, Series라면 시리즈와 순서

다음 파일이 만들어집니다.

```text
content/posts/oke-cluster/
└── index.md
```

영문 이름은 소문자·숫자·단어 사이의 하이픈을 사용하며, 공개 주소는 `/posts/oke-cluster/`가 됩니다. 제목이나 분류를 수정해도 영문 이름을 유지하면 주소는 유지됩니다. 새 글은 항상 `draft: true`인 초안으로 생성됩니다.

선택 없이 한 번에 생성하는 명령도 지원합니다.

```bash
./blog new --title "OKE 클러스터 구축" --slug oke-cluster \
  --collection docs --category guide-lab --tags OCI OKE Kubernetes
```

Series 예시:

```bash
./blog new --title "클러스터 초기화" --slug kubernetes-bootstrap \
  --collection series --series kubernetes-cluster --tags Kubernetes
```

필요하면 `--order 40`으로 순서를 직접 지정합니다. 기존 파일과 폴더를 덮어쓰지 않습니다.

Hugo 명령을 직접 사용해도 됩니다. 두 종류 모두 동일한 `content/posts/` 아래에 생성합니다.

```bash
hugo new content --kind docs posts/oke-cluster/index.md
hugo new content --kind series posts/kubernetes-bootstrap/index.md
```

생성 후 Docs는 `docCategory`를 확인하고, Series는 빈 `seriesId`와 `seriesOrder`를 지정하세요. 분류를 선택해서 자동으로 입력하려면 `./blog new`를 사용합니다.

## 5. 글 상단 정보 이해하기

Docs 예시:

```yaml
---
title: "OKE 클러스터 구축"
date: "2026-11-01T15:00:00+09:00"
draft: true
collection: docs
docCategory: guide-lab
tags: ["OCI", "OKE", "Kubernetes"]
---
```

Series 예시:

```yaml
---
title: "Kubernetes 클러스터 초기화"
date: "2026-11-01T15:00:00+09:00"
draft: true
collection: series
seriesId: kubernetes-cluster
seriesOrder: 40
tags: ["Kubernetes"]
---
```

| 항목 | 수정 규칙 |
| --- | --- |
| `title` | 글 제목. 언제든 수정 가능 |
| `linkTitle` | 선택 항목. 메뉴에 더 짧은 제목이 필요할 때만 입력 |
| `date` | 최초 작성일. 기존 글을 고칠 때 유지 |
| `draft` | 초안은 `true`, 공개 준비가 끝나면 `false`. 따옴표 없이 작성 |
| `collection` | `docs` 또는 `series` 중 하나 |
| `docCategory` | Docs에서만 사용. 네 가지 분류 중 하나 |
| `seriesId` | Series에서만 사용. 등록된 시리즈 ID |
| `seriesOrder` | Series에서만 사용. 같은 시리즈 안에서 중복되지 않는 양의 정수 |
| `tags` | 선택 항목. 기술 키워드 목록 |
| `aliases` | 선택 항목. 이미 공개된 이전 주소를 현재 글로 연결. 새 글에는 입력하지 않아도 됨 |
| `lastmod` | 선택 항목. 기본 수정일은 Git 기록으로 자동 반영. 특정 날짜로 고정할 때만 사용 |

`categories`, `weight`는 이 블로그의 게시물 분류·순서에 사용하지 않습니다. Docs에 시리즈 정보를 함께 넣거나 Series에 `docCategory`를 넣으면 검사에서 안내합니다.

## 6. 본문·이미지 수정

본문은 Markdown으로 작성합니다. 이미지는 글과 같은 폴더에 넣고 파일 이름으로 연결합니다.

```text
content/posts/oke-cluster/
├── index.md
├── architecture.png
└── result.png
```

```markdown
![OKE 구성도](architecture.png)
```

이미지를 자유롭게 추가·삭제할 수 있습니다. 삭제한 이미지가 본문에서 참조되고 있으면 게시 전 확인에서 알려줍니다. 이미지와 본문에 계정 비밀번호·인증 키 같은 민감정보가 없는지도 확인하세요.

다른 게시물로 연결할 때는 Hugo의 `relref`를 사용합니다. 삭제되거나 없는 게시물을 가리키면 빌드에서 확인할 수 있습니다.

```markdown
[클러스터 초기화]({{< relref "/posts/kubernetes-bootstrap/" >}})
```

## 7. 기존 글 찾기·분류 변경

```bash
./blog list --search OKE
```

검색 결과의 `content/posts/<영문-이름>/index.md`를 편집기로 엽니다. 제목·본문·태그 수정은 이 파일에서 수행합니다.

분류는 관리 메뉴 또는 다음 명령으로 바꿀 수 있습니다.

```bash
./blog classify oke-cluster
```

새로운 Docs/Series 소속과 세부 분류를 선택하면 불필요해진 이전 분류 정보는 자동으로 제거됩니다. 파일 위치·본문·이미지는 유지됩니다.

```bash
# Docs의 다른 분류로 변경
./blog classify oke-cluster --collection docs --category theory-reference

# Series로 변경하거나 다른 시리즈로 이동
./blog classify oke-cluster --collection series --series oci-foundations --order 120
```

직접 글 상단을 수정해도 됩니다. **Docs에는 `docCategory`만, Series에는 `seriesId`와 `seriesOrder`만** 남기세요. 저장 후 미리보기를 확인하면 분류 목록·왼쪽 메뉴·현재 위치·시리즈 이전/다음 글이 새 정보에 맞게 반영됩니다.

## 8. 시리즈 등록·이름 변경

```bash
./blog series-add --id oke-operations --title "OKE 운영" --description "OKE 운영 절차를 순서대로 정리합니다."
```

이 명령은 **분류 정의 파일 `data/navigation.json` 한곳만 수정**합니다. Hugo가 목록 페이지와 메뉴를 자동으로 만드므로 별도 폴더나 메뉴를 추가하지 않습니다.

이 파일에서 Docs·Series의 `title`과 `description`을 수정할 수 있습니다. `subtitle`은 기존 카드의 짧은 소개, `homeSubtitle`은 홈의 짧은 소개, `icon`은 카드 아이콘입니다. 새 시리즈에서는 생략할 수 있습니다. 시리즈의 배열 순서는 메뉴와 홈의 표시 순서입니다. **이름만 바꿀 때는 `id`를 유지**하세요. ID를 바꾸거나 시리즈를 삭제할 경우에는 소속된 글의 `seriesId`도 함께 변경해야 합니다. Docs 네 분류의 ID는 고정입니다.

## 9. 미리보기·공개 준비

```bash
./blog preview
```

브라우저에서 `http://localhost:1313/`을 엽니다. 초안도 보이며, 초안 글 상단에는 안내가 표시됩니다. 종료하려면 터미널에서 `Ctrl+C`를 누릅니다. 메뉴에서 실행했다면 메뉴로 돌아갑니다.

확인할 내용:

- Docs/Series와 세부 분류가 올바른가
- 메뉴·현재 위치·시리즈 순서와 이전/다음 이동이 올바른가
- 본문·이미지·표·코드와 모바일 화면이 정상인가

검수가 끝난 글만 `draft: false`로 바꾸고 실행합니다.

```bash
./blog check
```

이 명령은 초안의 작성 정보도 검사하지만, 공개 결과에는 공개할 글만 포함됐는지 확인합니다. 미래의 작성일·게시 예정일을 지정한 글은 해당 시각 전까지 공개되지 않습니다. 수정일 자동 반영은 커밋 후 빌드에서 적용됩니다. 2026년 11월 1일에 기존 게시물 132개의 표시 수정일만 등록일로 한 번 보정했습니다. 이후 해당 게시물 파일을 수정하고 커밋하면 새 수정일이 자동 반영되며, 등록일인 `date`는 유지됩니다.

## 10. 게시·수정 반영·비공개·삭제

공개 준비가 끝나면 [운영 가이드](OPERATIONS.md)에 따라 변경 파일을 커밋하고 PR을 올립니다. PR 검사 성공 후 `main`에 병합하면 GitHub Pages에 배포됩니다.

- **기존 글 수정 반영:** 수정하고 미리보기·확인 후 같은 PR 절차로 반영합니다.
- **비공개 전환:** `draft: true`로 바꾼 뒤 PR로 반영합니다. 공개 사이트에서 빠져도 저장소에 파일은 남습니다. 공개 저장소에 있는 초안은 비밀 문서가 아닙니다.
- **삭제:** 글 폴더를 삭제하고, 그 글을 참조하는 내부 링크도 고친 뒤 확인·PR 절차를 수행합니다. 글과 이미지의 이전 버전은 Git 기록에 남습니다.

`public/`은 자동 생성 결과이므로 직접 수정하거나 커밋하지 않습니다. 게시 작업에는 이관 계획표나 과거 이미지 개수 기록을 수정할 필요가 없습니다.


## 11. 이전 주소 연결

글은 현재 `/posts/<영문-이름>/`에서 공개됩니다. 과거에 공개했던 `/study/.../`, `/series/.../`, `/docs/.../` 등의 주소는 해당 글의 `aliases`로 연결합니다. 분류를 바꾸어도 이 정보는 유지되며, 새 글에 과거 주소를 만들 필요는 없습니다.

```yaml
aliases:
  - "/study/aws-security/01-01-shared-responsibility-model/"
  - "/series/aws-security/01-01-shared-responsibility-model/"
  - "/posts/aws04/"
```

이전 링크에서 자동으로 현재 글로 이동합니다. 이전 주소 연결은 글 상단의 분류와 별개이며, `./blog classify`로 분류를 바꿔도 유지됩니다. 이전 주소가 중복되거나 현재 글 주소와 충돌하면 `./blog check`가 알려줍니다. 초안·비공개 글의 연결 페이지도 공개 빌드에서는 제외됩니다.
