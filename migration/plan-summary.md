# 전체 게시물 이관 계획 요약

- 원본 저장소 커밋: `0a4de91468bb512bddf279e5ca8bc880944c077e`
- 원본 게시물: 132개
- Docs 제안: 35개
- Study 제안: 97개
- 현재 이관 완료: 132개
- 남은 게시물: 0개
- 원본 저장소는 읽기 전용으로 유지
- 실제 이관 전에 모든 기존 URL과 원문 해시를 보존

## Docs 분류

| 분류 | 게시물 수 |
|---|---:|
| Theory & Reference | 5 |
| Command & Tool | 4 |
| Guide & Lab | 26 |
| Issue & Troubleshooting | 0 |

## Study 제안

| Study | 게시물 수 | 검토 상태 |
|---|---:|---|
| AWS Security Study | 38 | add-source-metadata |
| AWS Technical Essentials Study | 1 | add-source-metadata |
| Kubernetes Cluster Study | 4 | add-source-metadata |
| Linux Fundamentals Study | 5 | add-source-metadata |
| Network Fundamentals Study | 15 | add-source-metadata |
| Network Security Study | 8 | add-source-metadata |
| OCI Foundations Study | 11 | add-source-metadata |
| Terraform Infrastructure Study | 9 | add-source-metadata |
| Web Security Study | 6 | add-source-metadata |

## 사용자 검토 대기열

| 상태 | 게시물 수 | 의미 |
|---|---:|---|
| ready | 35 | 현재 분류로 바로 이관 가능 |
| add-source-metadata | 97 | Study 출처 정보 필요 |
| confirm-study-boundary-and-source | 0 | Study 여부와 범위 확인 필요 |
| confirm-docs-or-study-based-on-origin | 0 | 강의·책 기반 여부에 따라 Docs/Study 결정 |

## 안전 장치

- `full-plan.json`의 `source_sha256`로 이관 도중 원문 변경 여부를 감지합니다.
- 모든 게시물의 `legacy_url`을 새 문서의 alias로 보존합니다.
- 기존 블로그 파일은 수정하거나 삭제하지 않습니다.
- 제목 통합과 문서 병합은 1:1 이관 및 검증 완료 후 별도 단계에서 수행합니다.
- `destination`이 비어 있는 문서는 최종 영문 slug를 확정한 뒤에만 이관합니다.
