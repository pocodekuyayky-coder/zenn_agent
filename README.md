# zenn_agent

水素・核融合・新エネルギー・AI分野の最新ニュースをGemini AIで収集・記事生成し、Zennに毎日自動投稿するエージェントです。

## 仕組み

GitHub Actions が毎日0時に起動 → Gemini AIがニュース収集・記事生成 → articlesフォルダにMarkdownを生成 → git push → Zennが自動デプロイ

## 投稿スケジュール

| 曜日 | ジャンル |
|------|---------|
| 月・水・金 | 水素・核融合・新エネルギー |
| 火・木・土・日 | AI・人工知能 |

## セットアップ

### GitHub Secrets に登録するもの

| シークレット名 | 内容 |
|---|---|
| `GEMINI_API_KEY` | Google AI StudioのAPIキー |

※ `GITHUB_TOKEN` はGitHub Actionsが自動で提供します。

### ZennとGitHubリポジトリの連携

Zennのダッシュボード → GitHub連携 → このリポジトリを選択
