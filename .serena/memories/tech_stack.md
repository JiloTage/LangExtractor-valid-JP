# 技術スタック

## 言語・ランタイム
- **Python 3.12+**: メイン言語（必須バージョン）
- **uv**: 高速パッケージマネージャー（pip使用禁止）

## コア依存関係
- **langextract**: Google LangExtractライブラリ（情報抽出）
- **requests**: HTTP通信（青空文庫からのテキスト取得）
- **beautifulsoup4**: HTML解析（青空文庫のテキスト抽出）
- **pandas**: データ処理・CSV出力
- **plotly**: データ可視化（HTMLレポート）
- **python-dotenv**: 環境変数管理

## 開発ツール
- **pytest**: テストフレームワーク
- **ruff**: リンター・フォーマッター（100文字行長制限）
- **pre-commit**: Git フック（自動品質チェック）

## 外部サービス
- **Gemini API**: Google のLLMサービス（デフォルト）
- **OpenAI API**: GPT-4など（オプション）
- **青空文庫**: 日本の古典文学デジタルアーカイブ

## 開発環境
- **Docker**: コンテナ化対応
- **Devcontainer**: VS Code開発環境
- **SuperClaude Framework**: AI支援開発フレームワーク
- **Serena MCP**: インテリジェントコードナビゲーション