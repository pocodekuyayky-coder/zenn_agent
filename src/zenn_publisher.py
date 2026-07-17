"""
Zenn公開モジュール - Markdownファイルを生成してgit pushするだけ
"""

import os
import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ARTICLES_DIR = Path(__file__).parent.parent / "articles"

def publish_to_zenn(article: dict) -> bool:
    ARTICLES_DIR.mkdir(exist_ok=True)

    date_str = datetime.now().strftime("%Y%m%d%H%M")
    slug = f"auto-{date_str}"
    filepath = ARTICLES_DIR / f"{slug}.md"

    content = _build_zenn_markdown(article)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"記事ファイル生成: {filepath}")
    _git_push(filepath, article["title"])
    return True

def _build_zenn_markdown(article: dict) -> str:
    """Zennのフロントマター付きMarkdownを生成"""
    topics = article.get("topics", ["tech"])
    emoji = article.get("emoji", "📝")

    # タイトルのダブルクォートをシングルクォートに置換（YAML崩れ防止）
    title = article['title'].replace('"', "'")

    # トピックを正しいYAML形式に変換
    topics_str = "\n".join([f"  - {t}" for t in topics[:5]])

    content = f"""---
title: "{title}"
emoji: "{emoji}"
type: "idea"
topics:
{topics_str}
published: true
---

{article['body']}
"""
    return content

def _git_push(filepath: Path, title: str):
    repo_root = Path(__file__).parent.parent

    subprocess.run(
        ["git", "config", "user.email", "zenn-agent@github-actions.com"],
        cwd=repo_root, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Zenn Agent"],
        cwd=repo_root, check=True
    )

    token = os.environ["GITHUB_TOKEN"]
    repo_url = f"https://x-access-token:{token}@github.com/pocodekuyayky-coder/zenn_agent.git"
    subprocess.run(
        ["git", "remote", "set-url", "origin", repo_url],
        cwd=repo_root, check=True
    )

    subprocess.run(["git", "add", str(filepath)], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"feat: 自動投稿 - {title}"],
        cwd=repo_root, check=True
    )
    subprocess.run(["git", "push", "origin", "main"], cwd=repo_root, check=True)
    logger.info("git push 完了")