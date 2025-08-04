# コードスタイル・規約

## 必須ルール（CLAUDE.md より）
1. **パッケージ管理**: `uv add` のみ使用、`pip install` 禁止
2. **型ヒント**: すべての関数に必須
3. **ドキュメント**: Google スタイルのdocstring
4. **Git コミット**: Conventional Commits形式（feat:, fix:, docs:）
5. **テスト**: 新機能には必ずテスト、バグ修正には回帰テスト

## Ruff設定詳細

### 基本設定
- **行長**: 100文字
- **ターゲット**: Python 3.12
- **規約**: Google docstring convention

### 有効化ルール
- **ANN**: 型アノテーション必須
- **B**: flake8-bugbear（バグ検出）
- **D**: pydocstyle（docstring）
- **E/W**: pycodestyle（コード品質）
- **F**: pyflakes（構文エラー）
- **I**: isort（import順序）
- **PTH**: pathlib推奨
- **RUF**: ruff固有ルール
- **SIM**: flake8-simplify（簡潔化）
- **UP**: pyupgrade（Python更新）

### 除外ルール
- **D1**: public docstring（一部除外）
- **ANN401**: Any型使用許可
- **COM812/819**: カンマ関連
- **Q0**: シングルクォート許可

## プロジェクト構造規約
```
src/
├── aozora_fetcher.py      # 青空文庫テキスト取得
├── text_extractor.py      # LangExtract実行・情報抽出
├── result_analyzer.py     # 結果分析・可視化
└── my_package/           # 汎用パッケージ（テンプレート）
```

## 日本語対応
- UTF-8エンコーディング
- 青空文庫のShift_JIS→UTF-8変換対応
- ルビ記法除去：`｜漢字《かんじ》` → `漢字`