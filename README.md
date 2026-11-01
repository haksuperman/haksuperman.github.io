# 뭉게뭉게 학수의 클라우드 세상

Hugo/Hextra 기반 기술 블로그입니다.

- 공개 사이트: https://haksuperman.github.io/
- Docs 게시물: `content/posts/docs/<문서-분류>/<영문-이름>/index.md`
- Series 게시물: `content/posts/series/<시리즈-ID>/<영문-이름>/index.md`
- Docs: Theory & Reference / Command & Tool / Guide & Lab / Issue & Troubleshooting
- Series: 등록된 시리즈별로 순서대로 읽는 게시물
- 글의 소속과 순서는 글 상단 정보로 관리하며, 운영 도우미가 분류에 맞는 폴더로 글과 이미지를 함께 이동합니다.
- 이미지와 첨부 파일은 해당 글과 같은 폴더에 저장합니다.

## 시작하기

Python 3와 Hugo Extended 0.156.0·Go 또는 Docker Desktop을 준비합니다.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./blog
```

Mac에서는 `블로그 관리.command`를 열어 같은 메뉴를 사용할 수 있습니다.

```bash
./blog new       # 새 글과 분류 선택
./blog list      # 기존 글 찾기
./blog preview   # 초안 포함 미리보기
./blog check     # 공개 전 확인
```

- [게시물 등록·수정 가이드](AUTHORING.md): 분류 선택, 본문·이미지 작성, 시리즈와 초안 관리
- [운영·배포 가이드](OPERATIONS.md): 작업 브랜치, PR, 자동 검사, 배포 확인과 복구

`main` 대상 PR에서 검사하고, 병합 후 GitHub Pages에 배포합니다. `public/`은 자동 생성 결과이므로 직접 편집하거나 커밋하지 않습니다.
