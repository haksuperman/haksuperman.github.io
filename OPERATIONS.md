# 블로그 운영 및 복구 가이드

이 문서는 게시물 작성 이후의 Pull Request 검증, GitHub Pages 배포, 실패 대응, 롤백과 로컬 저장소 동기화 절차를 설명합니다.

## 1. 배포 구조

`.github/workflows/pages.yaml`은 다음 조건으로 실행됩니다.

| 실행 조건 | build | validate | deploy |
| --- | --- | --- | --- |
| `main` 대상 Pull Request | 실행 | 실행 | 건너뜀 |
| `main` 브랜치 push 또는 PR 병합 | 실행 | 실행 | 실행 |
| 수동 실행(`workflow_dispatch`) | 실행 | 실행 | 건너뜀 |

Pull Request에서는 사이트를 공개하지 않고 Hugo 빌드와 `scripts/validate_build.py` 검증만 수행합니다. 실제 GitHub Pages 배포는 `main` 브랜치가 변경될 때만 수행합니다.

## 2. 원격 저장소 이름 확인

Git 명령을 실행하기 전에 원격 저장소 이름을 확인합니다.

```bash
git remote -v
```

새로 복제한 저장소는 보통 `origin`이지만 현재 로컬 공식 저장소는 `blog`를 사용합니다. 아래 예시는 현재 공식 저장소 기준입니다. `git remote -v`에 `origin`만 표시되면 `REMOTE_NAME=origin`으로 바꿉니다.

## 3. 일상적인 게시 절차

```bash
REMOTE_NAME=blog
git status
git switch main
git pull --ff-only "$REMOTE_NAME" main
git switch -c docs/update-oke-guide
```

문서를 작성하거나 수정한 뒤 로컬에서 확인합니다.

```bash
hugo server --buildDrafts --navigateToChanged
```

검수가 끝나면 `draft: false`로 변경하고 전체 검증을 실행합니다.

```bash
hugo --gc --minify --cleanDestinationDir
python3 scripts/validate_build.py
```

변경 파일만 커밋해 브랜치를 올립니다.

```bash
git status
git add content/docs/guide-lab/oke-version-upgrade
git diff --cached
git commit -m "Describe the document change"
git push -u "$REMOTE_NAME" HEAD
```

GitHub에서 `main` 대상 Pull Request를 생성하거나 GitHub CLI를 사용합니다.

```bash
gh pr create --base main --fill
gh pr checks --watch
```

`build`가 성공한 뒤 변경 내용을 검토하고 병합합니다. 병합 후에는 `main`용 실행에서 `build`와 `deploy`가 모두 성공했는지 확인합니다.

## 4. GitHub Actions 확인

GitHub 화면에서는 저장소의 **Actions → Deploy Hugo site to Pages**에서 확인합니다.

```bash
gh run list --workflow pages.yaml --limit 5
RUN_ID=1234567890
gh run view "$RUN_ID"
gh run view "$RUN_ID" --log-failed
```

정상적인 Pull Request 실행에서는 `build`가 성공하고 `deploy`는 `skipped`로 표시됩니다. `deploy`가 건너뛰어진 것은 오류가 아니라 공개 배포 방지 장치입니다.

## 5. 실패 유형별 대응

### Hugo 설치 또는 모듈 다운로드 실패

- 일시적인 GitHub 또는 네트워크 오류인지 확인합니다.
- 같은 커밋으로 실패한 작업만 한 번 재실행합니다.
- 반복되면 `go.mod`, `go.sum`과 워크플로의 Hugo 버전을 확인합니다.

### Build with Hugo 실패

- Actions의 실패 로그에서 파일 경로와 줄 번호를 확인합니다.
- 로컬에서 `hugo --gc --minify --cleanDestinationDir`를 실행합니다.
- front matter 문법, shortcode, Markdown 링크와 이미지 파일 이름을 확인합니다.
- 브랜치에서 수정해 다시 push하고 새 검증 결과를 기다립니다.

### Validate generated site 실패

