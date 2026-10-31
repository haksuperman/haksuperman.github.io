# 뭉게뭉게 학수의 클라우드 세상

`haksuperman.github.io`의 Hugo/Hextra 기반 기술 블로그 저장소입니다.

## 원칙

- 기존 공식 사이트는 최종 승인 전까지 변경하지 않습니다.
- 문서는 `Docs`에서 제목순으로 탐색합니다.
- 강의와 책을 따라 학습한 글은 `Series`에서 목차 순서로 탐색합니다.
- 독립적인 구축 및 테스트 절차는 `Docs / Guide & Lab`에 둡니다.
- 기존 `/posts/.../` 주소는 Hugo alias로 보존합니다.
- 기술 스택은 상위 카테고리 대신 태그로 유지합니다.

## 로컬 확인

Hugo Extended와 Go를 설치한 뒤 다음 명령을 실행합니다.

```bash
hugo server --buildDrafts --navigateToChanged
```

새 게시물 생성, 이미지 배치와 초안 검수는 [게시물 작성 가이드](AUTHORING.md)를 따릅니다. Pull Request 검증, GitHub Pages 배포, 실패 대응과 롤백은 [운영 및 복구 가이드](OPERATIONS.md)를 따릅니다.

Docs 문서는 다음처럼 생성합니다.

```bash
SLUG=oke-version-upgrade
hugo new content --kind docs "docs/guide-lab/${SLUG}/index.md"
```

Series 문서는 다음처럼 생성합니다.

```bash
SERIES_NAME=aws-security
SEQUENCE_SLUG=11-01-new-security-topic
hugo new content --kind series "series/${SERIES_NAME}/${SEQUENCE_SLUG}/index.md"
```

## 마이그레이션

전체 132개 게시물의 분류·원문 해시·기존 URL 계획표를 다시 생성합니다.

```bash
python3 scripts/build_migration_plan.py \
  --source /path/to/haksuperman.github.io/site
```

1차 Docs 이관 명세를 만든 뒤 게시물을 재생성합니다. 원본 해시가 계획 시점과 다르면 이관을 중단합니다.

```bash
python3 scripts/build_ready_docs_manifest.py

python3 scripts/migrate_posts.py \
  --source /path/to/haksuperman.github.io/site \
  --target . \
  --manifest migration/ready-docs.json
```

변환 과정에서는 기존 `/posts/.../` 주소를 alias로 보존하고, 이미지를 각 Hugo page bundle로 복사하며, 공개되어 있던 VPN Pre-Shared Key 값은 자리표시자로 치환합니다.

확정된 Series 묶음은 별도의 명세로 재생성합니다. 정확한 강의·책 출처가 확인되지 않은 문서는 front matter의 `sourceStatus: needs-review`로 추적합니다.

```bash
python3 scripts/build_series_manifest.py

python3 scripts/migrate_posts.py \
  --source /path/to/haksuperman.github.io/site \
  --target . \
  --manifest migration/series-posts.json
```

이관 후에는 Hugo 전체 빌드를 실행한 다음 다음 검증을 통과해야 합니다.

```bash
python3 scripts/validate_build.py
```
