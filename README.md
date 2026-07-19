# jobs — 구직 알리미

내 조건에 맞는 IT/개발 정규직 일자리를 **국내·해외**에서 찾아 **디스코드**로 알려주는 개인용 도구.

조사(무엇을 찾을지)는 사람/AI가 유연하게, 전송·중복제거·기록은 스크립트가 결정적으로 처리하도록 역할을 나눴다.

## 구성 (3축)

| 폴더 | 역할 |
|------|------|
| `research/` | **조사로직** — 조건에 맞는 공고를 찾는다 (`guide.md` 절차대로 조사 → `data/candidates.json` 생성) |
| `dispatch/` | **전송로직** — 찾은 공고를 디스코드로 보내고, 중복/이력을 기록 |
| `worklog/`  | **작업기록** — 이 프로그램 개발의 결정·진행 기록 (`decision/` `progress/` `scope/` `issue/`) |

보조 폴더:
- `config/` — 사람이 편집하는 설정 (`conditions` / `sources` / `secrets`)
- `data/`   — 실행 산출물 (자동 생성: `candidates.json`, `seen.json`, `history/`)

## 동작 흐름

```
[조사]  conditions·sources 를 읽고 조사  →  data/candidates.json
                          │
[전송]  python dispatch/run.py
          ├─ seen.json 과 대조해 신규만 추림 (중복 제거)
          ├─ 디스코드로 전송 (트랙별 색: 사이트=파랑, 회사=초록)
          └─ seen.json 갱신 + data/history/ 에 이력 기록
```

조사는 두 트랙으로 나뉜다 (`config/sources.yaml` 에서 `track` 으로 구분):
- **트랙1 (site)**: 채용 사이트 넓게 검색 — 국내(원티드·점핏·잡코리아·사람인) + 해외(LinkedIn·Indeed·Wellfound) + 원격(WWR·RemoteOK)
- **트랙2 (company)**: 관심 회사 채용 페이지 직접 모니터링

## 설치

```bash
git clone https://github.com/gary5876/job-notifier.git
cd job-notifier
pip install requests pyyaml
```

## 설정 (처음 한 번)

1. **시크릿** — 예시를 복사해 실제 디스코드 웹훅 URL 입력:
   ```bash
   cp config/secrets.example.yaml config/secrets.yaml
   # config/secrets.yaml 을 열어 webhook_url 채우기
   ```
   > `secrets.yaml` 은 `.gitignore` 처리되어 커밋되지 않습니다. **웹훅 URL을 저장소에 올리지 마세요.**
2. **구직 조건** — `config/conditions.yaml` 에서 직무·지역(kr/global/remote)·경력·기술스택·희망연봉 등 채우기
3. **조사 대상** — `config/sources.yaml` 에서 조사할 사이트/회사 확정

## 사용

```bash
# 0) 전송 채널 연결 확인 (테스트 메시지 1건 발송)
python dispatch/send.py --test

# 1) 조사
#    research/guide.md 절차대로 조건에 맞는 공고를 수집해 data/candidates.json 저장
#    (AI 에이전트에게 "채용공고 조사해줘"로 맡기거나, 같은 스키마로 직접 작성)

# 2) 전송 — 신규 공고만 디스코드로
python dispatch/run.py --dry-run   # 먼저 미리보기 (전송 안 함)
python dispatch/run.py             # 실제 전송 + 기록
```

## 요구 사항
- Python 3.13+
- 패키지: `requests`, `PyYAML`

## 참고
개인용 도구입니다. `data/` 의 실행 산출물과 `config/secrets.yaml` 은 저장소에 포함되지 않습니다.
