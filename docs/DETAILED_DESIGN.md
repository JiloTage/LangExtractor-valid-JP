# 詳細設計書: 日本語テキスト解析システム

## 1. 青空文庫インターフェース詳細設計

### 1.1 テキスト取得方法

#### 方法1: 青空文庫API (推奨)
```python
import requests
from typing import Optional, Dict
import re

class AozoraAPI:
    BASE_URL = "https://www.aozora.gr.jp/cards"
    
    def get_text_by_id(self, author_id: str, work_id: str) -> str:
        """
        作品IDからテキストを取得
        例: 夏目漱石(000148)の坊っちゃん(000752)
        URL: https://www.aozora.gr.jp/cards/000148/files/752_ruby_2438.html
        """
        # HTMLファイルのURL構築
        url = f"{self.BASE_URL}/{author_id}/files/{work_id}_ruby_*.html"
        # 実際の実装では、ファイル一覧から適切なファイルを選択
        
    def get_text_from_github(self, work_id: str) -> str:
        """
        青空文庫のGitHubミラーから取得（より安定）
        https://github.com/aozorabunko/aozorabunko
        """
        pass
```

#### 方法2: 直接URL指定
```python
def fetch_from_url(self, url: str) -> str:
    """任意のURLからテキスト取得"""
    response = requests.get(url)
    response.encoding = 'shift_jis'  # 青空文庫の文字コード
    return response.text
```

### 1.2 テキスト前処理の詳細

#### ルビ処理パターン
```python
class TextNormalizer:
    # ルビのパターン
    RUBY_PATTERNS = [
        # パターン1: ｜漢字《かんじ》
        (r'｜([^《]+)《[^》]+》', r'\1'),
        # パターン2: 漢字《かんじ》（｜なし）
        (r'([一-龥々]+)《[^》]+》', r'\1'),
        # パターン3: ｜漢字（かんじ）
        (r'｜([^（]+)（[^）]+）', r'\1'),
    ]
    
    # 注釈のパターン
    ANNOTATION_PATTERNS = [
        # ［＃「...」に傍点］
        (r'［＃[^］]+］', ''),
        # ※［＃...］
        (r'※［＃[^］]+］', ''),
    ]
    
    def normalize(self, text: str) -> str:
        """テキストの正規化処理"""
        # 1. ルビの除去
        for pattern, replacement in self.RUBY_PATTERNS:
            text = re.sub(pattern, replacement, text)
            
        # 2. 注釈の除去
        for pattern, replacement in self.ANNOTATION_PATTERNS:
            text = re.sub(pattern, replacement, text)
            
        # 3. 改行・空白の正規化
        text = re.sub(r'\r\n', '\n', text)  # 改行コード統一
        text = re.sub(r'　+', '　', text)   # 全角スペース重複除去
        text = re.sub(r'\n\n+', '\n\n', text)  # 空行の正規化
        
        # 4. 青空文庫ヘッダー・フッターの除去
        text = self._remove_headers_footers(text)
        
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """作品本文以外の部分を除去"""
        lines = text.split('\n')
        
        # 本文開始・終了マーカーを探す
        start_markers = ['-------', '【テキスト中に現れる記号について】']
        end_markers = ['底本：', '※［＃']
        
        # 実装省略
        return '\n'.join(lines[start:end])
```

### 1.3 サンプルテキスト取得関数
```python
# 動作確認用のサンプル作品リスト
SAMPLE_WORKS = {
    "羅生門": {
        "author_id": "000879",  # 芥川龍之介
        "work_id": "127",
        "url": "https://www.aozora.gr.jp/cards/000879/files/127_ruby_150.html"
    },
    "坊っちゃん": {
        "author_id": "000148",  # 夏目漱石
        "work_id": "752",
        "url": "https://www.aozora.gr.jp/cards/000148/files/752_ruby_2438.html"
    },
    "走れメロス": {
        "author_id": "000035",  # 太宰治
        "work_id": "1567",
        "url": "https://www.aozora.gr.jp/cards/000035/files/1567_ruby_4948.html"
    }
}
```

## 2. LangExtract実行エンジン詳細設計

### 2.1 日本語用プロンプトエンジニアリング

