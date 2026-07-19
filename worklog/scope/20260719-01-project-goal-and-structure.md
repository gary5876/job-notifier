# scope — 프로젝트 목표와 구조

## 목표
내 조건에 맞는 IT/개발 정규직 일자리를 **국내·해외 모두** 찾아 나에게 알린다.

## 3대 구성요소 = 3개 폴더
1. **조사로직** → `research/`  : 조건에 맞는 공고를 찾는다 (guide.md 절차 + Claude 실행)
2. **전송로직** → `dispatch/` : 찾은 결과를 디스코드로 보낸다 (send / record / run)
3. **작업기록** → `worklog/`  : 이 개발의 결정·진행 기록 (분류별 하위 폴더)

## 조사 2트랙 (config/sources.yaml 에서 track으로 구분)
- **트랙1 (site)**: 채용 사이트 넓게 검색 — 국내(원티드/점핏/잡코리아/사람인) + 해외(LinkedIn/Indeed/Wellfound) + 원격(WWR/RemoteOK)
- **트랙2 (company)**: 관심 회사 채용 페이지 직접 모니터링

## 폴더 구조
```
jobs/
├── README.md
├── config/       사람이 편집: conditions / sources / secrets(웹훅)
├── research/     ① 조사로직: guide.md
├── dispatch/     ② 전송로직: send.py, record.py, run.py
├── data/         실행 산출물(자동): candidates.json, seen.json, history/
└── worklog/      ③ 작업기록: decision/ progress/ scope/ issue/
```

## 이 범위에서 "안 하는 것" (지금은)
- 자동 스케줄 실행 (나중에 /schedule 또는 /loop로. 지금은 수동)
- 지원서 자동 제출 (조사·알림까지만)
