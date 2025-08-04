"""
抽出結果の分析と可視化を行うモジュール
"""
import json
from typing import Dict, List, Any
from pathlib import Path
from collections import Counter
import pandas as pd


class ResultAnalyzer:
    """抽出結果を分析するクラス"""
    
    def __init__(self, results: Dict[str, List]):
        """
        初期化
        Args:
            results: 抽出結果の辞書
        """
        self.results = results
        self.characters = results.get("characters", [])
        self.emotions = results.get("emotions", [])
        self.relationships = results.get("relationships", [])
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """抽出結果の統計サマリーを取得"""
        # 感情の種類別カウント
        emotion_counts = Counter(e.emotion_type for e in self.emotions)
        
        # 性別の分布
        gender_counts = Counter(c.gender for c in self.characters)
        
        # 関係性の種類別カウント
        relation_counts = Counter(r.relation_type for r in self.relationships)
        
        stats = {
            "total_characters": len(self.characters),
            "unique_names": len(set(c.name for c in self.characters)),
            "total_emotions": len(self.emotions),
            "emotion_types": dict(emotion_counts),
            "total_relationships": len(self.relationships),
            "relation_types": dict(relation_counts),
            "gender_distribution": dict(gender_counts),
            "characters_with_emotions": len(set(e.subject for e in self.emotions))
        }
        
        return stats
    
    def analyze_japanese_specific(self) -> Dict[str, Any]:
        """日本語特有の分析"""
        analysis = {
            "first_person_pronouns": [],
            "indirect_emotions": [],
            "formal_relationships": []
        }
        
        # 一人称の抽出
        first_person = ["私", "僕", "俺", "わたし", "わたくし", "あたし"]
        for char in self.characters:
            if any(pronoun in char.name for pronoun in first_person):
                analysis["first_person_pronouns"].append(char.name)
        
        # 間接的な感情表現
        indirect_markers = ["そうだ", "らしい", "ようだ", "みたい"]
        for emotion in self.emotions:
            if any(marker in emotion.quote for marker in indirect_markers):
                analysis["indirect_emotions"].append({
                    "subject": emotion.subject,
                    "emotion": emotion.emotion_type,
                    "quote": emotion.quote
                })
        
        # 敬語を含む関係性
        formal_relations = ["上司部下", "師弟", "先輩後輩"]
        for rel in self.relationships:
            if rel.relation_type in formal_relations:
                analysis["formal_relationships"].append({
                    "persons": f"{rel.person1} - {rel.person2}",
                    "type": rel.relation_type
                })
        
        return analysis
    
    def save_results(self, work_name: str = "unknown", output_dir: str = "data/results"):
        """結果をファイルに保存（作品ごとのディレクトリに分けて保存）"""
        # 作品名をファイル名安全な形式に変換
        safe_work_name = work_name.replace(" ", "_").replace("/", "_")
        work_output_path = Path(output_dir) / safe_work_name
        work_output_path.mkdir(parents=True, exist_ok=True)
        
        # JSON形式で保存
        results_dict = {
            "work_name": work_name,
            "characters": [c.to_dict() for c in self.characters],
            "emotions": [e.to_dict() for e in self.emotions],
            "relationships": [r.to_dict() for r in self.relationships],
            "summary": self.get_summary_stats(),
            "japanese_analysis": self.analyze_japanese_specific()
        }
        
        with open(work_output_path / "extraction_results.json", "w", encoding="utf-8") as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)
        
        # CSV形式でも保存
        if self.characters:
            pd.DataFrame([c.to_dict() for c in self.characters]).to_csv(
                work_output_path / "characters.csv", index=False, encoding="utf-8"
            )
        
        if self.emotions:
            pd.DataFrame([e.to_dict() for e in self.emotions]).to_csv(
                work_output_path / "emotions.csv", index=False, encoding="utf-8"
            )
        
        if self.relationships:
            pd.DataFrame([r.to_dict() for r in self.relationships]).to_csv(
                work_output_path / "relationships.csv", index=False, encoding="utf-8"
            )
        
        print(f"📁 結果を保存しました: {work_output_path}")
        return work_output_path


