# コードベース構造

## ディレクトリ構造
```
LangExtractor-valid-JP/
├── src/                        # メインソースコード
│   ├── aozora_fetcher.py       # 青空文庫からのテキスト取得
│   ├── text_extractor.py       # LangExtract実行・情報抽出
│   ├── result_analyzer.py      # 結果分析・HTMLレポート生成
│   └── my_package/             # 汎用パッケージ（テンプレート）
├── tests/                      # テストファイル
│   └── test_hello.py           # サンプルテスト
├── data/                       # データ・結果保存
│   └── results/                # 抽出結果（JSON/CSV/HTML）
├── docs/                       # 設計ドキュメント
├── docker/                     # Docker設定
├── .superclaude/              # SuperClaude Framework設定
├── quick_test.py              # メイン実行スクリプト
├── pyproject.toml             # プロジェクト設定・依存関係
├── CLAUDE.md                  # Claude Code向け指示書
└── README.md                  # プロジェクト説明書
```

## 主要コンポーネント

### 1. aozora_fetcher.py
- **クラス**: `AozoraFetcher`, `TextNormalizer`
- **機能**: 青空文庫からのHTTP取得、ルビ・注釈除去、テキスト正規化
- **対応作品**: 羅生門、坊っちゃん、走れメロス、銀河鉄道の夜

### 2. text_extractor.py
- **クラス**: `JapaneseTextExtractor`
- **データクラス**: `Character`, `Emotion`, `Relationship`
- **機能**: LangExtract実行、テキストチャンク化、エラーハンドリング、重複除去
- **API対応**: Gemini, GPT-4

### 3. result_analyzer.py
- **クラス**: `ResultVisualizer`, `ResultAnalyzer`
- **機能**: CLI表示、HTMLレポート生成、CSV/JSON出力、統計分析

### 4. quick_test.py
- **機能**: メイン実行スクリプト、コマンドライン引数処理、統合テスト

## 設定ファイル

### pyproject.toml
- プロジェクト依存関係
- Ruff設定（リント・フォーマット）
- ビルド設定

### .env / .env.example
- APIキー設定（GOOGLE_API_KEY, OPENAI_API_KEY）
- モデル選択（LANGEXTRACT_MODEL）

### .pre-commit-config.yaml
- UV lock更新
- Ruff チェック・フォーマット自動実行

## データフロー
1. **テキスト取得**: 青空文庫 → HTTP取得 → 正規化
2. **情報抽出**: 正規化テキスト → チャンク分割 → LangExtract → 構造化データ
3. **結果出力**: 構造化データ → CLI表示 + ファイル保存（JSON/CSV/HTML）

## 拡張ポイント
- 新作品追加: `SAMPLE_WORKS` 辞書に追加
- 新抽出タイプ: `text_extractor.py` にプロンプト・例・処理追加  
- 新出力形式: `result_analyzer.py` に出力メソッド追加