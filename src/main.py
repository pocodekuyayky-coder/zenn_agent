"""
zenn_agent - 水素・核融合・新エネルギー・AI分野の記事を自動生成してZennに投稿するエージェント
"""

import os
import random
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
        "subtopics": [
            {"name": "グリーン水素・ブルー水素", "keywords": ["グリーン水素", "ブルー水素", "水電解", "再生可能エネルギー 水素"]},
            {"name": "核融合炉の最新研究", "keywords": ["ITER", "核融合炉", "民間核融合", "プラズマ制御"]},
            {"name": "水素ステーション・燃料電池", "keywords": ["水素ステーション", "燃料電池車", "FCV", "水素インフラ"]},
            {"name": "洋上風力・太陽光発電", "keywords": ["洋上風力", "太陽光発電 最新", "再生可能エネルギー 日本", "蓄電池"]},
            {"name": "アンモニア・合成燃料", "keywords": ["アンモニア燃料", "合成燃料", "e-fuel", "脱炭素 燃料"]},
            {"name": "小型核融合・スタートアップ", "keywords": ["小型核融合", "核融合スタートアップ", "Commonwealth Fusion", "Helion"]},
            {"name": "日本のエネルギー政策", "keywords": ["日本 エネルギー政策", "GX", "脱炭素 日本", "原子力 再稼働"]},
            {"name": "世界のエネルギー革命", "keywords": ["エネルギー転換", "脱炭素 世界", "カーボンニュートラル", "COP"]},
        ],
        "topics": ["energy", "sustainability", "tech"],
        "emoji_list": ["⚡", "🔋", "🌱", "💡", "🌊", "☀️", "🔬", "🌍"]
    },
    {
        "id": "ai",
        "name": "AI・人工知能",
        "subtopics": [
            {"name": "生成AI全般・最新動向", "keywords": ["生成AI 最新", "Claude Anthropic", "Llama Meta", "Mistral AI", "生成AI比較"]},
            {"name": "画像・動画・音声生成AI", "keywords": ["画像生成AI 最新", "Midjourney", "動画生成AI", "音声生成AI", "マルチモーダルAI"]},
            {"name": "AIコーディングツール", "keywords": ["Cursor AI", "GitHub Copilot", "AIコーディング", "Devin AI", "AIプログラミング"]},
            {"name": "AI検索・情報収集ツール", "keywords": ["Perplexity AI", "AI検索エンジン", "Grok xAI", "AI情報収集", "検索AI比較"]},
            {"name": "AIとビジネス活用", "keywords": ["AI ビジネス活用", "生成AI 業務効率化", "AI ROI", "企業AI導入 事例"]},
            {"name": "AI規制・倫理・安全性", "keywords": ["AI規制 最新", "EU AI法", "AIガバナンス", "AI安全性 研究"]},
            {"name": "AIエージェント・自律AI", "keywords": ["AIエージェント 最新", "自律型AI", "マルチエージェント", "AI workflow"]},
            {"name": "医療・ヘルスケアAI", "keywords": ["医療AI 最新", "ヘルスケアAI", "AI診断", "創薬AI"]},
            {"name": "教育・学習へのAI活用", "keywords": ["教育AI", "AI 学習支援", "EdTech AI", "AI家庭教師"]},
            {"name": "オープンソースAI・競争", "keywords": ["オープンソースAI", "AI競争 2025", "中国AI DeepSeek", "Gemini Claude GPT Grok 比較"]},
        ],
        "topics": ["ai", "machinelearning", "tech"],
        "emoji_list": ["🤖", "🧠", "💻", "🔮", "📊", "🚀", "🎯", "✨"]
    }
]

ANGLES = [
    "最新ニュースを噛み砕いて解説する入門記事",
    "ビジネスパーソン向けの実践的活用ガイド",
    "技術の仕組みをわかりやすく深掘りする解説記事",
    "日本と世界の動向を比較する記事",
    "3年後・5年後の未来を予測する記事",
    "メリット・デメリットを公平に分析する記事",
    "成功事例・失敗事例を紹介するケーススタディ",
    "初心者向けQ&A形式の解説記事",
    "専門家の視点で課題と解決策を論じる記事",
    "コスト・経済性の観点から分析する記事",
]

def select_genre_and_subtopic():
    """曜日でジャンルを切り替え、サブトピックと切り口をランダムに選択"""
    weekday = datetime.now().weekday()
    genre = GENRES[0] if weekday in [0, 2, 4] else GENRES[1]
    subtopic = random.choice(genre["subtopics"])
    angle = random.choice(ANGLES)
    emoji = random.choice(genre["emoji_list"])
    logger.info(f"ジャンル: {genre['name']} / サブトピック: {subtopic['name']} / 切り口: {angle}")
    return genre, subtopic, angle, emoji

def main():
    logger.info("=== zenn_agent 開始 ===")

    for key in ["GEMINI_API_KEY", "GITHUB_TOKEN"]:
        if not os.environ.get(key):
            raise EnvironmentError(f"環境変数 {key} が設定されていません")

    genre, subtopic, angle, emoji = select_genre_and_subtopic()

    logger.info("① ニュース収集を開始...")
    news_items = collect_news(subtopic["keywords"])
    if not news_items:
        logger.warning("ニュースが取得できませんでした。キーワードのみで記事生成します。")

    logger.info("② 記事生成を開始...")
    article = generate_article(genre, subtopic, angle, emoji, news_items)
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