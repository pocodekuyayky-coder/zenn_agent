"""
記事生成モジュール - Gemini AIで1000〜2000文字のZenn記事を生成
"""

import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

PROMPT = """
あなたはZennで人気の科学・テクノロジーライターです。
以下の条件で記事を1本書いてください。

## ジャンル
{genre_name}

## 参考ニュース
{news_summary}

## 執筆条件
- 文字数: 1000〜2000文字
- 読者: テクノロジーに関心がある一般ビジネスパーソン
- トーン: 親しみやすく知的。専門用語は噛み砕いて説明する
- 構成:
  1. 読者を引き込む書き出し
  2. メインテーマの解説
  3. 具体的なトピックの深掘り
  4. まとめ・読者へのメッセージ

## 出力形式（この形式のみ、他の文言は不要）
TITLE: [タイトル（40文字以内）]
BODY:
[本文。見出しは##を使用。]
TOPICS: [topic1,topic2,topic3（英語小文字、Zennの有効トピックのみ）]
EMOJI: [1文字の絵文字]
"""

VALID_TOPICS = {
    "energy": ["energy", "sustainability", "tech"],
    "ai": ["ai", "machinelearning", "tech", "python"]
}

def generate_article(genre: dict, news_items: list[dict]) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    if news_items:
        news_summary = "\n".join([
            f"・{i.get('title','')}: {i.get('summary','')}"
            for i in news_items[:5]
        ])
    else:
        news_summary = f"キーワード参考: {', '.join(genre['keywords'][:5])}"

    prompt = PROMPT.format(
        genre_name=genre["name"],
        news_summary=news_summary
    )

    logger.info("Gemini APIで記事生成中...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=4096,
        )
    )

    article = _parse(response.text, genre)
    logger.info(f"タイトル: {article['title']} / {len(article['body'])}文字")
    return article

def _parse(raw: str, genre: dict) -> dict:
    title, body, emoji = "", "", "📝"
    topics = VALID_TOPICS.get(genre["id"], ["tech"])
    mode = None
    body_lines = []

    for line in raw.strip().split("\n"):
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("BODY:"):
            mode = "body"
        elif line.startswith("TOPICS:"):
            mode = None
            raw_topics = line.replace("TOPICS:", "").strip()
            parsed = [t.strip() for t in raw_topics.split(",") if t.strip()]
            if parsed:
                topics = parsed[:5]
        elif line.startswith("EMOJI:"):
            mode = None
            emoji = line.replace("EMOJI:", "").strip()[:1] or "📝"
        elif mode == "body":
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    if not title:
        title = f"{genre['name']}の最新動向"
    if not body:
        body = raw.strip()

    return {
        "title": title,
        "body": body,
        "topics": topics,
        "emoji": emoji
    }
