"""
ニュース収集モジュール - Gemini AIのグラウンディング機能でWeb検索
"""

import os
import logging
import random
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

def collect_news(keywords: list[str]) -> list[dict]:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    selected = random.sample(keywords, min(3, len(keywords)))
    query = " OR ".join(selected)
    logger.info(f"検索クエリ: {query}")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""以下のトピックに関する最新ニュースを5件、日本語で要約してください。

トピック: {query}

出力形式（各ニュースごと）：
タイトル: [見出し]
概要: [2〜3文の要約]
重要度: [高/中/低]

---
""",
            config=types.GenerateContentConfig(
                temperature=0.3,
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )
        raw_text = response.text
        logger.info(f"ニュース収集完了: {len(raw_text)}文字")
        return _parse(raw_text)
    except Exception as e:
        logger.error(f"ニュース収集エラー: {e}")
        return []

def _parse(text: str) -> list[dict]:
    items = []
    for block in text.strip().split("---"):
        block = block.strip()
        if not block:
            continue
        item = {}
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("タイトル:"):
                item["title"] = line.replace("タイトル:", "").strip()
            elif line.startswith("概要:"):
                item["summary"] = line.replace("概要:", "").strip()
        if "title" in item and "summary" in item:
            items.append(item)
    logger.info(f"ニュース件数: {len(items)}件")
    return items
