"""
파이프라인 — 조사 결과를 받아 걸러내고, 디스코드로 보내고, 기록한다.

흐름:
  1) 조사로직(조사 단계)이 data/candidates.json 을 만든다.
     → Claude가 research/guide.md 절차대로 조건에 맞는 공고를 수집해 저장.
  2) 이 스크립트가 candidates.json 을 읽어:
     - seen.json 과 대조해 신규 공고만 추림 (중복 제거)
     - 디스코드로 전송
     - seen.json 갱신 + 날짜별 로그 기록

실행:
    python dispatch/run.py                      # data/candidates.json 사용
    python dispatch/run.py --file 경로.json      # 다른 후보 파일 지정
    python dispatch/run.py --dry-run            # 전송 없이 미리보기
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import record
import send

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CANDIDATES = ROOT / "data" / "candidates.json"


def load_candidates(path: Path) -> list[dict]:
    if not path.exists():
        print(f"[!] 후보 파일이 없습니다: {path}", file=sys.stderr)
        print("    먼저 조사 단계를 실행해 candidates.json 을 만드세요 "
              "(research/guide.md 참고).", file=sys.stderr)
        return []
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # {"jobs": [...]} 또는 [...] 둘 다 허용
    if isinstance(data, dict):
        data = data.get("jobs", [])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="구직 알림 파이프라인")
    parser.add_argument("--file", type=Path, default=DEFAULT_CANDIDATES,
                        help="조사 결과 후보 JSON 경로")
    parser.add_argument("--dry-run", action="store_true",
                        help="전송/기록 없이 무엇을 보낼지만 출력")
    args = parser.parse_args()

    candidates = load_candidates(args.file)
    if not candidates:
        return 1

    seen = record.load_seen()
    fresh = record.filter_new(candidates, seen)

    print(f"조사 발견: {len(candidates)}건 / 신규: {len(fresh)}건")

    if args.dry_run:
        for j in fresh:
            track = "🏢회사" if j.get("track") == "company" else "🔎사이트"
            print(f"  [{track}] {j.get('title','')} — {j.get('company','')} — {j.get('url','')}")
        print("(dry-run: 전송/기록하지 않음)")
        return 0

    if not fresh:
        record.write_log(found=len(candidates), new=0, sent=0, jobs_sent=[],
                         note="신규 공고 없음")
        print("신규 공고 없음. 전송 생략.")
        return 0

    settings = send.load_settings()
    sent_count = send.send_jobs(fresh, settings)

    # 실제 전송된 것(max_per_run 제한 반영)만 기록
    sent_jobs = fresh[: sent_count]
    record.mark_sent(sent_jobs, seen)
    record.save_seen(seen)
    log_path = record.write_log(found=len(candidates), new=len(fresh),
                                sent=sent_count, jobs_sent=sent_jobs)

    print(f"전송 완료: {sent_count}건 → 디스코드")
    print(f"기록: {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
