"""
LangExtractを使用して日本語テキストから情報を抽出するモジュール
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import re
import time
import langextract as lx
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()


class Gender(Enum):
    """性別の列挙型"""
    MALE = "男性"
    FEMALE = "女性"
    UNKNOWN = "不明"


@dataclass
class Character:
    """登場人物のデータクラス"""
    name: str
    gender: str
    age: Optional[str]
    occupation: Optional[str]
    appearance: Optional[str]
    personality: Optional[str]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Emotion:
    """感情のデータクラス"""
    emotion_type: str
    subject: str
    target: Optional[str]
    intensity: str
    quote: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Relationship:
    """関係性のデータクラス"""
    person1: str
    person2: str
    relation_type: str
    direction: str
    evidence: str
    
    def to_dict(self):
        return asdict(self)


class JapaneseTextExtractor:
    """日本語テキスト用のLangExtract実行クラス"""
    
    def __init__(self, model_id: str = None):
        """
        初期化
        Args:
            model_id: 使用するLLMモデル（Noneの場合は環境変数から取得）
        """
        import os
        
        # モデルIDの決定（優先順位: 引数 > 環境変数 > デフォルト）
        if model_id is None:
            model_id = os.getenv("LANGEXTRACT_MODEL", "gemini-2.0-flash-exp")
        
        self.model_id = model_id
        
        # APIキーの取得（モデルに応じて適切なAPIキーを選択）
        if "gpt" in model_id.lower():
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OpenAIモデルを使用する場合はOPENAI_API_KEYが必要です")
        else:
            # Geminiやその他のモデル
            self.api_key = os.getenv("GOOGLE_API_KEY")
            if not self.api_key:
                raise ValueError("GeminiモデルまたはGoogle系モデルを使用する場合はGOOGLE_API_KEYが必要です")
        
        print(f"🤖 使用モデル: {self.model_id}")
        
        # プロンプトテンプレート
        self.prompts = {
            "character": self._get_character_prompt(),
            "emotion": self._get_emotion_prompt(),
            "relationship": self._get_relationship_prompt()
        }
        
        # 抽出例
        self.examples = {
            "character": self._get_character_examples(),
            "emotion": self._get_emotion_examples(),
            "relationship": self._get_relationship_examples()
        }
    
    def extract_all(self, text: str, max_chunk_size: int = 3000, use_scaling: bool = True, 
                   extraction_passes: int = 2, max_workers: int = 10, max_char_buffer: int = 1000) -> Dict[str, List]:
        """
        すべての情報を抽出（大容量テキスト対応・LangExtractのScaling to Longer Documents機能使用）
        Args:
            text: 入力テキスト
            max_chunk_size: テキストチャンクの最大サイズ
            use_scaling: LangExtractのscaling設定を使用するか
            extraction_passes: 抽出パス数（複数回実行で精度向上）
            max_workers: 並列処理ワーカー数
            max_char_buffer: コンテキストバッファサイズ
        Returns:
            抽出結果の辞書
        """
        print("🔍 情報抽出を開始します...")
        
        # LangExtractのScaling機能を使用する場合
        if use_scaling and len(text) > max_chunk_size:
            print(f"🚀 LangExtractのScaling機能を使用して長文処理を実行します")
            print(f"   抽出パス数: {extraction_passes}, 並列ワーカー: {max_workers}, バッファサイズ: {max_char_buffer}")
            
            try:
                # Scaling機能を使用した抽出
                results = {
                    "characters": self._extract_with_scaling(text, "character", extraction_passes, max_workers, max_char_buffer),
                    "emotions": self._extract_with_scaling(text, "emotion", extraction_passes, max_workers, max_char_buffer),
                    "relationships": self._extract_with_scaling(text, "relationship", extraction_passes, max_workers, max_char_buffer)
                }
                
                print("✅ Scaling機能による抽出完了!")
                return results
                
            except Exception as e:
                print(f"⚠️ Scaling機能でエラーが発生: {e}")
                print("   フォールバック: 従来のチャンク処理に切り替えます...")
        
        # テキストが長い場合はチャンク化（従来の方法）
        if len(text) > max_chunk_size:
            print(f"📏 テキストが長いため、{max_chunk_size}文字ずつに分割して処理します")
            chunks = self._chunk_text(text, max_chunk_size)
            print(f"📝 {len(chunks)}個のチャンクに分割しました")
            
            # 各チャンクから抽出してマージ
            all_characters = []
            all_emotions = []
            all_relationships = []
            
            for i, chunk in enumerate(chunks, 1):
                print(f"  🔄 チャンク {i}/{len(chunks)} を処理中...")
                try:
                    chunk_results = {
                        "characters": self._safe_extract_characters(chunk),
                        "emotions": self._safe_extract_emotions(chunk),
                        "relationships": self._safe_extract_relationships(chunk)
                    }
                    
                    all_characters.extend(chunk_results["characters"])
                    all_emotions.extend(chunk_results["emotions"])
                    all_relationships.extend(chunk_results["relationships"])
                    
                    # チャンク間の待機時間（API制限対策）
                    if i < len(chunks):
                        print(f"    ⏳ API制限回避のため2秒待機中...")
                        time.sleep(2)
                    
                except Exception as e:
                    print(f"    ⚠️ チャンク{i}でエラー発生: {e}")
                    # レート制限エラーの場合は長めに待機
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        print(f"    ⏱️ レート制限エラー: 60秒待機してリトライします...")
                        time.sleep(60)
                        try:
                            # リトライ
                            chunk_results = {
                                "characters": self._safe_extract_characters(chunk),
                                "emotions": self._safe_extract_emotions(chunk), 
                                "relationships": self._safe_extract_relationships(chunk)
                            }
                            all_characters.extend(chunk_results["characters"])
                            all_emotions.extend(chunk_results["emotions"])
                            all_relationships.extend(chunk_results["relationships"])
                            print(f"    ✅ リトライ成功")
                        except Exception as retry_e:
                            print(f"    ❌ リトライも失敗: {retry_e}")
                    continue
            
            # 重複除去
            results = {
                "characters": self._deduplicate_characters(all_characters),
                "emotions": all_emotions,  # 感情は重複があっても問題ない
                "relationships": self._deduplicate_relationships(all_relationships)
            }
        else:
            # 通常処理
            results = {
                "characters": self._safe_extract_characters(text),
                "emotions": self._safe_extract_emotions(text),
                "relationships": self._safe_extract_relationships(text)
            }
        
        print("✅ 抽出完了!")
        return results
    
    def extract_characters(self, text: str) -> List[Character]:
        """登場人物を抽出"""
        print("  👤 登場人物を抽出中...")
        
        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["character"],
                examples=self.examples["character"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            # 結果をCharacterオブジェクトに変換
            characters = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                char = Character(
                    name=extraction.extraction_text or attrs.get("name", "不明"),
                    gender=attrs.get("gender", "不明"),
                    age=attrs.get("age"),
                    occupation=attrs.get("occupation"),
                    appearance=attrs.get("appearance"),
                    personality=attrs.get("personality")
                )
                characters.append(char)
            
            print(f"    → {len(characters)}人の登場人物を発見")
            return characters
            
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def extract_emotions(self, text: str) -> List[Emotion]:
        """感情を抽出"""
        print("  💭 感情を抽出中...")
        
        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["emotion"],
                examples=self.examples["emotion"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            emotions = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                emotion = Emotion(
                    emotion_type=attrs.get("emotion_type", "不明"),
                    subject=attrs.get("subject", "不明"),
                    target=attrs.get("target"),
                    intensity=attrs.get("intensity", "普通"),
                    quote=extraction.extraction_text or attrs.get("quote", "")
                )
                emotions.append(emotion)
            
            print(f"    → {len(emotions)}個の感情を発見")
            return emotions
            
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def extract_relationships(self, text: str) -> List[Relationship]:
        """関係性を抽出"""
        print("  🔗 関係性を抽出中...")
        
        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["relationship"],
                examples=self.examples["relationship"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            relationships = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                rel = Relationship(
                    person1=attrs.get("person1", "不明"),
                    person2=attrs.get("person2", "不明"),
                    relation_type=attrs.get("relation_type", "不明"),
                    direction=attrs.get("direction", "一方向"),
                    evidence=extraction.extraction_text or attrs.get("evidence", "")
                )
                relationships.append(rel)
            
            print(f"    → {len(relationships)}個の関係性を発見")
            return relationships
            
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def _chunk_text(self, text: str, max_size: int) -> List[str]:
        """テキストを適切なサイズにチャンク化"""
        chunks = []
        sentences = re.split(r'[。！？\n]', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _safe_extract_characters(self, text: str) -> List[Character]:
        """安全な登場人物抽出（エラーハンドリング付き）"""
        try:
            import json
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["character"],
                examples=self.examples["character"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            characters = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                char = Character(
                    name=extraction.extraction_text or attrs.get("name", "不明"),
                    gender=attrs.get("gender", "不明"),
                    age=attrs.get("age"),
                    occupation=attrs.get("occupation"),
                    appearance=attrs.get("appearance"),
                    personality=attrs.get("personality")
                )
                characters.append(char)
            
            return characters
            
        except json.JSONDecodeError as e:
            print(f"    ⚠️ JSON解析エラー: テキストサイズを縮小してリトライします")
            # より小さなチャンクで再試行
            if len(text) > 1000:
                smaller_chunks = self._chunk_text(text, 1000)
                all_chars = []
                for chunk in smaller_chunks[:3]:  # 最初の3チャンクのみ
                    try:
                        chunk_chars = self._safe_extract_characters(chunk)
                        all_chars.extend(chunk_chars)
                    except:
                        continue
                return all_chars
            return []
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def _safe_extract_emotions(self, text: str) -> List[Emotion]:
        """安全な感情抽出（エラーハンドリング付き）"""
        try:
            import json
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["emotion"],
                examples=self.examples["emotion"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            emotions = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                emotion = Emotion(
                    emotion_type=attrs.get("emotion_type", "不明"),
                    subject=attrs.get("subject", "不明"),
                    target=attrs.get("target"),
                    intensity=attrs.get("intensity", "普通"),
                    quote=extraction.extraction_text or attrs.get("quote", "")
                )
                emotions.append(emotion)
            
            return emotions
            
        except json.JSONDecodeError as e:
            print(f"    ⚠️ JSON解析エラー: テキストサイズを縮小してリトライします")
            if len(text) > 1000:
                smaller_chunks = self._chunk_text(text, 1000)
                all_emotions = []
                for chunk in smaller_chunks[:3]:
                    try:
                        chunk_emotions = self._safe_extract_emotions(chunk)
                        all_emotions.extend(chunk_emotions)
                    except:
                        continue
                return all_emotions
            return []
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def _safe_extract_relationships(self, text: str) -> List[Relationship]:
        """安全な関係性抽出（エラーハンドリング付き）"""
        try:
            import json
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts["relationship"],
                examples=self.examples["relationship"],
                model_id=self.model_id,
                api_key=self.api_key
            )
            
            relationships = []
            for extraction in result.extractions:
                attrs = extraction.attributes
                rel = Relationship(
                    person1=attrs.get("person1", "不明"),
                    person2=attrs.get("person2", "不明"),
                    relation_type=attrs.get("relation_type", "不明"),
                    direction=attrs.get("direction", "一方向"),
                    evidence=extraction.extraction_text or attrs.get("evidence", "")
                )
                relationships.append(rel)
            
            return relationships
            
        except json.JSONDecodeError as e:
            print(f"    ⚠️ JSON解析エラー: テキストサイズを縮小してリトライします")
            if len(text) > 1000:
                smaller_chunks = self._chunk_text(text, 1000)
                all_rels = []
                for chunk in smaller_chunks[:3]:
                    try:
                        chunk_rels = self._safe_extract_relationships(chunk)
                        all_rels.extend(chunk_rels)
                    except:
                        continue
                return all_rels
            return []
        except Exception as e:
            print(f"    ❌ エラー: {e}")
            return []
    
    def _deduplicate_characters(self, characters: List[Character]) -> List[Character]:
        """登場人物の重複除去"""
        seen_names = set()
        unique_chars = []
        
        for char in characters:
            # 名前の正規化（空白除去、小文字化）
            normalized_name = char.name.replace(" ", "").replace("　", "").lower()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                unique_chars.append(char)
        
        return unique_chars
    
    def _deduplicate_relationships(self, relationships: List[Relationship]) -> List[Relationship]:
        """関係性の重複除去"""
        seen_rels = set()
        unique_rels = []
        
        for rel in relationships:
            # 関係性の正規化
            rel_key = f"{rel.person1}_{rel.person2}_{rel.relation_type}"
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                unique_rels.append(rel)
        
        return unique_rels
    
    def _extract_with_scaling(self, text: str, extraction_type: str, extraction_passes: int, 
                             max_workers: int, max_char_buffer: int) -> List:
        """
        LangExtractのScaling機能を使用した抽出
        Args:
            text: 入力テキスト
            extraction_type: 抽出タイプ (character, emotion, relationship)
            extraction_passes: 抽出パス数
            max_workers: 並列処理ワーカー数
            max_char_buffer: コンテキストバッファサイズ
        Returns:
            抽出結果のリスト
        """
        print(f"  📡 {extraction_type}をScaling機能で抽出中...")
        
        try:
            # LangExtractのScaling機能を使用
            result = lx.extract(
                text_or_documents=text,
                prompt_description=self.prompts[extraction_type],
                examples=self.examples[extraction_type],
                model_id=self.model_id,
                api_key=self.api_key,
                # Scaling parameters
                extraction_passes=extraction_passes,  # 複数パスで精度向上
                max_workers=max_workers,             # 並列処理
                max_char_buffer=max_char_buffer      # 小さなバッファで精度向上
            )
            
            # 結果を適切なデータクラスに変換
            if extraction_type == "character":
                items = []
                for extraction in result.extractions:
                    attrs = extraction.attributes
                    char = Character(
                        name=extraction.extraction_text or attrs.get("name", "不明"),
                        gender=attrs.get("gender", "不明"),
                        age=attrs.get("age"),
                        occupation=attrs.get("occupation"),
                        appearance=attrs.get("appearance"),
                        personality=attrs.get("personality")
                    )
                    items.append(char)
            
            elif extraction_type == "emotion":
                items = []
                for extraction in result.extractions:
                    attrs = extraction.attributes
                    emotion = Emotion(
                        emotion_type=attrs.get("emotion_type", "不明"),
                        subject=attrs.get("subject", "不明"),
                        target=attrs.get("target"),
                        intensity=attrs.get("intensity", "普通"),
                        quote=extraction.extraction_text or attrs.get("quote", "")
                    )
                    items.append(emotion)
            
            elif extraction_type == "relationship":
                items = []
                for extraction in result.extractions:
                    attrs = extraction.attributes
                    rel = Relationship(
                        person1=attrs.get("person1", "不明"),
                        person2=attrs.get("person2", "不明"),
                        relation_type=attrs.get("relation_type", "不明"),
                        direction=attrs.get("direction", "一方向"),
                        evidence=extraction.extraction_text or attrs.get("evidence", "")
                    )
                    items.append(rel)
            
            else:
                items = []
            
            print(f"    → Scaling機能で{len(items)}個の{extraction_type}を発見")
            return items
            
        except Exception as e:
            print(f"    ❌ Scaling機能でエラー: {e}")
            raise e
    
    # プロンプトテンプレート
    def _get_character_prompt(self) -> str:
        return """
