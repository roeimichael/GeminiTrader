import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data
from src.gemini_api.simple_engine import SimpleAnalysisEngine


class StockAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Stock Analysis")
        self.root.geometry("800x600")

        self.api_key = None
        self.engine = None
        self.results = []
        self.analysis_running = False

        self.setup_gui()
        self.load_api_key()

    def setup_gui(self):
        title = tk.Label(self.root, text="Gemini Stock Analysis", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.test_btn = tk.Button(button_frame, text="Test API", command=self.test_api,
                                   bg="#4CAF50", fg="white", font=("Arial", 12), width=15)
        self.test_btn.pack(side=tk.LEFT, padx=5)

        self.run_btn = tk.Button(button_frame, text="Run Analysis", command=self.run_analysis,
                                 bg="#2196F3", fg="white", font=("Arial", 12), width=15)
        self.run_btn.pack(side=tk.LEFT, padx=5)

        self.export_btn = tk.Button(button_frame, text="Export CSV", command=self.export_csv,
                                    bg="#FF9800", fg="white", font=("Arial", 12), width=15, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=5)

        self.output_area = scrolledtext.ScrolledText(self.root, width=95, height=30, font=("Courier", 10))
        self.output_area.pack(pady=10, padx=10)

    def load_api_key(self):
        load_dotenv()
        self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            self.log("ERROR: GEMINI_API_KEY not found in .env file")
            self.test_btn.config(state=tk.DISABLED)
            self.run_btn.config(state=tk.DISABLED)
        else:
            self.log(f"API Key loaded successfully")
            self.log(f"Model: {Settings.GEMINI_MODEL}")
            self.log(f"Stocks to analyze: {len(Settings.DEFAULT_TICKERS)}")
            self.engine = SimpleAnalysisEngine(self.api_key, Settings.GEMINI_MODEL)

    def log(self, message):
        self.output_area.insert(tk.END, f"{message}\n")
        self.output_area.see(tk.END)
        self.root.update()

    def clear_output(self):
        self.output_area.delete(1.0, tk.END)

    def test_api(self):
        self.clear_output()
        self.log("Testing API connection...")
        self.log("=" * 80)

        test_ticker = Settings.DEFAULT_TICKERS[0]
        self.log(f"Testing with {test_ticker}...\n")

        try:
            stock_data = get_stock_data(test_ticker)
            self.log(f"✓ Stock data fetched successfully")

            scores = self.engine.analyze_stock(test_ticker, stock_data)

            if all(score is not None for score in scores.values()):
                self.log(f"\n✓ API Test PASSED!\n")
                self.log(f"  Fundamental Score: {scores['fundamental_score']}/100")
                self.log(f"  Technical Score:   {scores['technical_score']}/100")
                self.log(f"  Sentiment Score:   {scores['sentiment_score']}/100")
                self.log("\n" + "=" * 80)
                self.log("Ready to run full analysis!")
            else:
                self.log(f"\n✗ API Test FAILED - Some scores missing")
                self.log(f"  Scores: {scores}")

        except Exception as e:
            self.log(f"\n✗ API Test FAILED")
            self.log(f"  Error: {str(e)}")

    def run_analysis(self):
        if self.analysis_running:
            return

        self.analysis_running = True
        self.clear_output()
        self.results = []

        self.run_btn.config(state=tk.DISABLED)
        self.test_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)

        self.log("Starting Stock Analysis")
        self.log("=" * 80)

        tickers = Settings.DEFAULT_TICKERS
        total = len(tickers)

        for i, ticker in enumerate(tickers, 1):
            self.log(f"\n[{i}/{total}] Analyzing {ticker}...")

            try:
                stock_data = get_stock_data(ticker)
                scores = self.engine.analyze_stock(ticker, stock_data)

                if all(score is not None for score in scores.values()):
                    self.log(f"  ✓ F:{scores['fundamental_score']} T:{scores['technical_score']} S:{scores['sentiment_score']}")
                    self.results.append({
                        'Ticker': ticker,
                        'Fundamental_Score': scores['fundamental_score'],
                        'Technical_Score': scores['technical_score'],
                        'Sentiment_Score': scores['sentiment_score']
                    })
                else:
                    self.log(f"  ✗ Missing scores")
                    self.results.append({
                        'Ticker': ticker,
                        'Fundamental_Score': None,
                        'Technical_Score': None,
                        'Sentiment_Score': None
                    })

            except Exception as e:
                self.log(f"  ✗ Error: {str(e)[:50]}")
                self.results.append({
                    'Ticker': ticker,
                    'Fundamental_Score': None,
                    'Technical_Score': None,
                    'Sentiment_Score': None
                })

        self.log("\n" + "=" * 80)
        self.log(f"Analysis Complete!")
        self.log(f"Successful: {sum(1 for r in self.results if r['Fundamental_Score'] is not None)}/{total}")
        self.log("Click 'Export CSV' to save results")

        self.run_btn.config(state=tk.NORMAL)
        self.test_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        self.analysis_running = False

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "No analysis results to export")
            return

        df = pd.DataFrame(self.results)
        filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)

        self.log(f"\n✓ Exported to: {filename}")
        messagebox.showinfo("Export Complete", f"Results saved to:\n{filename}")


def main():
    root = tk.Tk()
    app = StockAnalysisGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
