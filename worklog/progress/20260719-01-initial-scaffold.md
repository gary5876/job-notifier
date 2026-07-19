# progress — 초기 뼈대 구축

## 오늘 한 것
- 3축 폴더 구조 확정: `research/` `dispatch/` `worklog/` + `config/` `data/`
- 조사로직: `research/guide.md` (조사 절차 + candidates.json 스키마, 국내/해외 대응)
- 전송로직: `dispatch/send.py` (디스코드 임베드 전송, `--test` 연결 확인)
- 중복제거/운영로그: `dispatch/record.py` (seen.json, `data/history/` 날짜별 로그)
- 메인 실행: `dispatch/run.py` (후보 → 필터 → 전송 → 기록, `--dry-run` 지원)
- 설정: `config/secrets.yaml`(웹훅), `conditions.yaml`, `sources.yaml`(사이트+회사 통합)
- worklog 규칙: 파일/폴더명 영문만, `worklog/<category>/YYYYMMDD-NN-slug.md`

## 미결 (다음)
- [ ] `conditions.yaml` 실제 조건 채우기 (사용자가 채팅으로 제공 예정) — 현재 TODO
- [ ] `sources.yaml` 실제 타겟 사이트/회사·해외 국가 확정
- [ ] 디스코드 웹훅 연결 테스트 (`python dispatch/send.py --test`)
- [ ] 첫 조사 실행 → candidates.json → run.py 전송 e2e 검증
- [ ] (선택) 자동 스케줄 실행 붙이기
