"""
記事生成モジュール - Gemini AIで1000〜2000文字のZenn記事を生成
"""

import os
import time
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

PROMPT = """
あなたはZennで人気の科学・テクノロジーライター「ぽこ」です。
以下の条件で記事を1本書いてください。

## ジャンル
{genre_name}

## 今回のサブトピック
{subtopic_name}

## 今回の切り口
{angle}

## 参考ニュース
{news_summary}

## 執筆条件
- 文字数: 1200〜2000文字
- 読者: テクノロジーに関心がある一般ビジネスパーソン
- トーン: 親しみやすく知的。専門用語は噛み砕いて説明する
- 書き出しは「ライターのぽこです。」で始める
- 今回の切り口を意識した独自の視点・構成にする
- 他の記事と差別化された内容にする
- 構成は切り口に合わせて自由に工夫する（必ずしも同じ構成にしない）
- 太字（**テキスト**）は絶対に使用しない
- 強調したい内容は見出し（##）や箇条書き（-）で表現する
- AIに関する記事の場合、ChatGPTやGeminiだけでなく、Claude、Copilot、Perplexity、Grok、Cursor、Llama、Mistral、DeepSeekなど多様なAIツール・モデルを積極的に取り上げること
- 特定のAIツールに偏らず、複数のサービスや技術を比較・紹介する視点を持つこと

## 出力形式（この形式のみ、他の文言は不要）
TITLE: [タイトル（40文字以内、切り口を反映したキャッチーなもの）]
BODY:
[本文。見出しは##を使用。太字は使用しない。]
TOPICS: [topic1,topic2,topic3（英語小文字のみ、カンマ区切り、最大5つ）]
"""

VALID_TOPICS = {
    "energy": ["energy", "sustainability", "tech", "hydrogen", "nuclear"],
    "ai": ["ai", "machinelearning", "tech", "python", "deeplearning"]
}

def generate_article(genre: dict, subtopic: dict, angle: str, emoji: str, news_items: list[dict]) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    if news_items:
        news_summary = "\n".join([
            f"・{i.get('title','')}: {i.get('summary','')}"
            for i in news_items[:5]
        ])
    else:
        news_summary = f"キーワード参考: {', '.join(subtopic['keywords'][:4])}"

    prompt = PROMPT.format(
        genre_name=genre["name"],
        subtopic_name=subtopic["name"],
        angle=angle,
        news_summary=news_summary
    )

    logger.info("Gemini APIで記事生成中...")
    response = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    max_output_tokens=8192,
                )
            )
            break
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                wait = (attempt + 1) * 30
                logger.warning(f"503エラー。{wait}秒後にリトライ ({attempt+1}/3)...")
                time.sleep(wait)
            else:
                raise

    article = _parse(response.text, genre, emoji)
    logger.info(f"タイトル: {article['title']} / {len(article['body'])}文字")
    return article

def _parse(raw: str, genre: dict, emoji: str) -> dict:
    title, body = "", ""
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
            parsed = [t.strip().lower() for t in raw_topics.split(",") if t.strip()]
            if parsed:
                topics = parsed[:5]
        elif mode == "body":
            # 太字記法を除去
            line = line.replace("**", "")
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