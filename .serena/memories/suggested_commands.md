# 推奨コマンド一覧

## 必須開発コマンド

### パッケージ管理（必須：uv使用）
```bash
uv sync                    # 依存関係インストール
uv add package-name        # パッケージ追加
uv add --dev package-name  # 開発依存関係追加
```

### コード品質・テスト
```bash
uv run ruff format .       # コードフォーマット
uv run ruff check . --fix  # リント（自動修正）
uv run pytest             # 全テスト実行
uv run pytest tests/test_hello.py::test_hello  # 特定テスト実行
```

### 開発ワークフロー
```bash
uv run pre-commit install  # Git フック設定（初回のみ）
./docker/build.sh         # Docker イメージビルド
./docker/run.sh           # Docker 実行
```

## プロジェクト固有コマンド

### LangExtract実行
```bash
# デフォルト実行（羅生門）
uv run python quick_test.py

# 作品指定
uv run python quick_test.py "走れメロス"
uv run python quick_test.py "坊っちゃん"
uv run python quick_test.py "銀河鉄道の夜"

# モデル指定
uv run python quick_test.py "羅生門" --model "gpt-4o"
uv run python quick_test.py "羅生門" --model "gemini-1.5-flash"
```

### 環境設定
```bash
cp .env.example .env       # 環境変数ファイル作成
# .envファイルを編集してAPIキー設定
```

## システムコマンド（macOS）
```bash
ls -la                     # ファイル一覧
cd directory              # ディレクトリ移動
grep -r "pattern" .       # 文字列検索
find . -name "*.py"       # ファイル検索
git status                # Git状態確認
git add .                 # ファイル追加
git commit -m "message"   # コミット
```

## SuperClaude Framework
```bash
# MCP設定
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project $(pwd)

# SuperClaude コマンド
/analyze                  # コードベース解析
/implement feature        # 機能実装
/improve --wave-mode      # 体系的改善
```

## トラブルシューティング
```bash
uv --version              # uv バージョン確認
python --version          # Python バージョン確認
uv run python -c "import langextract; print('OK')"  # LangExtract動作確認
```