あなたは日本文学の専門家です。以下の小説から登場人物を抽出してください。

抽出する情報:
- name: 人物名（フルネーム、愛称、呼び名すべて）
- gender: 性別（男性/女性/不明）
- age: 年齢（明記されていれば数値、なければ推定：子供/若者/中年/老人）
- occupation: 職業・身分
- appearance: 外見的特徴
- personality: 性格・人柄（具体的な描写から推測）

注意事項:
- 「私」「僕」などの一人称も人物として扱う
- 同一人物の異なる呼び名は統合する
- 推測の場合は必ず「推定」と明記する
"""
    
    def _get_emotion_prompt(self) -> str:
        return """
テキストから感情表現を抽出してください。

抽出する情報:
- emotion_type: 感情の種類（喜び、悲しみ、怒り、恐れ、驚き、嫌悪、期待、信頼など）
- subject: 感情の主体（誰の感情か）
- target: 感情の対象（何に対する感情か）
- intensity: 感情の強度（弱い/普通/強い）
- quote: 原文の該当箇所（正確に引用）

日本語特有の表現に注意:
- 間接的な感情表現（「〜そうだ」「〜らしい」）
- 擬態語・擬音語による感情表現
- 文末表現による感情のニュアンス
"""
    
    def _get_relationship_prompt(self) -> str:
        return """