#### 基本プロンプト構造
```python
class JapanesePromptTemplates:
    
    CHARACTER_EXTRACTION = """
あなたは日本文学の専門家です。以下の小説から登場人物を抽出してください。

抽出する情報:
1. 人物名（フルネーム、愛称、呼び名すべて）
2. 性別（男性/女性/不明）
3. 年齢（明記されていれば数値、なければ推定：子供/若者/中年/老人）
4. 職業・身分
5. 外見的特徴
6. 性格・人柄（具体的な描写から推測）

注意事項:
- 「私」「僕」などの一人称も人物として扱う
- 同一人物の異なる呼び名は統合する
- 推測の場合は必ず「推定」と明記する
"""

    EMOTION_EXTRACTION = """
テキストから感情表現を抽出してください。

抽出する情報:
1. 感情の種類（喜び、悲しみ、怒り、恐れ、驚き、嫌悪、期待、信頼など）
2. 感情の主体（誰の感情か）
3. 感情の対象（何に対する感情か）
4. 感情の強度（弱い/普通/強い）
5. 原文の該当箇所（正確に引用）

日本語特有の表現に注意:
- 間接的な感情表現（「〜そうだ」「〜らしい」）
- 擬態語・擬音語による感情表現
- 文末表現による感情のニュアンス
"""

    RELATIONSHIP_EXTRACTION = """
登場人物間の関係性を抽出してください。

関係性の種類:
- 家族関係（親子、兄弟、夫婦など）
- 社会的関係（上司部下、師弟、同僚など）
- 個人的関係（友人、恋人、敵対など）

抽出形式:
- 人物A → 関係の種類 → 人物B
- 双方向の場合は両方記載
- 関係性の根拠となる文章を引用
"""
```

#### 実行例（Example）の設計
```python
def create_extraction_examples():
    """LangExtract用の例を作成"""
    
    character_example = {
        "text": "私は猫である。名前はまだ無い。",
        "extracted": [
            {
                "name": "私（猫）",
                "gender": "不明",
                "age": "不明",
                "occupation": "なし（猫）",
                "appearance": "猫",
                "personality": "観察力が鋭い、哲学的"
            }
        ]
    }
    
    emotion_example = {
        "text": "メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。",
        "extracted": [
            {
                "emotion": "怒り",
                "subject": "メロス",
                "target": "王",
                "intensity": "強い",
                "quote": "メロスは激怒した"
            }
        ]
    }
    
    return [character_example], [emotion_example]
```

### 2.2 抽出スキーマの詳細定義

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class Gender(Enum):
    MALE = "男性"
    FEMALE = "女性"
    UNKNOWN = "不明"

class EmotionType(Enum):
    JOY = "喜び"
    SADNESS = "悲しみ"
    ANGER = "怒り"
    FEAR = "恐れ"
    SURPRISE = "驚き"
    DISGUST = "嫌悪"
    TRUST = "信頼"
    ANTICIPATION = "期待"

@dataclass
class Character:
    name: str
    aliases: List[str]  # 別名・愛称
    gender: Gender
    age: Optional[str]
    occupation: Optional[str]
    appearance: Optional[str]
    personality: Optional[str]
    first_appearance: int  # 初登場の文字位置

@dataclass
class Emotion:
    type: EmotionType
    subject: str
    target: Optional[str]
    intensity: str  # 弱い/普通/強い
    quote: str
    position: int  # テキスト内の位置

@dataclass
class Relationship:
    person1: str
    person2: str
    relation_type: str
    direction: str  # 一方向/双方向
    evidence: str  # 根拠となる引用
```

### 2.3 チャンク分割戦略

```python
class TextChunker:
    def __init__(self, max_chars: int = 3000, overlap: int = 500):
        """
        max_chars: チャンクの最大文字数
        overlap: チャンク間の重複文字数
        """
        self.max_chars = max_chars
        self.overlap = overlap
    
    def split_by_scenes(self, text: str) -> List[str]:
        """シーン（段落）単位で分割"""
        # 1. 段落で分割
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks
    
    def split_with_context(self, text: str) -> List[Dict[str, any]]:
        """文脈を保持した分割"""
        chunks = self.split_by_scenes(text)
        
        # 各チャンクに文脈情報を付加
        chunk_data = []
        for i, chunk in enumerate(chunks):
            context = {
                "chunk_id": i,
                "text": chunk,
                "previous_summary": self._summarize(chunks[i-1]) if i > 0 else None,
                "position": sum(len(c) for c in chunks[:i])
            }
            chunk_data.append(context)
            
        return chunk_data
