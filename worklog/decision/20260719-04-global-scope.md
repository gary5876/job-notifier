# decision — 국내 + 해외 조사 범위

## 무엇을
조사 대상을 국내에 한정하지 않고 **해외 채용도 포함**한다.
- `conditions.yaml`에 `regions: [kr, global, remote]` + `overseas`(비자/언어) 항목 추가.
- `sources.yaml`의 각 대상에 `region` 태그(kr/global/remote) 부여.
  - 해외: LinkedIn, Indeed, Wellfound
  - 원격: We Work Remotely, RemoteOK
- 각 공고에 `region` 필드를 남겨 디스코드에서 국내/해외 구분 가능.

## 왜
- 사용자가 "한국뿐 아니라 해외 직업도 살펴본다"고 명시.
- 해외는 비자 스폰서·언어 요건이 매칭에 중요 → conditions에 별도 항목으로 분리해 필터링.

## 열린 질문 (issue로 추적 필요)
- 실제 타겟 국가/지역? (미국·일본·유럽·동남아 등)
- 원격만 볼지, 현지 이주까지 열어둘지?
→ conditions.yaml 채울 때 확정.
