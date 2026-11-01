# Hugo 블로그 운영·배포 가이드

글 등록·수정·분류 변경은 [작성 가이드](AUTHORING.md)를 따릅니다. 이 문서는 작업 브랜치부터 배포 확인·복구까지 설명합니다.

## 1. 저장소와 파일의 역할

| 위치 | 역할 |
| --- | --- |
| `content/posts/docs/<분류>/<이름>/index.md` | Docs 게시물의 본문과 분류 정보 |
| `content/posts/series/<시리즈>/<이름>/index.md` | Series 게시물의 본문과 순서 정보 |
| 글과 같은 폴더 | 이미지와 첨부 파일 |
| `data/navigation.json` | Docs 네 분류와 시리즈의 이름·소개·표시 순서 |
| `content/docs/`, `content/series/` | Docs/Series 첫 화면 |
| `content/_content.gotmpl` | 분류 정의에서 목록 페이지를 만드는 Hugo 템플릿 |
| `./blog` | 등록·분류·미리보기·검사 도우미 |
| `hugo.yaml` | 테마·사이트 주소·검색과 출력 설정 |
| `public/` | Hugo가 만드는 결과물. 편집·커밋하지 않음 |

기존 게시물의 표시 수정일은 이관 및 분류 폴더 재구성처럼 본문 의미를 바꾸지 않은 일괄 작업에 한해 등록일로 보정했습니다. 보정 대상 커밋은 `data/lastmod_baseline.json`에 기록되어 있으며, 이후 실제로 수정된 글에는 새 Git 수정일이 적용됩니다.

게시물 폴더와 글 상단의 `collection`, `docCategory`, `seriesId`, `seriesOrder`는 같은 분류를 가리켜야 합니다. 메뉴와 목록은 글 상단 정보를 사용하고, 게시 전 검사는 실제 폴더도 일치하는지 확인합니다. 분류 변경은 `./blog classify`를 사용하면 글과 이미지를 함께 이동합니다.

## 2. 작업 시작

저장소 루트에서 현재 작업 상태와 원격 저장소 이름을 확인합니다.

```bash
cd /Users/haksu/Projects/haksuperman.github.io/site
git status
git remote -v
```

현재 공식 로컬 저장소의 원격 이름은 `blog`입니다. 새로 복제한 환경에 `origin`만 있다면 아래의 `REMOTE_NAME`을 바꿉니다.

**미완료 변경이 없는 상태에서** 최신 main을 받고 작업 브랜치를 만듭니다.

```bash
REMOTE_NAME=blog
git switch main
git pull --ff-only "$REMOTE_NAME" main
git switch -c docs/update-posts
```

이미 작성 중인 브랜치가 있다면 그 브랜치에서 계속 작업합니다. 다른 변경이 있을 때는 먼저 해당 작업을 별도 커밋이나 브랜치에 보존하세요.

## 3. 작성·검사

```bash
./blog
```

글을 작성하거나 수정한 뒤:

```bash
./blog preview
# 브라우저 확인 후 Ctrl+C로 종료
./blog check
```

도우미 없이 Hugo와 Python으로 직접 확인할 수도 있습니다.

```bash
.venv/bin/python scripts/validate_build.py --sources-only
hugo --gc --minify --cleanDestinationDir --printPathWarnings
.venv/bin/python scripts/validate_build.py
```

Hugo가 설치되지 않은 환경에서는 `./blog check`가 Docker를 사용합니다. Python 의존성 준비는 작성 가이드 1절을 따릅니다.

## 4. PR로 게시 요청

변경한 글 폴더만 추가합니다. 시리즈를 새로 만들거나 표시 이름을 변경했다면 `data/navigation.json`도 추가합니다.

```bash
git status
git add content/posts/docs/guide-lab/oke-cluster
# 분류 정의도 변경했다면 다음 줄 실행
git add data/navigation.json
git diff --cached
git commit -m "docs: update OKE cluster guide"
git push -u "$REMOTE_NAME" HEAD
```

GitHub 저장소에서 현재 브랜치의 **Compare & pull request**를 눌러 `main` 대상 PR을 만듭니다. GitHub CLI가 있다면:

```bash
gh pr create --repo haksuperman/haksuperman.github.io --base main --fill
gh pr checks --watch
```

