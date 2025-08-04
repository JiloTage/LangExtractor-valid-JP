# LangExtract 日本語テキスト解析

Google LangExtractライブラリを使用して、青空文庫の日本語小説から構造化情報を抽出するプロジェクトです。

## 🎯 目的

- LangExtractライブラリの日本語テキストに対する挙動調査
- 青空文庫の小説から登場人物、感情、関係性を自動抽出
- 日本語特有の表現（敬語、一人称、間接表現等）への対応確認

## 📋 機能

1. **青空文庫からのテキスト取得**
   - ルビ・注釈の自動除去
   - テキストの正規化処理

2. **構造化情報の抽出**
   - 登場人物（名前、性別、年齢、職業、性格）
   - 感情表現（種類、主体、対象、強度）
   - 人物関係（関係の種類、方向性）

3. **結果の分析・可視化**
   - CLI表示
   - HTMLレポート生成
   - JSON/CSV形式での保存

## 🚀 クイックスタート

### 1. 必要な準備

```bash
# 依存関係のインストール
uv sync
## or pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーとモデルを設定
```

### 2. 実行

```bash
# デフォルト（羅生門、環境変数のモデル）で実行
uv run python quick_test.py

# 作品を指定して実行
uv run python quick_test.py "走れメロス"

# モデルを指定して実行
uv run python quick_test.py "羅生門" --model "gpt-4o"
uv run python quick_test.py "坊っちゃん" --model "gemini-1.5-pro"
```

### 3. 利用可能な作品

- 羅生門（芥川龍之介）
- 坊っちゃん（夏目漱石）
- 走れメロス（太宰治）
- 銀河鉄道の夜（宮沢賢治）

## 📁 プロジェクト構造

```
langextract-jp-analysis/
├── src/
│   ├── aozora_fetcher.py      # 青空文庫からテキスト取得
│   ├── text_extractor.py      # LangExtract実行
│   └── result_analyzer.py     # 結果分析・可視化
├── data/
│   └── results/               # 抽出結果の保存
├── docs/                      # 設計ドキュメント
├── quick_test.py              # クイック実行スクリプト
└── requirements.txt           # 依存関係
```

## 📊 出力例

### CLI出力
```
👤 登場人物:
  • 下人
    性別: 男性
    年齢: 若者
    職業: 使用人（推定）
    性格: 迷いやすい、生きることへの執着

💭 感情分析:
  • 恐れ: 3回
  • 不安: 2回
  • 決意: 1回

🔗 人物関係:
  • 下人 → 老婆: 対立関係
```

### ファイル出力
作品ごとに `data/results/(作品名)/` ディレクトリに保存されます：

- `data/results/羅生門/extraction_results.json` - 全結果
- `data/results/羅生門/characters.csv` - 登場人物一覧
- `data/results/羅生門/emotions.csv` - 感情一覧
- `data/results/羅生門/relationships.csv` - 関係性一覧
- `data/results/羅生門/report.html` - HTMLレポート

## ⚙️ カスタマイズ

### モデルの変更

#### 方法1: .envファイルで設定
```bash
# .envファイルを編集
LANGEXTRACT_MODEL=gpt-4o
```

#### 方法2: コマンドライン引数で指定
```bash
uv run python quick_test.py "羅生門" --model "gpt-4o"
```

## 📝 注意事項

- Gemini APIの利用にはAPIキーが必要です
- 長文の解析には時間がかかる場合があります
- APIの利用制限に注意してください

## 🔍 今後の拡張案

- [ ] より多くの作品への対応
- [ ] 抽出精度の定量評価
- [ ] 複数モデルの比較機能
- [ ] ストリーミング処理対応
- [ ] Web UIの追加

## 🐛 既知の問題と対応

### JSON解析エラー（修正済み）
- **問題**: 大容量テキスト処理時にLangExtractでJSON解析エラーが発生
- **対応**: テキストチャンク化による分割処理とエラーハンドリングを実装
- **効果**: 5000文字以上のテキストでも安定して処理可能

### API制限対応（改善済み）
- **問題**: Gemini APIの無料枠制限（15回/分）によるエラー
- **対応**: レート制限検出と自動リトライ機能を実装
- **効果**: チャンク間待機とエラー時60秒待機でレート制限を回避

### 重複データ対策（実装済み）
- **問題**: チャンク処理で登場人物・関係性の重複が発生
- **対応**: 重複除去アルゴリズムを実装
- **効果**: 名前正規化による精度向上と結果の整合性確保