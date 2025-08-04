# タスク完了時のワークフロー

## 必須実行手順

### 1. コード品質チェック（必須）
```bash
uv run ruff format .       # コードフォーマット実行
uv run ruff check . --fix  # リント + 自動修正
```

### 2. テスト実行（必須）
```bash
uv run pytest             # 全テスト実行
# または特定のテストのみ
uv run pytest tests/test_specific.py
```

### 3. 動作確認（プロジェクト固有）
```bash
# LangExtract動作確認
uv run python quick_test.py "羅生門" --model "gemini-1.5-flash"

# 結果ファイル確認
ls -la data/results/
```

### 4. Pre-commit フック（推奨）
```bash
uv run pre-commit install  # 一度だけ実行
# 以降はgit commitで自動実行
```

## 品質ゲート

### コード品質基準
- ✅ Ruff チェックエラーなし
- ✅ 型ヒント完備
- ✅ Google スタイル docstring
- ✅ 100文字行長制限遵守

### テスト基準
- ✅ 既存テストすべて通過
- ✅ 新機能には対応テスト作成
- ✅ バグ修正には回帰テスト作成

### 機能検証基準（プロジェクト固有）
- ✅ テキスト取得の動作確認
- ✅ LangExtract抽出の動作確認
- ✅ 結果ファイル生成確認
- ✅ APIキー環境変数の動作確認

## Git コミット

### コミットメッセージ形式
```bash
# Conventional Commits形式
git commit -m "feat: 新機能の説明"
git commit -m "fix: バグ修正の説明"
git commit -m "docs: ドキュメント更新"
git commit -m "refactor: リファクタリング"
git commit -m "test: テスト追加"
```

### コミット前チェックリスト
- [ ] コードフォーマット実行済み
- [ ] リントエラー解消済み
- [ ] テスト実行済み
- [ ] 動作確認済み
- [ ] APIクォータ消費量確認済み

## エラー時の対処

### よくあるエラー
1. **API制限エラー**: 待機またはモデル変更
2. **JSONパースエラー**: テキストチャンク化で解決済み
3. **依存関係エラー**: `uv sync` で解決
4. **テストエラー**: 個別にデバッグ・修正

### デバッグコマンド
```bash
uv run python -c "import langextract; print('LangExtract OK')"
uv run python -c "from src.aozora_fetcher import AozoraFetcher; print('Fetcher OK')"
uv run python -c "from src.text_extractor import JapaneseTextExtractor; print('Extractor OK')"
```