class ResultVisualizer:
    """結果を可視化するクラス"""
    
    def __init__(self, results: Dict[str, List], original_text: str = ""):
        """
        初期化
        Args:
            results: 抽出結果の辞書
            original_text: 元のテキスト
        """
        self.results = results
        self.original_text = original_text
        self.analyzer = ResultAnalyzer(results)
    
    def display_results_cli(self):
        """コマンドライン用の結果表示"""
        results = self.results
        stats = self.analyzer.get_summary_stats()
        
        print("\n" + "="*60)
        print("📊 LangExtract 日本語テキスト解析結果")
        print("="*60)
        
        # 登場人物
        print("\n👤 登場人物:")
        for char in results["characters"]:
            print(f"  • {char.name}")
            if char.gender != "不明":
                print(f"    性別: {char.gender}")
            if char.age:
                print(f"    年齢: {char.age}")
            if char.occupation:
                print(f"    職業: {char.occupation}")
            if char.personality:
                print(f"    性格: {char.personality}")
            print()
        
        # 感情分析
        print("\n💭 感情分析:")
        emotion_types = stats["emotion_types"]
        for emotion_type, count in sorted(emotion_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {emotion_type}: {count}回")
        
        # 代表的な感情表現
        if results["emotions"]:
            print("\n  代表的な感情表現:")
            for i, emotion in enumerate(results["emotions"][:3]):
                print(f"  {i+1}. {emotion.subject}の{emotion.emotion_type}")
                print(f"     「{emotion.quote}」")
        
        # 関係性
        print("\n🔗 人物関係:")
        for rel in results["relationships"]:
            arrow = "↔" if rel.direction == "双方向" else "→"
            print(f"  • {rel.person1} {arrow} {rel.person2}: {rel.relation_type}")
            if rel.evidence:
                print(f"    根拠: 「{rel.evidence[:50]}...」")
        
        # 統計サマリー
        print("\n📈 統計サマリー:")
        print(f"  • 登場人物数: {stats['total_characters']}人")
        print(f"  • 感情表現数: {stats['total_emotions']}個")
        print(f"  • 関係性数: {stats['total_relationships']}個")
        print(f"  • 感情を持つ人物数: {stats['characters_with_emotions']}人")
        
        # 日本語特有の分析
        jp_analysis = self.analyzer.analyze_japanese_specific()
        if jp_analysis["first_person_pronouns"]:
            print(f"\n🗾 日本語特有の要素:")
            print(f"  • 一人称: {', '.join(jp_analysis['first_person_pronouns'])}")
        
        print("\n" + "="*60)
    
    def generate_html_report(self, work_name: str = "unknown", output_dir: str = "data/results", filename: str = "report.html"):
        """HTMLレポートを生成"""
        stats = self.analyzer.get_summary_stats()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8">
    <title>LangExtract 日本語解析結果</title>
    <style>
        body {{
            font-family: 'Hiragino Sans', 'Meiryo', sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #4CAF50;
            margin-top: 30px;
        }}
        .character {{
            background-color: #e3f2fd;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .emotion {{
            background-color: #fff3e0;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .relationship {{
            background-color: #f3e5f5;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background-color: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .quote {{
            font-style: italic;
            color: #666;
            padding-left: 20px;
            border-left: 3px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 LangExtract 日本語テキスト解析結果</h1>
        
        <h2>📈 統計サマリー</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{stats['total_characters']}</div>
                <div>登場人物数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_emotions']}</div>
                <div>感情表現数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_relationships']}</div>
                <div>関係性数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['characters_with_emotions']}</div>
                <div>感情を持つ人物数</div>
            </div>
        </div>
        
        <h2>👤 登場人物</h2>
        {"".join(self._format_character_html(char) for char in self.results['characters'])}
        
        <h2>💭 感情分析</h2>
        {"".join(self._format_emotion_html(emotion) for emotion in self.results['emotions'][:10])}
        
        <h2>🔗 人物関係</h2>
        {"".join(self._format_relationship_html(rel) for rel in self.results['relationships'])}
    </div>
</body>
</html>
"""
        
        # 作品ごとのディレクトリを作成
        safe_work_name = work_name.replace(" ", "_").replace("/", "_")
        work_output_path = Path(output_dir) / safe_work_name
        work_output_path.mkdir(parents=True, exist_ok=True)
        
        # HTMLファイルを作成
        html_file = work_output_path / filename
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📄 HTMLレポートを生成しました: {html_file}")
        return html_file
    
    def _format_character_html(self, char) -> str:
        """登場人物のHTML形式"""
        details = []
        if char.gender != "不明":
            details.append(f"性別: {char.gender}")
        if char.age:
            details.append(f"年齢: {char.age}")
        if char.occupation:
            details.append(f"職業: {char.occupation}")
        if char.personality:
            details.append(f"性格: {char.personality}")
        
        details_html = "<br>".join(details) if details else ""
        
        return f"""
        <div class="character">
            <strong>{char.name}</strong>
            {f"<br>{details_html}" if details_html else ""}
        </div>
        """
    
    def _format_emotion_html(self, emotion) -> str:
        """感情のHTML形式"""
        return f"""
        <div class="emotion">
            <strong>{emotion.subject}の{emotion.emotion_type}</strong> 
            （強度: {emotion.intensity}）
            <div class="quote">「{emotion.quote}」</div>
        </div>
        """
    
    def _format_relationship_html(self, rel) -> str:
        """関係性のHTML形式"""
        arrow = "↔" if rel.direction == "双方向" else "→"
        return f"""
        <div class="relationship">
            <strong>{rel.person1} {arrow} {rel.person2}</strong>: {rel.relation_type}
            {f'<div class="quote">根拠: 「{rel.evidence}」</div>' if rel.evidence else ''}
        </div>
        """