```

## 3. 結果分析システム詳細設計

### 3.1 評価メトリクスの定義

```python
class ExtractionMetrics:
    """抽出結果の評価指標"""
    
    def calculate_extraction_stats(self, results):
        return {
            "total_characters": len(results.characters),
            "unique_characters": len(set(c.name for c in results.characters)),
            "emotions_per_character": self._emotions_per_character(results),
            "relationship_density": len(results.relationships) / len(results.characters),
            "extraction_coverage": self._calculate_coverage(results)
        }
    
    def analyze_japanese_specific(self, results):
        """日本語特有の分析"""
        return {
            "honorific_usage": self._analyze_honorifics(results),
            "emotion_indirectness": self._analyze_indirect_emotions(results),
            "name_variations": self._analyze_name_variations(results)
        }
```

### 3.2 可視化の具体的なUI/UX

#### 3.2.1 HTMLレポート生成
```python
class ResultVisualizer:
    def generate_html_report(self, results, original_text):
        """インタラクティブHTMLレポート生成"""
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>LangExtract 日本語解析結果</title>
            <style>
                .character { background-color: #e3f2fd; padding: 2px; cursor: pointer; }
                .emotion { background-color: #fff3e0; padding: 2px; }
                .relationship { text-decoration: underline; }
                .sidebar { position: fixed; right: 0; width: 300px; 
                          height: 100%; overflow-y: scroll; }
            </style>
        </head>
        <body>
            <div class="main-content">
                {annotated_text}
            </div>
            <div class="sidebar">
                <h2>抽出結果サマリー</h2>
                {summary}
            </div>
        </body>
        </html>
        """
        
        annotated = self._annotate_text(original_text, results)
        summary = self._generate_summary(results)
        
        return html_template.format(
            annotated_text=annotated,
            summary=summary
        )
```

#### 3.2.2 ターミナル表示用
```python
def display_results_cli(results):
    """コマンドライン用の結果表示"""
    
    print("="*50)
    print("📚 LangExtract 解析結果")
    print("="*50)
    
    print("\n👤 登場人物:")
    for char in results.characters:
        print(f"  • {char.name} ({char.gender.value}, {char.age or '年齢不明'})")
        if char.personality:
            print(f"    性格: {char.personality}")
    
    print("\n💭 感情分析:")
    emotion_counts = {}
    for emotion in results.emotions:
        emotion_counts[emotion.type] = emotion_counts.get(emotion.type, 0) + 1
    
    for emotion_type, count in emotion_counts.items():
        print(f"  • {emotion_type}: {count}回")
    
    print("\n🔗 関係性:")
    for rel in results.relationships:
        print(f"  • {rel.person1} ← {rel.relation_type} → {rel.person2}")
```

### 3.3 比較分析機能

```python
class ComparativeAnalyzer:
    """複数の実行結果を比較"""
    
    def compare_models(self, text, models=["gemini-2.0-flash-exp", "gpt-4"]):
        """異なるモデルでの結果比較"""
        results = {}
        for model in models:
            results[model] = self._run_extraction(text, model)
        
        comparison = {
            "character_overlap": self._calculate_overlap(results, "characters"),
            "emotion_consistency": self._compare_emotions(results),
            "performance": self._compare_performance(results)
        }
        
        return comparison
    
    def analyze_chunk_consistency(self, chunks_results):
        """チャンク間での抽出の一貫性を分析"""
        # 同一人物が異なる名前で抽出されていないか
        # 関係性の矛盾がないか
        # 感情の連続性があるか
        pass
```

### 3.4 クイック実行スクリプト

```python
# quick_test.py
import langextract as lx
from src.aozora_fetcher import AozoraFetcher
from src.text_extractor import JapaneseTextExtractor
from src.result_analyzer import ResultVisualizer

def quick_analyze(work_name="羅生門"):
    """簡単に実行できるテスト関数"""
    
    # 1. テキスト取得
    fetcher = AozoraFetcher()
    text = fetcher.fetch_sample(work_name)
    
    # 2. LangExtract実行
    extractor = JapaneseTextExtractor()
    results = extractor.extract_all(text)
    
    # 3. 結果表示
    visualizer = ResultVisualizer()
    visualizer.display_results_cli(results)
    
    # 4. HTMLレポート生成
    html = visualizer.generate_html_report(results, text)
    with open(f"output_{work_name}.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n📄 レポートを生成しました: output_{work_name}.html")

if __name__ == "__main__":
    quick_analyze()
```