- `python3 scripts/validate_build.py`를 로컬에서 실행합니다.
- 게시물 수, 기존 URL alias, 생성된 HTML 링크 중 어떤 검증이 실패했는지 확인합니다.
- 검증 스크립트를 우회하거나 삭제하지 않고 원인이 된 문서 또는 경로를 수정합니다.

### Deploy to GitHub Pages 실패

- `build` 성공 여부를 먼저 확인합니다.
- GitHub Pages 환경의 이전 배포 상태를 확인합니다.
- 일시적인 오류라면 실패한 작업을 한 번 재실행합니다.
- 반복되거나 공개 사이트가 비정상이면 7절의 롤백 절차를 사용합니다.

## 6. 게시 후 확인

배포가 성공하면 다음 항목을 확인합니다.

- `https://haksuperman.github.io/`가 열리는가
- 새 문서의 실제 URL이 열리는가
- Docs 또는 Series의 올바른 위치와 순서에 표시되는가
- 이미지와 내부 링크가 정상인가
- 검색에서 제목을 찾을 수 있는가
- 기존 `/posts/.../` 주소가 새 문서로 이동하는가

## 7. 안전한 롤백

`main`을 강제로 이전 커밋으로 되돌리거나 force push하지 않습니다. 문제가 된 변경을 되돌리는 새 Pull Request를 만듭니다.

GitHub PR 화면에 **Revert** 버튼이 있으면 이를 사용해 되돌림 Pull Request를 생성하는 방법이 가장 간단합니다.

명령줄에서 일반 커밋 또는 squash merge를 되돌릴 때는 다음 절차를 사용합니다.

```bash
REMOTE_NAME=blog
COMMIT_SHA=abc1234
git switch main
git pull --ff-only "$REMOTE_NAME" main
git switch -c rollback/site-deployment
git revert "$COMMIT_SHA"
git push -u "$REMOTE_NAME" HEAD
gh pr create --base main --fill
```

PR이 merge commit으로 병합된 경우에는 부모를 지정합니다.

```bash
MERGE_COMMIT_SHA=abc1234
git revert -m 1 "$MERGE_COMMIT_SHA"
```

최초 Hugo 전환 전 사이트는 다음 태그로 보존되어 있습니다.

```text
pre-hugo-migration-2026-10-31
```

태그를 확인하고 현재 상태와 비교할 수 있습니다.

```bash
git fetch "$REMOTE_NAME" --tags
git show pre-hugo-migration-2026-10-31
git diff pre-hugo-migration-2026-10-31..main
```

이 태그는 복구 기준점입니다. 태그를 `main`에 force push하지 않고 revert PR을 사용합니다.

## 8. 배포 후 로컬 저장소 동기화

로컬 변경이 없으면 다음처럼 동기화합니다.

```bash
REMOTE_NAME=blog
git status
git switch main
git pull --ff-only "$REMOTE_NAME" main
```

`git status`에 수정 파일이 있다면 pull 전에 변경을 별도 브랜치에 보존합니다.

```bash
git switch -c backup/local-before-sync
git add -A
git commit -m "Preserve local changes before Hugo sync"
git switch main
git pull --ff-only "$REMOTE_NAME" main
```

동기화 후 다음을 실행해 새 Hugo 구조가 정상인지 확인합니다.

```bash
hugo --gc --minify --cleanDestinationDir
python3 scripts/validate_build.py
```

## 9. 운영 원칙

- 게시물 크기와 관계없이 작업 브랜치와 Pull Request를 기본으로 사용합니다.
- Pull Request의 build가 실패한 상태로 병합하지 않습니다.
- `public/` 디렉터리를 직접 수정하거나 커밋하지 않습니다.
- 공개된 URL을 변경할 때는 기존 경로를 `aliases`에 남깁니다.
- 비밀번호, API Key, 인증서 개인 키와 VPN Pre-Shared Key를 문서나 이미지에 포함하지 않습니다.
- `main`에 force push하거나 복구를 위해 `git reset --hard`를 사용하지 않습니다.
