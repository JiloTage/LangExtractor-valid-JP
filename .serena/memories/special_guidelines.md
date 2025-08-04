# 特別なガイドライン・パターン

## プロジェクト固有の重要事項

### API使用上の注意
1. **レート制限**: Gemini無料枠は15リクエスト/分、50リクエスト/日
2. **チャンク処理**: 3000文字超は自動分割処理
3. **エラーハンドリング**: JSON解析エラー時は自動リトライ
4. **モデル選択**: 環境変数 > コマンド引数 > デフォルト順

### 日本語処理の特殊性
1. **文字エンコーディング**: 青空文庫 Shift_JIS → UTF-8変換
2. **ルビ記法処理**: `｜漢字《かんじ》` → `漢字` 自動変換
3. **注釈除去**: `［＃...］` 形式の編集注釈を自動除去
4. **文境界検出**: `[。！？\n]` での文分割

### SuperClaude Framework統合
- MCP Serena: インテリジェントコードナビゲーション
- Wave モード: 複雑操作の多段階実行
- Persona システム: ドメイン特化AI行動パターン
- Token効率化: `--uc` フラグでの圧縮出力

## 設計パターン

### エラー処理パターン
```python
try:
    # LangExtract実行
    result = lx.extract(...)
except json.JSONDecodeError:
    # チャンクサイズ縮小してリトライ
    smaller_chunks = self._chunk_text(text, 1000)
    # 部分処理継続
except Exception as e:
    if "429" in str(e):
        # レート制限時は60秒待機
        time.sleep(60)
        # リトライ
```

### 環境変数管理パターン
```python
# 優先順位: 明示的引数 > 環境変数 > デフォルト
model_id = explicit_model or os.getenv("LANGEXTRACT_MODEL", "gemini-2.0-flash-exp")
api_key = os.getenv("GOOGLE_API_KEY" if "gemini" in model_id else "OPENAI_API_KEY")
```

### データクラス活用パターン
```python
@dataclass
class Character:
    name: str
    gender: str
    age: Optional[str]
    # ... 他フィールド
    
    def to_dict(self):
        return asdict(self)
```

## 開発時の注意点

### パフォーマンス考慮
- 大容量テキスト（坊っちゃん、銀河鉄道の夜）は30+チャンクに分割
- API呼び出し間に2秒待機でレート制限回避
- 重複除去アルゴリズムで結果の一意性保証

### デバッグのベストプラクティス
1. **段階的実行**: 小さな作品（羅生門）でテスト → 大きな作品へ
2. **モデル比較**: 複数モデルでの結果比較で品質確認
3. **ログ確認**: LangExtractの進行状況表示で問題箇所特定
4. **結果検証**: HTMLレポートでの視覚的確認

### セキュリティ考慮
- APIキーは.envファイルで管理（.gitignore済み）
- 本番環境では.env.exampleをコピーして設定
- APIキー誤コミット防止策実装済み

## 既知の制限・制約
1. **LangExtract依存**: Google/OpenAI APIの可用性に依存
2. **青空文庫URL**: 作品URLの変更可能性（定期確認推奨）
3. **JavaScript未対応**: 動的コンテンツ含むページは未対応
4. **言語制限**: 日本語特化設計（他言語は要カスタマイズ）