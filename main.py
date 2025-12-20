import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import threading
from src.config.settings import Settings
from src.data.data_fetcher import get_stock_data
from src.gemini_api.simple_engine import SimpleAnalysisEngine


class StockAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Stock Analysis")
        self.root.geometry("900x650")

        # Dark theme colors
        self.bg_dark = "#1e1e1e"
        self.bg_medium = "#2d2d2d"
        self.fg_light = "#e0e0e0"
        self.accent_green = "#4CAF50"
        self.accent_blue = "#2196F3"
        self.accent_orange = "#FF9800"
        self.accent_red = "#f44336"

        self.root.configure(bg=self.bg_dark)

        self.api_key = None
        self.engine = None
        self.results = []
        self.analysis_running = False

        try:
            self.setup_gui()
            self.load_api_key()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize GUI:\n{str(e)}")
            self.root.destroy()

    def setup_gui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=self.bg_dark)
        title_frame.pack(pady=20)

        title = tk.Label(title_frame, text="⚡ Gemini Stock Analysis",
                        font=("Arial", 22, "bold"), bg=self.bg_dark, fg=self.fg_light)
        title.pack()

        subtitle = tk.Label(title_frame, text="AI-Powered Stock Market Analysis",
                           font=("Arial", 10), bg=self.bg_dark, fg="#888888")
        subtitle.pack()

        # Button frame
        button_frame = tk.Frame(self.root, bg=self.bg_dark)
        button_frame.pack(pady=15)

        # Test API Button
        self.test_btn = tk.Button(button_frame, text="🔍 Test API", command=self.safe_test_api,
                                   bg=self.accent_green, fg="white", font=("Arial", 11, "bold"),
                                   width=16, height=2, relief=tk.FLAT, bd=0,
                                   activebackground="#45a049", cursor="hand2")
        self.test_btn.pack(side=tk.LEFT, padx=8)

        # Run Analysis Button
        self.run_btn = tk.Button(button_frame, text="▶ Run Analysis", command=self.safe_run_analysis,
                                 bg=self.accent_blue, fg="white", font=("Arial", 11, "bold"),
                                 width=16, height=2, relief=tk.FLAT, bd=0,
                                 activebackground="#1976D2", cursor="hand2")
        self.run_btn.pack(side=tk.LEFT, padx=8)

        # Export CSV Button
        self.export_btn = tk.Button(button_frame, text="💾 Export CSV", command=self.safe_export_csv,
                                    bg=self.accent_orange, fg="white", font=("Arial", 11, "bold"),
                                    width=16, height=2, relief=tk.FLAT, bd=0,
                                    activebackground="#F57C00", cursor="hand2", state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT, padx=8)

        # Output area
        output_frame = tk.Frame(self.root, bg=self.bg_dark)
        output_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.output_area = scrolledtext.ScrolledText(output_frame, width=100, height=28,
                                                     font=("Consolas", 10),
                                                     bg=self.bg_medium, fg=self.fg_light,
                                                     insertbackground=self.fg_light,
                                                     selectbackground="#4CAF50",
                                                     relief=tk.FLAT, bd=0)
        self.output_area.pack(fill=tk.BOTH, expand=True)

    def load_api_key(self):
        try:
            load_dotenv()
            self.api_key = os.getenv('GEMINI_API_KEY')

            if not self.api_key:
                self.log("⚠️  ERROR: GEMINI_API_KEY not found in .env file")
                self.log("Please create a .env file with: GEMINI_API_KEY=your_key_here")
                self.test_btn.config(state=tk.DISABLED, bg="#555555")
                self.run_btn.config(state=tk.DISABLED, bg="#555555")
                messagebox.showwarning("API Key Missing",
                                      "GEMINI_API_KEY not found in .env file.\n\n"
                                      "Please create a .env file with:\nGEMINI_API_KEY=your_key_here")
            else:
                self.log(f"✓ API Key loaded successfully")
                self.log(f"✓ Model: {Settings.GEMINI_MODEL}")
                self.log(f"✓ Stocks to analyze: {len(Settings.DEFAULT_TICKERS)}")
                self.log(f"\nReady to start! Click 'Test API' to validate your connection.")
                self.engine = SimpleAnalysisEngine(self.api_key, Settings.GEMINI_MODEL)
        except Exception as e:
            self.log(f"⚠️  Error loading configuration: {str(e)}")
            messagebox.showerror("Configuration Error", f"Failed to load configuration:\n{str(e)}")

    def log(self, message):
        self.output_area.insert(tk.END, f"{message}\n")
        self.output_area.see(tk.END)
        self.root.update()

    def clear_output(self):
        self.output_area.delete(1.0, tk.END)

    def safe_test_api(self):
        if self.analysis_running:
            messagebox.showinfo("Test Running", "A test or analysis is already in progress")
            return

        # Run in separate thread to prevent GUI freeze
        thread = threading.Thread(target=self._run_test_api_thread, daemon=True)
        thread.start()

    def _run_test_api_thread(self):
        try:
            self.test_api()
        except Exception as e:
            self.log(f"\n⚠️  Critical Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Test Failed", f"API test failed with error:\n{str(e)}"))

    def test_api(self):
        if not self.api_key:
            self.root.after(0, lambda: messagebox.showwarning("No API Key", "Please configure your API key in .env file first"))
            return

        self.clear_output()
        self.log("🔍 Testing API connection...")
        self.log("=" * 90)

        try:
            test_ticker = Settings.DEFAULT_TICKERS[0]
            self.log(f"Testing with {test_ticker}...\n")

            stock_data = get_stock_data(test_ticker)
            self.log(f"✓ Stock data fetched successfully")

            self.log("Calling Gemini API (this may take a few seconds)...")
            scores = self.engine.analyze_stock(test_ticker, stock_data)

            if all(score is not None for score in scores.values()):
                self.log(f"\n✅ API Test PASSED!\n")
                self.log(f"  📊 Fundamental Score: {scores['fundamental_score']}/100")
                self.log(f"  📈 Technical Score:   {scores['technical_score']}/100")
                self.log(f"  💭 Sentiment Score:   {scores['sentiment_score']}/100")
                self.log("\n" + "=" * 90)
                self.log("✓ Ready to run full analysis!")
                self.root.after(0, lambda: messagebox.showinfo("Test Passed", "API connection successful!\nReady to analyze stocks."))
            else:
                self.log(f"\n❌ API Test FAILED - Some scores missing")
                self.log(f"  Scores: {scores}")
                self.root.after(0, lambda: messagebox.showwarning("Test Warning", "API responded but some scores are missing."))

        except Exception as e:
            self.log(f"\n❌ API Test FAILED")
            self.log(f"  Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Test Failed", f"API test failed:\n{str(e)}"))

    def safe_run_analysis(self):
        if self.analysis_running:
            messagebox.showinfo("Analysis Running", "Analysis is already in progress")
            return

        if not self.api_key:
            messagebox.showwarning("No API Key", "Please configure your API key in .env file first")
            return

        response = messagebox.askyesno("Start Analysis",
                                       f"Start analyzing {len(Settings.DEFAULT_TICKERS)} stocks?\n\n"
                                       "This may take several minutes.")
        if not response:
            return

        # Run in separate thread to prevent GUI freeze
        thread = threading.Thread(target=self._run_analysis_thread, daemon=True)
        thread.start()

    def _run_analysis_thread(self):
        try:
            self.run_analysis()
        except Exception as e:
            self.log(f"\n⚠️  Critical Error: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Analysis Failed", f"Analysis failed with error:\n{str(e)}"))
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL, bg=self.accent_blue))
            self.root.after(0, lambda: self.test_btn.config(state=tk.NORMAL, bg=self.accent_green))
            self.analysis_running = False

    def run_analysis(self):
        self.analysis_running = True
        self.clear_output()
        self.results = []

        self.run_btn.config(state=tk.DISABLED, bg="#555555")
        self.test_btn.config(state=tk.DISABLED, bg="#555555")
        self.export_btn.config(state=tk.DISABLED, bg="#555555")

        self.log("▶️  Starting Stock Analysis")
        self.log("=" * 90)

        tickers = Settings.DEFAULT_TICKERS
        total = len(tickers)
        success_count = 0
        error_count = 0

        try:
            for i, ticker in enumerate(tickers, 1):
                self.log(f"\n[{i}/{total}] 🔄 Analyzing {ticker}...")

                try:
                    stock_data = get_stock_data(ticker)
                    scores = self.engine.analyze_stock(ticker, stock_data)

                    if all(score is not None for score in scores.values()):
                        self.log(f"  ✅ F:{scores['fundamental_score']} T:{scores['technical_score']} S:{scores['sentiment_score']}")
                        success_count += 1
                        self.results.append({
                            'Ticker': ticker,
                            'Fundamental_Score': scores['fundamental_score'],
                            'Technical_Score': scores['technical_score'],
                            'Sentiment_Score': scores['sentiment_score']
                        })
                    else:
                        self.log(f"  ⚠️  Missing scores")
                        error_count += 1
                        self.results.append({
                            'Ticker': ticker,
                            'Fundamental_Score': None,
                            'Technical_Score': None,
                            'Sentiment_Score': None
                        })

                except Exception as e:
                    self.log(f"  ❌ Error: {str(e)[:60]}")
                    error_count += 1
                    self.results.append({
                        'Ticker': ticker,
                        'Fundamental_Score': None,
                        'Technical_Score': None,
                        'Sentiment_Score': None
                    })

        except Exception as e:
            self.log(f"\n⚠️  Analysis interrupted: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Analysis Error", f"Analysis was interrupted:\n{str(e)}"))

        finally:
            self.log("\n" + "=" * 90)
            self.log(f"🏁 Analysis Complete!")
            self.log(f"✅ Successful: {success_count}/{total}")
            self.log(f"❌ Failed: {error_count}/{total}")
            self.log(f"\n💾 Click 'Export CSV' to save results")

            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL, bg=self.accent_blue))
            self.root.after(0, lambda: self.test_btn.config(state=tk.NORMAL, bg=self.accent_green))
            self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL, bg=self.accent_orange))
            self.analysis_running = False

            msg = f"Analysis finished!\n\nSuccessful: {success_count}/{total}\nFailed: {error_count}/{total}\n\nClick 'Export CSV' to save results."
            self.root.after(0, lambda: messagebox.showinfo("Analysis Complete", msg))

    def safe_export_csv(self):
        try:
            self.export_csv()
        except Exception as e:
            self.log(f"\n⚠️  Export Error: {str(e)}")
            messagebox.showerror("Export Failed", f"Failed to export CSV:\n{str(e)}")

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "No analysis results to export.\n\nPlease run analysis first.")
            return

        try:
            df = pd.DataFrame(self.results)
            filename = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)

            self.log(f"\n💾 Exported to: {filename}")
            messagebox.showinfo("Export Complete",
                              f"✅ Results saved successfully!\n\n"
                              f"File: {filename}\n"
                              f"Rows: {len(self.results)}")
        except PermissionError:
            messagebox.showerror("Export Failed",
                               "Permission denied. The file may be open in another program.")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to save CSV:\n{str(e)}")


def main():
    root = tk.Tk()
    app = StockAnalysisGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
