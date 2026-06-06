"""
Zenn公開モジュール - Markdownファイルを生成してgit pushするだけ
"""

import os
import re
import logging
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

ARTICLES_DIR = Path(__file__).parent.parent / "articles"

def publish_to_zenn(article: dict) -> bool:
    """
    ZennのMarkdown形式で記事ファイルを生成し、git pushする。
    Zennはpushを検知して自動でデプロイしてくれる。
    """
    ARTICLES_DIR.mkdir(exist_ok=True)

    # ファイル名生成（日付+スラッグ）
    date_str = datetime.now().strftime("%Y%m%d%H%M")
    slug = _make_slug(article["title"], date_str)
    filepath = ARTICLES_DIR / f"{slug}.md"

    # Zenn形式のMarkdownを生成
    content = _build_zenn_markdown(article, slug)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"記事ファイル生成: {filepath}")

    # git push
    _git_push(filepath, article["title"])

    return True

def _make_slug(title: str, date_str: str) -> str:
    """タイトルからZennのスラッグを生成（英数字とハイフンのみ）"""
    slug = f"auto-{date_str}"
    return slug

def _build_zenn_markdown(article: dict, slug: str) -> str:
    """Zennのフロントマター付きMarkdownを生成"""
    topics = article.get("topics", ["tech"])
    emoji = article.get("emoji", "📝")

    # トピックをZenn形式に変換（最大5つ）
    topics_str = "\n".join([f'  - {t}' for t in topics[:5]])

    content = f"""---
title: "{article['title']}"
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
    """git add, commit, pushを実行"""
    repo_root = Path(__file__).parent.parent

    # git設定
    subprocess.run(
        ["git", "config", "user.email", "zenn-agent@github-actions.com"],
        cwd=repo_root, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Zenn Agent"],
        cwd=repo_root, check=True
    )

    # git remote にトークンを設定
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
