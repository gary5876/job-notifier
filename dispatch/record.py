"""
작업기록 — 무엇을 찾았고 무엇을 보냈는지 기록한다.

- data/seen.json : 이미 전송한 공고의 지문(중복 방지). URL 기준.
- data/history/YYYY-MM-DD.md : 날짜별 전송 이력 (사람이 읽는 운영 로그).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SEEN_PATH = DATA / "seen.json"
LOGS_DIR = DATA / "history"

KST = timezone(timedelta(hours=9))


def _now() -> datetime:
    return datetime.now(KST)


def job_key(job: dict) -> str:
    """공고를 식별하는 안정적 키. URL 우선, 없으면 회사+제목 해시."""
    url = (job.get("url") or "").strip().rstrip("/").lower()
    if url:
        return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]
    basis = f"{job.get('company','')}|{job.get('title','')}".lower()
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()[:16]


def load_seen() -> dict:
    if SEEN_PATH.exists():
        with open(SEEN_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(seen: dict) -> None:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)


def filter_new(jobs: list[dict], seen: dict) -> list[dict]:
    """아직 안 보낸 공고만 골라낸다."""
    fresh = []
    for job in jobs:
        key = job_key(job)
        if key not in seen:
            job["_key"] = key
            fresh.append(job)
    return fresh


def mark_sent(jobs: list[dict], seen: dict) -> None:
    """전송한 공고를 seen에 등록."""
    stamp = _now().isoformat(timespec="seconds")
    for job in jobs:
        key = job.get("_key") or job_key(job)
        seen[key] = {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "url": job.get("url", ""),
            "sent_at": stamp,
        }


def write_log(found: int, new: int, sent: int, jobs_sent: list[dict], note: str = "") -> Path:
    """날짜별 마크다운 로그에 이번 실행 결과를 덧붙인다."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    now = _now()
    path = LOGS_DIR / f"{now:%Y-%m-%d}.md"
    lines = [
        f"\n## {now:%H:%M:%S} 실행",
        f"- 조사 발견: {found}건 / 신규: {new}건 / 전송: {sent}건",
    ]
    if note:
        lines.append(f"- 메모: {note}")
    if jobs_sent:
        lines.append("- 전송 공고:")
        for j in jobs_sent:
            track = "🏢" if j.get("track") == "company" else "🔎"
            lines.append(f"  - {track} [{j.get('title','제목없음')}]({j.get('url','')}) — {j.get('company','')}")
    header_needed = not path.exists()
    with open(path, "a", encoding="utf-8") as f:
        if header_needed:
            f.write(f"# 작업기록 {now:%Y-%m-%d}\n")
        f.write("\n".join(lines) + "\n")
    return path