PR의 **build 성공**과 실제 변경 내용을 확인한 후 병합합니다. PR 생성만으로 사이트에 공개되지는 않습니다. **main에 병합될 때 실제 배포**가 실행됩니다.

## 5. 자동 검사와 배포

GitHub **Actions → Deploy Hugo site to Pages**에서 확인합니다.

| 실행 조건 | 검사·빌드 | 공개 배포 |
| --- | --- | --- |
| main 대상 PR | 실행 | 안 함 |
| main에 병합 또는 push | 실행 | 실행 |
| 수동 워크플로 실행 | 실행 | 안 함 |

검사 내용:

- Docs/Series 및 세부 분류의 필수값·잘못된 조합·없는 시리즈
- 같은 시리즈 안의 순서 중복과 잘못된 날짜·초안 값
- 모든 현재 게시물의 공개 여부와 생성 결과
- 분류별 글 목록·시리즈 목차·현재 위치·이전/다음 연결
- 생성된 HTML의 내부 링크와 이미지·첨부 파일 참조
- 등록된 이전 주소가 현재 글로 연결되는지와 주소 중복·충돌
- 등록·분류 변경 기능의 자동 테스트

CLI로 확인하려면:

```bash
gh run list --repo haksuperman/haksuperman.github.io --workflow pages.yaml --limit 5
gh run view RUN_ID --repo haksuperman/haksuperman.github.io --log-failed
```

배포 성공 후 실제 사이트에서 수정한 글, 메뉴, 이미지, 검색과 모바일 화면을 확인합니다. 내용이 예전으로 보이면 새로고침하고 Actions에서 해당 커밋의 배포 성공 여부를 확인하세요.

## 6. 자주 발생하는 문제

| 현상 | 해결 |
| --- | --- |
| Python 의존성 안내 | 작성 가이드 1절의 가상환경·의존성 설치 실행 |
| Docker 연결 실패 | Docker Desktop을 실행한 뒤 다시 시도 |
| 분류가 없거나 두 종류가 섞임 | `./blog classify <영문-이름>`으로 다시 선택 |
| 시리즈 순서 중복 | 해당 글의 `seriesOrder`를 빈 번호로 변경 |
| 이미지가 없음 | 파일 이름·대소문자·본문 경로 확인 |
| 이전 공유 주소가 404 | 대상 글의 aliases와 공개 상태를 확인하고 ./blog check 실행 |
| 공개할 글이 안 보임 | `draft: false` 여부와 미래 날짜 여부 확인 |
| 목록 이름이 바뀌지 않음 | `data/navigation.json`의 title 수정 여부와 Hugo 재빌드 확인 |
| 공개 빌드에서 초안 링크 오류 | 공개 글에서 초안으로 연결한 링크를 제거하거나 대상 글도 공개 준비 |
| 수정일이 예전 날짜 | lastmod 고정값을 제거하고 해당 파일을 커밋한 뒤 배포 |
| PR build 실패 | 병합 전에 오류 메시지의 파일을 수정하고 다시 push |
| deploy 실패 | Actions 로그와 공개 사이트를 확인하고 일시적 실패이면 작업 재실행 |

초안은 저장해도 공개 빌드에 포함되지 않습니다. 초안의 분류·순서 입력 오류는 미리 검사하지만, 초안 본문의 실제 이미지 렌더링은 `./blog preview`로 확인하세요.

## 7. 복구

배포된 변경에 문제가 있으면 해당 PR의 **Revert**로 되돌림 PR을 만들고 검사 후 병합합니다. 일반 커밋이나 squash merge는 다음처럼 되돌릴 수 있습니다.

```bash
git switch main
git pull --ff-only "$REMOTE_NAME" main
git switch -c rollback/post-update
git revert COMMIT_SHA
git push -u "$REMOTE_NAME" HEAD
gh pr create --repo haksuperman/haksuperman.github.io --base main --fill
```

merge commit은 필요하면 `git revert -m 1 MERGE_COMMIT_SHA`를 사용합니다. main을 강제로 덮어쓰는 대신 되돌림 커밋을 사용합니다.

## 8. 배포 후 동기화

로컬 변경이 없는지 확인한 뒤 main을 갱신합니다.

```bash
git status
git switch main
git pull --ff-only "$REMOTE_NAME" main
```

다음 글을 작성할 때는 새 작업 브랜치를 만듭니다. 게시물 수와 관계없이 같은 작성·검사·PR·배포 절차를 사용합니다.
