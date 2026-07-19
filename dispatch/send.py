"""
전송로직 — 찾은 채용공고를 디스코드로 보낸다.

단독 실행하면 웹훅 연결 테스트 메시지를 보낸다:
    python dispatch/send.py --test

run.py 에서 send_jobs()를 호출해 실제 공고를 전송한다.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "config" / "secrets.yaml"

# 트랙별 임베드 색상
COLOR_SITE = 0x4A90D9      # 트랙1: 채용 사이트 (파랑)
COLOR_COMPANY = 0x2ECC71   # 트랙2: 회사 직접 공고 (초록)


def load_settings() -> dict:
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _job_to_embed(job: dict) -> dict:
    """공고 dict 하나를 디스코드 임베드로 변환."""
    track = job.get("track", "site")
    color = COLOR_COMPANY if track == "company" else COLOR_SITE

    fields = []
    if job.get("company"):
        fields.append({"name": "회사", "value": str(job["company"]), "inline": True})
    if job.get("location"):
        fields.append({"name": "지역", "value": str(job["location"]), "inline": True})
    if job.get("experience"):
        fields.append({"name": "경력", "value": str(job["experience"]), "inline": True})
    if job.get("salary"):
        fields.append({"name": "연봉", "value": str(job["salary"]), "inline": True})
    if job.get("stack"):
        stack = job["stack"]
        stack = ", ".join(stack) if isinstance(stack, list) else str(stack)
        fields.append({"name": "기술스택", "value": stack, "inline": False})

    source = job.get("source", "")
    footer = f"{source}" if source else ""
    if job.get("why"):
        footer = (footer + " · " if footer else "") + f"매칭: {job['why']}"

    embed = {
        "title": (job.get("title") or "제목 없음")[:250],
        "url": job.get("url", ""),
        "color": color,
        "fields": fields,
    }
    if job.get("summary"):
        embed["description"] = str(job["summary"])[:400]
    if footer:
        embed["footer"] = {"text": footer[:2000]}
    return embed


def _post(webhook_url: str, payload: dict) -> None:
    resp = requests.post(webhook_url, json=payload, timeout=15)
    # 429(레이트리밋) 시 안내대로 대기 후 1회 재시도
    if resp.status_code == 429:
        retry_after = resp.json().get("retry_after", 1)
        time.sleep(float(retry_after) + 0.5)
        resp = requests.post(webhook_url, json=payload, timeout=15)
    resp.raise_for_status()


def send_jobs(jobs: list[dict], settings: dict | None = None) -> int:
    """공고 리스트를 디스코드로 전송. 보낸 개수를 반환.

    디스코드 임베드는 메시지당 최대 10개까지 → 배치로 나눠 보낸다.
    """
    if not jobs:
        return 0
    settings = settings or load_settings()
    dc = settings["discord"]
    webhook_url = dc["webhook_url"]
    username = dc.get("username", "구직 알리미")
    max_per_run = int(dc.get("max_per_run", 15))

    jobs = jobs[:max_per_run]
    sent = 0
    for i in range(0, len(jobs), 10):
        batch = jobs[i : i + 10]
        payload = {
            "username": username,
            "embeds": [_job_to_embed(j) for j in batch],
        }
        _post(webhook_url, payload)
        sent += len(batch)
        time.sleep(1)  # 배치 간 여유
    return sent


def send_text(message: str, settings: dict | None = None) -> None:
    """단순 텍스트 메시지 전송 (요약/헤더용)."""
    settings = settings or load_settings()
    dc = settings["discord"]
    payload = {"username": dc.get("username", "구직 알리미"), "content": message[:1900]}
    _post(dc["webhook_url"], payload)


def _test() -> None:
    send_text("✅ 구직 알리미 연결 테스트 — 이 메시지가 보이면 전송로직 정상 작동 중입니다.")
    print("테스트 메시지 전송 완료.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="디스코드 전송로직")
    parser.add_argument("--test", action="store_true", help="웹훅 연결 테스트 메시지 전송")
    args = parser.parse_args()
    if args.test:
        _test()
    else:
        print("사용법: python dispatch/send.py --test", file=sys.stderr)
        sys.exit(1)