登場人物間の関係性を抽出してください。

抽出する情報:
- person1: 人物1の名前
- person2: 人物2の名前
- relation_type: 関係の種類（家族/友人/恋人/上司部下/師弟/敵対など）
- direction: 関係の方向性（一方向/双方向）
- evidence: 関係性の根拠となる文章の引用

関係性の種類の例:
- 家族関係（親子、兄弟、夫婦など）
- 社会的関係（上司部下、師弟、同僚など）
- 個人的関係（友人、恋人、敵対など）
"""
    
    # 抽出例の定義
    def _get_character_examples(self) -> List:
        return [
            lx.data.ExampleData(
                text="私は猫である。名前はまだ無い。",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="character",
                        extraction_text="私",
                        attributes={
                            "name": "私（猫）",
                            "gender": "不明",
                            "age": "不明",
                            "occupation": "なし（猫）",
                            "appearance": "猫",
                            "personality": "観察力が鋭い、哲学的"
                        }
                    )
                ]
            )
        ]
    
    def _get_emotion_examples(self) -> List:
        return [
            lx.data.ExampleData(
                text="メロスは激怒した。必ず、かの邪智暴虐の王を除かなければならぬと決意した。",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="emotion",
                        extraction_text="メロスは激怒した",
                        attributes={
                            "emotion_type": "怒り",
                            "subject": "メロス",
                            "target": "王",
                            "intensity": "強い"
                        }
                    )
                ]
            )
        ]
    
    def _get_relationship_examples(self) -> List:
        return [
            lx.data.ExampleData(
                text="メロスには妹がいる。十六歳で、村の牧人と婚約していた。",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="メロスには妹がいる",
                        attributes={
                            "person1": "メロス",
                            "person2": "妹",
                            "relation_type": "兄妹",
                            "direction": "双方向"
                        }
                    )
                ]
            )
        ]