#!/usr/bin/env python3
"""
Website Change Monitor
指定URLのサイト内容を定期的にチェックし、変更があればDiscordに通知する
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

TARGET_URL = "https://www.31sumai.com/attend/X2571/"
STATE_FILE = "state.json"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")


def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_content(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    # スクリプト・スタイル・非表示要素を除去
    for element in soup(["script", "style", "noscript", "meta", "link"]):
        element.decompose()
    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_discord_notification(message: str, webhook_url: str) -> None:
    data = {"content": message}
    response = requests.post(webhook_url, json=data, timeout=10)
    response.raise_for_status()
    print(f"Discord通知を送信しました (status: {response.status_code})")


def main() -> None:
    if not DISCORD_WEBHOOK_URL:
        print("ERROR: 環境変数 DISCORD_WEBHOOK_URL が設定されていません", file=sys.stderr)
        sys.exit(1)

    print(f"[{datetime.now(timezone(timedelta(hours=9))).strftime('%Y-%m-%d %H:%M:%S')}] {TARGET_URL} を取得中...")

    try:
        html = fetch_page(TARGET_URL)
    except requests.RequestException as e:
        print(f"ERROR: ページの取得に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    content = extract_content(html)
    current_hash = compute_hash(content)
    state = load_state()
    previous_hash = state.get("hash")
    now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")

    if previous_hash is None:
        print("初回実行: 現在の状態を保存します。")
        state = {
            "hash": current_hash,
            "url": TARGET_URL,
            "last_checked": now,
            "last_changed": None,
        }
        save_state(state)
        # 初回実行時は通知せず終了
        return

    if current_hash != previous_hash:
        print("変更を検知しました！")
        message = (
            "**【サイト変更検知】**\n"
            f"以下のサイトに変更がありました。\n"
            f"URL: {TARGET_URL}\n"
            f"検知日時: {now} (JST)"
        )
        send_discord_notification(message, DISCORD_WEBHOOK_URL)
        state.update(
            {
                "hash": current_hash,
                "last_checked": now,
                "last_changed": now,
            }
        )
        save_state(state)
        print("状態を更新しました。")
    else:
        print("変更なし。")
        state["last_checked"] = now
        save_state(state)


if __name__ == "__main__":
    main()
