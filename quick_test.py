#!/usr/bin/env python3
"""
LangExtract日本語テキスト解析のクイックテスト
青空文庫から小説を取得してLangExtractで解析する
"""
import sys
from src.aozora_fetcher import AozoraFetcher
from src.text_extractor import JapaneseTextExtractor
from src.result_analyzer import ResultVisualizer, ResultAnalyzer


def quick_analyze(work_name: str = "羅生門", save_results: bool = True, model_id: str = None):
    """
    簡単に実行できるテスト関数
    
    Args:
        work_name: 作品名（羅生門、坊っちゃん、走れメロス、銀河鉄道の夜）
        save_results: 結果をファイルに保存するか
        model_id: 使用するLLMモデル（Noneの場合は環境変数から取得）
    """
    print(f"\n🚀 LangExtract 日本語解析テスト開始: {work_name}")
    print("="*60)
    
    try:
        # 1. テキスト取得
        fetcher = AozoraFetcher()
        text = fetcher.fetch_sample(work_name)
        
        # テキストの一部を表示
        print(f"\n📄 取得したテキスト（最初の200文字）:")
        print("-"*50)
        print(text[:200] + "...")
        print("-"*50)
        
        # 2. LangExtract実行
        print("\n🤖 LangExtractで情報抽出中...")
        extractor = JapaneseTextExtractor(model_id=model_id)
        
        results = extractor.extract_all(text)
        
        # 3. 結果表示
        visualizer = ResultVisualizer(results, text)
        visualizer.display_results_cli()
        
        # 4. 結果保存
        if save_results:
            # JSON/CSV保存（作品ごとのディレクトリに保存）
            analyzer = ResultAnalyzer(results)
            output_path = analyzer.save_results(work_name=work_name)
            
            # HTMLレポート生成（作品ごとのディレクトリに保存）
            html_filename = "report.html"
            html_file = visualizer.generate_html_report(work_name=work_name, filename=html_filename)
        
        print("\n✅ 解析完了!")
        
        if save_results:
            print(f"📂 結果の保存先: {output_path}")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """メイン関数"""
    # 作品リスト
    works = ["羅生門", "坊っちゃん", "走れメロス", "銀河鉄道の夜"]
    
    # コマンドライン引数の処理
    work_name = "羅生門"  # デフォルト
    model_id = None  # デフォルト（環境変数から取得）
    
    # モデル指定の処理
    if "--model" in sys.argv:
        try:
            model_index = sys.argv.index("--model")
            if model_index + 1 < len(sys.argv):
                model_id = sys.argv[model_index + 1]
                print(f"🔧 指定されたモデル: {model_id}")
            else:
                print("⚠️  --modelオプションにはモデル名が必要です")
                sys.exit(1)
        except ValueError:
            pass
    
    # 作品名の処理（--modelオプション以外の引数から）
    for arg in sys.argv[1:]:
        if not arg.startswith("--") and arg not in [model_id]:
            if arg in works:
                work_name = arg
                break
            else:
                print(f"⚠️  指定された作品が見つかりません: {arg}")
                print(f"利用可能な作品: {', '.join(works)}")
                print(f"使用例: uv run python quick_test.py 羅生門 --model gpt-4o")
                sys.exit(1)
    
    # 解析実行
    success = quick_analyze(work_name, model_id=model_id)
    
    if success:
        print("\n💡 ヒント:")
        print("  • 他の作品も試してみてください:")
        print(f"    uv run python quick_test.py 坊っちゃん")
        print("  • 異なるモデルを試してみてください:")
        print(f"    uv run python quick_test.py 羅生門 --model gpt-4o")
        print("  • 結果は data/results/(作品名)/ フォルダに作品ごとに保存されています")
        print("  • HTMLレポートでより詳細な結果を確認できます")
        print("  • 全文解析したい場合は、quick_test.pyのtest_textの長さ制限を解除してください")


if __name__ == "__main__":
    main()