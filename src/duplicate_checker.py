"""
重複チェックモジュール
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)
HISTORY_FILE = Path(__file__).parent.parent / "data" / "posted_history.json"

def _load() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def is_duplicate(title: str) -> bool:
    title_lower = title.lower().strip()
    for entry in _load():
        past = entry.get("title", "").lower().strip()
        if past == title_lower:
            return True
        words_new = set(title_lower.split())
        words_past = set(past.split())
        if words_new and words_past:
            overlap = len(words_new & words_past) / max(len(words_new), len(words_past))
            if overlap >= 0.8:
                return True
    return False

def save_posted(title: str, genre_id: str):
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    history = _load()
    history.append({
        "title": title,
        "genre_id": genre_id,
        "posted_at": datetime.now().isoformat()
    })
    history = history[-100:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    logger.info(f"投稿履歴保存 (合計: {len(history)}件)")
