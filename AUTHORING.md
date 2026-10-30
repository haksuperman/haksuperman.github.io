# 게시물 작성 가이드

이 문서는 AI 도구 없이 Hugo와 Git만 사용해 게시물을 작성하고 검수한 뒤 배포하는 절차를 설명합니다.

## 1. 문서 위치 선택

새 글을 만들기 전에 글의 목적에 맞는 위치를 선택합니다.

| 문서 종류 | 저장 위치 | 용도 |
| --- | --- | --- |
| Theory & Reference | `content/docs/theory-reference/` | 기술 정의, 원리, 아키텍처와 참고 문서 |
| Command & Tool | `content/docs/command-tool/` | 명령어와 도구 사용법 |
| Guide & Lab | `content/docs/guide-lab/` | 설치, 구축, 테스트와 재현 가능한 실습 |
| Issue & Troubleshooting | `content/docs/issue-troubleshooting/` | 문제 현상, 원인, 해결과 재발 방지 |
| Series | `content/study/<series-name>/` | 강의, 책 또는 연속 학습의 목차형 기록 |

화면에는 `Series`로 표시하지만 기존 주소를 보존하기 위해 실제 폴더명은 `study`를 사용합니다.

## 2. 새 Docs 문서 만들기

저장소 루트에서 다음 명령을 실행합니다. `<slug>`는 영문 소문자와 하이픈으로 작성합니다.

```bash
hugo new content --kind docs docs/guide-lab/<slug>/index.md
```

예시:

```bash
hugo new content --kind docs docs/guide-lab/oke-version-upgrade/index.md
```

생성 결과:

```text
content/docs/guide-lab/oke-version-upgrade/
└── index.md
```

분류에 따라 `guide-lab` 부분을 `theory-reference`, `command-tool`, `issue-troubleshooting`으로 변경합니다.

## 3. 새 Series 문서 만들기

먼저 글을 추가할 Series 폴더를 확인한 다음 다음 명령을 실행합니다.

```bash
hugo new content --kind series study/<series-name>/<sequence-slug>/index.md
```

예시:

```bash
hugo new content --kind series study/aws-security/11-01-new-security-topic/index.md
```

생성 결과:

```text
content/study/aws-security/11-01-new-security-topic/
└── index.md
```

Series 문서의 `weight`는 왼쪽 목차 순서를 결정합니다. 같은 Series의 앞뒤 문서를 확인해 중복되지 않는 값을 입력합니다.

## 4. Front Matter 작성

`index.md` 위쪽의 `---` 사이 영역은 문서의 메타데이터입니다.

```yaml
---
title: "OKE 버전 업그레이드"
linkTitle: "OKE 버전 업그레이드"
date: "2026-10-30T10:00:00+09:00"
draft: true
tags:
  - "oci"
  - "oke"
  - "kubernetes"
---
```

- `title`: 본문 상단에 표시되는 전체 제목
- `linkTitle`: 왼쪽 메뉴와 경로에 표시되는 짧은 제목
- `date`: 작성 시각. 한국 표준시는 `+09:00`을 사용합니다.
- `draft`: 작성 중에는 `true`, 공개할 때는 `false`
- `tags`: 기술 스택과 검색에 사용할 키워드
- `weight`: Series 문서의 목차 순서에만 사용
- `aliases`: 기존 주소를 변경하거나 대체할 때만 사용

새 문서는 기존 문서를 복사하지 말고 Hugo 명령으로 생성합니다. 기존 문서의 `aliases`, 날짜와 이관용 메타데이터가 실수로 복제되는 것을 방지할 수 있습니다.

## 5. 본문과 이미지 작성

본문은 Markdown으로 작성합니다.

```markdown
## 1. 개요

문서의 목적과 전제 조건을 설명합니다.

### 1.1. 구성

세부 내용을 작성합니다.
```

이미지는 `index.md`와 같은 폴더에 넣습니다.

```text
oke-version-upgrade/
├── index.md
├── architecture.png
└── result.png
```

본문에서는 파일 이름으로 참조합니다.

```markdown
![OKE 구성도](architecture.png)
```

파일 이름에는 영문 소문자, 숫자와 하이픈 사용을 권장합니다. 비밀번호, 인증 키, 개인 IP, 이메일과 계정 정보가 이미지에 포함되지 않았는지 반드시 확인합니다.

## 6. 로컬 미리보기

Hugo Extended와 Go가 설치된 환경에서 저장소 루트로 이동한 뒤 실행합니다.

```bash
hugo server --buildDrafts --navigateToChanged
```

터미널에 출력된 로컬 주소를 브라우저에서 엽니다. 저장할 때마다 페이지가 자동으로 다시 빌드됩니다.

확인 항목:

- 제목과 경로가 올바른가
- Docs 또는 Series의 올바른 위치에 표시되는가
- Series의 목차 순서가 올바른가
- 이미지, 표, 코드 블록과 내부 링크가 정상인가
- 모바일 폭에서도 내용을 읽을 수 있는가
- 민감정보가 포함되지 않았는가

## 7. 공개 전 검증

검수가 끝나면 `draft`를 `false`로 변경합니다.

```yaml
draft: false
```

전체 사이트를 다시 빌드하고 이관 검증을 실행합니다.

```bash
hugo --gc --minify --cleanDestinationDir
python3 scripts/validate_build.py
```

`public/`은 Hugo가 자동으로 만드는 결과물이므로 직접 수정하거나 Git에 추가하지 않습니다.

## 8. Git으로 게시하기

공식 저장소 이관이 끝난 뒤 다음 순서로 게시합니다.

```bash
git status
git add content/docs/guide-lab/oke-version-upgrade
git commit -m "Add OKE version upgrade guide"
git push origin main
```

Series 문서라면 실제 Series 경로를 `git add`에 사용합니다. `main` 브랜치에 push하면 GitHub Actions가 Hugo 사이트를 빌드하고 GitHub Pages에 배포합니다.

공식 전환 전에는 `migration/hextra-blog` 브랜치에서만 검수하고, 최종 승인 없이 `main`에 병합하지 않습니다. 공식 전환 후에는 일반 게시물을 작업 브랜치와 Pull Request로 검수하거나, 확인이 끝난 작은 변경을 `main`에 직접 push할 수 있습니다.

## 9. 게시 후 확인

GitHub Actions가 성공한 뒤 다음을 확인합니다.

- 새 문서의 실제 URL이 열리는가
- 왼쪽 메뉴와 상단 경로가 올바른가
- 이미지와 내부 링크가 정상인가
- 검색에서 새 문서를 찾을 수 있는가
- 이전 글과 다음 글 이동이 올바른가

게시 후 URL을 변경해야 한다면 기존 URL을 `aliases`에 추가한 뒤 이동합니다. 이미 공개된 경로를 별도 조치 없이 삭제하거나 변경하지 않습니다.

## 10. 공식 참고 문서

- [Hugo Archetypes](https://gohugo.io/content-management/archetypes/)
- [Hugo Content Organization](https://gohugo.io/content-management/organization/)
- [Hugo Page Bundles](https://gohugo.io/content-management/page-bundles/)
- [Hugo Front Matter](https://gohugo.io/content-management/front-matter/)
- [Hextra Organize Files](https://imfing.github.io/hextra/docs/guide/organize-files/)

