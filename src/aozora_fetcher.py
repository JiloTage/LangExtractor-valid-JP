"""
青空文庫からテキストを取得・前処理するモジュール
"""
import re
import requests
from bs4 import BeautifulSoup


class AozoraFetcher:
    """青空文庫のテキスト取得クラス"""
    
    # サンプル作品リスト
    SAMPLE_WORKS = {
        "羅生門": {
            "author": "芥川龍之介",
            "url": "https://www.aozora.gr.jp/cards/000879/files/127_15260.html"
        },
        "坊っちゃん": {
            "author": "夏目漱石", 
            "url": "https://www.aozora.gr.jp/cards/000148/files/752_14964.html"
        },
        "走れメロス": {
            "author": "太宰治",
            "url": "https://www.aozora.gr.jp/cards/000035/files/1567_14913.html"
        },
        "銀河鉄道の夜": {
            "author": "宮沢賢治",
            "url": "https://www.aozora.gr.jp/cards/000081/files/456_15050.html"
        }
    }
    
    def fetch_sample(self, work_name: str) -> str:
        """サンプル作品を取得"""
        if work_name not in self.SAMPLE_WORKS:
            raise ValueError(f"作品名が見つかりません: {work_name}")
        
        work_info = self.SAMPLE_WORKS[work_name]
        print(f"📚 {work_name}（{work_info['author']}）を取得中...")
        
        text = self.fetch_from_url(work_info['url'])
        normalized_text = self.normalize_text(text)
        
        print(f"✅ 取得完了: {len(normalized_text)}文字")
        return normalized_text
    
    def fetch_from_url(self, url: str) -> str:
        """指定URLからテキストを取得"""
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'shift_jis'  # 青空文庫の文字コード
            
            # HTMLからテキスト部分を抽出
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='shift_jis')
            
            # 本文を含むdivを探す
            main_text = soup.find('div', class_='main_text')
            if not main_text:
                # 古い形式の場合、bodyから直接取得
                main_text = soup.body
                if not main_text:
                    # さらに古い形式の場合、全体から取得
                    main_text = soup
            
            # テキスト抽出
            text = main_text.get_text()
            
            return text
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            print("📝 テスト用のサンプルテキストを使用します。")
            # エラー時のフォールバック
            return ""
    
    def normalize_text(self, text: str) -> str:
        """テキストの正規化（ルビ・注釈の除去）"""
        normalizer = TextNormalizer()
        return normalizer.normalize(text)


class TextNormalizer:
    """青空文庫形式のテキスト正規化クラス"""
    
    # ルビのパターン
    RUBY_PATTERNS = [
        # パターン1: ｜漢字《かんじ》
        (r'｜([^《]+)《[^》]+》', r'\1'),
        # パターン2: 漢字《かんじ》（｜なし）
        (r'([一-龥々ぁ-ゔァ-ヴー]+)《[^》]+》', r'\1'),
        # パターン3: ［＃ルビ関連］
        (r'［＃[^］]*ルビ[^］]*］', ''),
    ]
    
    # 注釈のパターン
    ANNOTATION_PATTERNS = [
        # ［＃...］形式の注釈
        (r'［＃[^］]+］', ''),
        # ※［＃...］形式
        (r'※［＃[^］]+］', ''),
    ]
    
    def normalize(self, text: str) -> str:
        """テキストを正規化"""
        # 1. ルビの除去
        for pattern, replacement in self.RUBY_PATTERNS:
            text = re.sub(pattern, replacement, text)
        
        # 2. 注釈の除去
        for pattern, replacement in self.ANNOTATION_PATTERNS:
            text = re.sub(pattern, replacement, text)
        
        # 3. 改行・空白の正規化
        text = re.sub(r'\r\n', '\n', text)  # 改行コード統一
        text = re.sub(r'　+', '　', text)   # 全角スペース重複除去
        text = re.sub(r'\n\n\n+', '\n\n', text)  # 過剰な空行を削除
        text = re.sub(r' +', ' ', text)     # 半角スペース重複除去
        
        # 4. ヘッダー・フッターの除去
        text = self._remove_headers_footers(text)
        
        return text.strip()
    
    def _remove_headers_footers(self, text: str) -> str:
        """作品本文以外の部分を除去"""
        lines = text.split('\n')
        
        # 本文開始位置を探す
        start_idx = 0
        for i, line in enumerate(lines):
            # 一般的な本文開始パターン
            if any(marker in line for marker in ['-------', '【テキスト中に現れる記号について】']):
                start_idx = i + 1
                break
        
        # 本文終了位置を探す
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            # 一般的な本文終了パターン
            if any(marker in line for marker in ['底本：', '入力：', '校正：', '※［＃']):
                end_idx = i
                break
        
        # 本文部分のみを返す
        return '\n'.join(lines[start_idx:end_idx])


if __name__ == "__main__":
    # テスト実行
    fetcher = AozoraFetcher()
    
    # 羅生門を取得してみる
    text = fetcher.fetch_sample("羅生門")
    
    # 最初の500文字を表示
    print("\n📄 取得したテキスト（最初の500文字）:")
    print("-" * 50)
    print(text[:500])
    print("-" * 50)