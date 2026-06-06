"""
zenn_agent - 水素・核融合・新エネルギー・AI分野の記事を自動生成してZennに投稿するエージェント
"""

import os
import logging
from datetime import datetime

from news_collector import collect_news
from article_generator import generate_article
from zenn_publisher import publish_to_zenn
from duplicate_checker import is_duplicate, save_posted

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

GENRES = [
    {
        "id": "energy",
        "name": "水素・核融合・新エネルギー",
        "keywords": [
            "水素エネルギー", "核融合炉", "再生可能エネルギー",
            "グリーン水素", "核融合発電", "太陽光発電 最新",
            "洋上風力 日本", "アンモニア燃料", "水電解", "小型核融合"
        ],
        "topics": ["energy", "tech"],
        "emoji": "⚡"
    },
    {
        "id": "ai",
        "name": "AI・人工知能",
        "keywords": [
            "生成AI 最新", "大規模言語モデル", "AI規制",
            "OpenAI", "Google Gemini", "Claude AI",
            "AIエージェント", "機械学習 研究", "AIと社会", "AI活用 ビジネス"
        ],
        "topics": ["ai", "tech"],
        "emoji": "🤖"
    }
]

def select_genre() -> dict:
    """曜日でジャンルを切り替え（月水金=エネルギー、火木土日=AI）"""
    weekday = datetime.now().weekday()
    genre = GENRES[0] if weekday in [0, 2, 4] else GENRES[1]
    logger.info(f"選択ジャンル: {genre['name']}")
    return genre

def main():
    logger.info("=== zenn_agent 開始 ===")

    for key in ["GEMINI_API_KEY", "GITHUB_TOKEN"]:
        if not os.environ.get(key):
            raise EnvironmentError(f"環境変数 {key} が設定されていません")

    genre = select_genre()

    logger.info("① ニュース収集を開始...")
    news_items = collect_news(genre["keywords"])
    if not news_items:
        logger.warning("ニュースが取得できませんでした。キーワードのみで記事生成します。")

    logger.info("② 記事生成を開始...")
    article = generate_article(genre, news_items)
    logger.info(f"生成タイトル: {article['title']}")
    logger.info(f"文字数: {len(article['body'])}文字")

    if is_duplicate(article["title"]):
        logger.warning(f"重複タイトルのためスキップ: {article['title']}")
        return

    logger.info("③ Zennへ公開...")
    publish_to_zenn(article)

    save_posted(article["title"], genre["id"])
    logger.info(f"✅ 投稿完了: {article['title']}")
    logger.info("=== zenn_agent 完了 ===")

if __name__ == "__main__":
    main()
