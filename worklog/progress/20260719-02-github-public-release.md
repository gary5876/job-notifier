# progress — GitHub 공개 저장소 게시

## 한 것
- 공개 전 민감정보 스캔: 웹훅 URL은 `config/secrets.yaml`(gitignore)에만 존재 확인.
- `config/secrets.example.yaml` 추가 (실제 값 없는 형식 템플릿).
- README 보완: 설치·시크릿 복사·사용법·요구사항 정리.
- `git init`(jobs 폴더 한정) → 커밋 → **public** 저장소 생성/푸시.
  - 저장소: https://github.com/gary5876/job-notifier (계정 gary5876)
- 푸시 후 원격 검증: `config/`에 `secrets.yaml` 없음(404), `secrets.example.yaml`만 존재.

## gitignore 로 제외된 것
- `config/secrets.yaml` (웹훅)
- `data/candidates.json`, `data/seen.json`, `data/history/*` (실행 산출물)
- `__pycache__`

## 메모
- fundamental 루트가 아닌 `jobs/` 하위에 `.git` 생성 → CLAUDE.md 규칙 위반 아님.
- 기본 브랜치명이 `master`로 생성됨. 필요시 `main`으로 변경 고려.
