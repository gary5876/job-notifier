# 조사로직 — 채용공고 조사 절차

이 문서는 **Claude가 매 실행마다 따르는 절차**다. 목적은 조건에 맞는 신규 채용공고를
찾아 `data/candidates.json` 으로 저장하는 것. 저장 후엔 `python dispatch/run.py`가
중복 제거·전송·기록을 담당한다. (조사=Claude, 전송/기록=스크립트 로 역할 분리)

## 입력
- `config/conditions.yaml` — 구직 조건 (직무/지역/경력/기술스택/제외어/민감도)
- `config/sources.yaml` — 조사 대상. `sites`(트랙1) + `companies`(트랙2), 각 항목 `region` 포함
- `data/seen.json` — 이미 보낸 공고 (참고용; 최종 중복 제거는 스크립트가 함)

## 절차

### 0. 조건 로드
`conditions.yaml`을 읽어 검색 키워드를 구성한다.
- `regions`로 대상 지역을 정한다: `kr`(국내) / `global`(해외) / `remote`(원격).
- `sources.yaml`의 각 대상은 `region` 태그가 있으니, `conditions.regions`와 겹치는 것만 조사.
- 예: roles=[백엔드], regions=[kr, remote], skills=[Python] →
  국내 검색 "백엔드 개발자 Python 채용" + 원격 검색 "remote backend python engineer".

### 1. 트랙 1 — 채용 사이트 (넓게)
`sources.yaml`의 `sites` 중 대상 region에 해당하는 것을:
- **WebSearch**로 조건 키워드 + 사이트명 조합 검색
  - 국내(kr): `원티드 백엔드 개발자`, `점핏 Python 백엔드`
  - 해외/원격: `site:linkedin.com/jobs backend engineer remote`, `remoteok python backend`
- 유망한 결과는 **WebFetch**로 상세를 열어 회사/직무/경력/지역/스택/마감일 추출
- JS 렌더링이라 WebFetch로 안 열리면 브라우저 도구(claude-in-chrome)로 크롤링
- 각 공고에 `track: "site"` 부여

### 2. 트랙 2 — 회사 직접 공고 (좁고 정확하게)
`sources.yaml`의 `companies` 각 `url`을:
- **WebFetch**(또는 브라우저)로 열어 현재 열린 포지션 목록 확보
- 조건(직무/스택)에 맞는 포지션만 추출
- 각 공고에 `track: "company"` 부여

### 3. 필터링
조건 대비 각 공고를 판단한다 (`match_mode` 존중):
- `exclude_keywords`에 걸리면 제외
- `experience_years` 범위 밖이면 제외 (명시된 경우)
- **해외 공고**: `overseas.visa_sponsorship_required`가 true면 비자 스폰서 명시 공고만,
  영어 필수인데 `overseas.languages`에 영어 없으면 제외
- `strict`=조건 대부분 충족만 / `normal`=핵심 직무 일치 / `loose`=관련성 있으면 포함
- 각 공고에 `why`(왜 매칭됐는지 한 줄)를 붙인다.

### 4. 저장
아래 스키마로 `data/candidates.json` 에 저장. (기존 파일은 덮어씀)

```json
{
  "jobs": [
    {
      "title": "백엔드 개발자 (Python)",
      "company": "토스",
      "url": "https://toss.im/career/job-detail?...",
      "location": "서울 강남",
      "region": "kr",
      "experience": "3~7년",
      "salary": "회사내규",
      "stack": ["Python", "Django", "AWS"],
      "summary": "결제 시스템 백엔드. 대용량 트래픽 경험 우대.",
      "track": "company",
      "source": "toss.im",
      "why": "직무=백엔드 일치, 스택 Python 포함"
    }
  ]
}
```

필수 필드: `title`, `url`, `track`. 나머지는 있으면 채우고 없으면 생략.
`url`은 **공고 상세 페이지**여야 한다(중복 제거·클릭 이동의 기준).

### 5. 전송
저장 후:
```
python dispatch/run.py            # 신규만 디스코드로 전송 + 기록
python dispatch/run.py --dry-run  # 먼저 확인만
```

## 주의
- URL은 최대한 **영구 상세 링크**로. 검색결과 리다이렉트 URL은 피한다(중복 판정 흔들림).
- 확실치 않은 공고는 버리기보다 `why`에 불확실성을 명시하고 `loose`에서만 포함.
- 한 번에 너무 많으면 도배됨 → 스크립트가 `max_per_run`으로 자르지만, 조사 단계에서도
  관련성 높은 순으로 정렬해 두면 좋다.
