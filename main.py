import customtkinter as ctk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
import json
import os
import threading

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Portfolio Tracker Pro - AI Enhanced")
        self.geometry("1400x800")
        
        # Portfolio data
        self.portfolio = []
        self.load_portfolio()
        
        # Create main layout
        self.create_widgets()
        self.update_portfolio_display()
        
    def create_widgets(self):
        # Left Panel - Input Section
        self.left_frame = ctk.CTkFrame(self, width=350, corner_radius=10)
        self.left_frame.pack(side="left", fill="both", padx=10, pady=10)
        self.left_frame.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(self.left_frame, text="📊 Add Stock", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Stock Symbol Input
        ctk.CTkLabel(self.left_frame, text="Stock Symbol:", 
                    font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.symbol_entry = ctk.CTkEntry(self.left_frame, placeholder_text="e.g., AAPL",
                                         width=250, height=40)
        self.symbol_entry.pack(pady=5)
        
        # Shares Input
        ctk.CTkLabel(self.left_frame, text="Number of Shares:", 
                    font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.shares_entry = ctk.CTkEntry(self.left_frame, placeholder_text="e.g., 10",
                                         width=250, height=40)
        self.shares_entry.pack(pady=5)
        
        # Purchase Price Input
        ctk.CTkLabel(self.left_frame, text="Purchase Price ($):", 
                    font=ctk.CTkFont(size=14)).pack(pady=(10, 5))
        self.price_entry = ctk.CTkEntry(self.left_frame, placeholder_text="e.g., 150.50",
                                        width=250, height=40)
        self.price_entry.pack(pady=5)
        
        # Add Button
        self.add_btn = ctk.CTkButton(self.left_frame, text="Add to Portfolio",
                                     command=self.add_stock, height=45,
                                     font=ctk.CTkFont(size=16, weight="bold"))
        self.add_btn.pack(pady=20)
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.left_frame, text="",
                                         font=ctk.CTkFont(size=12), wraplength=230)
        self.status_label.pack(pady=10)
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        self.refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh",
                                         command=self.refresh_prices, width=120)
        self.refresh_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(btn_frame, text="🗑️ Clear All",
                                       command=self.clear_portfolio, width=120,
                                       fg_color="#d32f2f", hover_color="#b71c1c")
        self.clear_btn.pack(side="left", padx=5)
        
        # Right Panel - Portfolio Display
        self.right_frame = ctk.CTkFrame(self, corner_radius=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Portfolio Title
        portfolio_title = ctk.CTkLabel(self.right_frame, text="Your Portfolio",
                                       font=ctk.CTkFont(size=28, weight="bold"))
        portfolio_title.pack(pady=20)
        
        # Summary Frame
        self.summary_frame = ctk.CTkFrame(self.right_frame, height=100)
        self.summary_frame.pack(fill="x", padx=20, pady=10)
        
        self.total_value_label = ctk.CTkLabel(self.summary_frame, text="Total Value: $0.00",
                                              font=ctk.CTkFont(size=20, weight="bold"))
        self.total_value_label.pack(pady=10)
        
        self.total_gain_label = ctk.CTkLabel(self.summary_frame, text="Total Gain/Loss: $0.00 (0%)",
                                             font=ctk.CTkFont(size=16))
        self.total_gain_label.pack(pady=5)
        
        # Scrollable Frame for Stocks
        self.scrollable_frame = ctk.CTkScrollableFrame(self.right_frame, height=500)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50  # Neutral if not enough data
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def get_stock_analysis(self, symbol):
        """Get comprehensive stock analysis with buy/sell signals"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data (30 days)
            hist = ticker.history(period="1mo")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            
            # Calculate indicators
            prices = hist['Close'].tolist()
            rsi = self.calculate_rsi(prices)
            
            # Moving averages
            ma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else current_price
            ma_30 = sum(prices) / len(prices)
            
            # Price change
            week_ago_price = prices[-7] if len(prices) >= 7 else prices[0]
            week_change_pct = ((current_price - week_ago_price) / week_ago_price) * 100
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Generate signal
            signal = self.generate_signal(rsi, ma_7, ma_30, current_price, week_change_pct, volume_ratio)
            
            # Get news
            news = self.get_stock_news(ticker)
            
            # Get company info
            info = ticker.info
            company_name = info.get('longName', symbol)
            sector = info.get('sector', 'N/A')
            
            return {
                'current_price': current_price,
                'rsi': rsi,
                'ma_7': ma_7,
                'ma_30': ma_30,
                'week_change_pct': week_change_pct,
                'volume_ratio': volume_ratio,
                'signal': signal,
                'news': news,
                'company_name': company_name,
                'sector': sector
            }
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def generate_signal(self, rsi, ma_7, ma_30, current_price, week_change, volume_ratio):
        """Generate buy/sell/hold signal based on indicators"""
        score = 0
        reasons = []
        
        # RSI Analysis
        if rsi < 30:
            score += 2
            reasons.append("🟢 Oversold (RSI < 30)")
        elif rsi > 70:
            score -= 2
            reasons.append("🔴 Overbought (RSI > 70)")
        elif 40 <= rsi <= 60:
            reasons.append("🟡 Neutral RSI")
        
        # Moving Average Analysis
        if ma_7 > ma_30:
            score += 1
            reasons.append("🟢 Short-term uptrend")
        else:
            score -= 1
            reasons.append("🔴 Short-term downtrend")
        
        # Price momentum
        if week_change > 5:
            score += 1
            reasons.append("🟢 Strong weekly gain")
        elif week_change < -5:
            score -= 1
            reasons.append("🔴 Weak weekly performance")
        
        # Volume analysis
        if volume_ratio > 1.5:
            reasons.append("📈 High trading volume")
        
        # Generate recommendation
        if score >= 2:
            recommendation = "🚀 STRONG BUY"
            color = "#00e676"
        elif score == 1:
            recommendation = "✅ BUY"
            color = "#66bb6a"
        elif score == 0:
            recommendation = "⏸️ HOLD"
            color = "#ffa726"
        elif score == -1:
            recommendation = "⚠️ CONSIDER SELLING"
            color = "#ff7043"
        else:
            recommendation = "🚨 SELL"
            color = "#ef5350"
        
        return {
            'recommendation': recommendation,
            'color': color,
            'reasons': reasons,
            'score': score
        }
    
    def get_stock_news(self, ticker):
        """Get latest news for stock"""
        try:
            news = ticker.news
            if news and len(news) > 0:
                latest = news[0]
                return {
                    'title': latest.get('title', 'No title'),
                    'publisher': latest.get('publisher', 'Unknown'),
                    'link': latest.get('link', '')
                }
        except:
            pass
        return None
    
    def add_stock(self):
        symbol = self.symbol_entry.get().upper().strip()
        shares_text = self.shares_entry.get().strip()
        price_text = self.price_entry.get().strip()
        
        # Validation
        if not symbol or not shares_text or not price_text:
            self.status_label.configure(text="❌ Please fill all fields", text_color="red")
            return
        
        try:
            shares = float(shares_text)
            purchase_price = float(price_text)
            
            if shares <= 0 or purchase_price <= 0:
                self.status_label.configure(text="❌ Values must be positive", text_color="red")
                return
        except ValueError:
            self.status_label.configure(text="❌ Invalid number format", text_color="red")
            return
        
        # Show loading
        self.status_label.configure(text="⏳ Analyzing stock...", text_color="blue")
        self.update()
        
        # Fetch analysis in background
        def fetch_and_add():
            analysis = self.get_stock_analysis(symbol)
            
            if not analysis:
                self.status_label.configure(text=f"❌ Could not fetch data for {symbol}", text_color="red")
                return
            
            # Add to portfolio
            stock_data = {
                'symbol': symbol,
                'shares': shares,
                'purchase_price': purchase_price,
                'current_price': analysis['current_price'],
                'date_added': datetime.now().strftime("%Y-%m-%d"),
                'analysis': analysis
            }
            
            self.portfolio.append(stock_data)
            self.save_portfolio()
            self.update_portfolio_display()
            
            # Clear inputs
            self.symbol_entry.delete(0, 'end')
            self.shares_entry.delete(0, 'end')
            self.price_entry.delete(0, 'end')
            
            self.status_label.configure(text=f"✅ Added {symbol} successfully!", text_color="green")
        
        thread = threading.Thread(target=fetch_and_add)
        thread.daemon = True
        thread.start()
    
    def update_portfolio_display(self):
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.portfolio:
            empty_label = ctk.CTkLabel(self.scrollable_frame, 
                                      text="No stocks in portfolio yet.\nAdd your first stock to get started!",
                                      font=ctk.CTkFont(size=16),
                                      text_color="gray")
            empty_label.pack(pady=50)
            self.total_value_label.configure(text="Total Value: $0.00")
            self.total_gain_label.configure(text="Total Gain/Loss: $0.00 (0%)")
            return
        
        total_value = 0
        total_cost = 0
        
        for i, stock in enumerate(self.portfolio):
            stock_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=10)
            stock_frame.pack(fill="x", pady=8, padx=5)
            
            current_value = stock['shares'] * stock['current_price']
            cost_basis = stock['shares'] * stock['purchase_price']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            # Stock header with company name
            header_frame = ctk.CTkFrame(stock_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=10)
            
            analysis = stock.get('analysis', {})
            company_name = analysis.get('company_name', stock['symbol'])
            
            symbol_label = ctk.CTkLabel(header_frame, 
                                        text=f"{stock['symbol']} - {company_name}",
                                        font=ctk.CTkFont(size=18, weight="bold"))
            symbol_label.pack(side="left")
            
            # Delete button
            delete_btn = ctk.CTkButton(header_frame, text="❌", width=30,
                                       command=lambda idx=i: self.delete_stock(idx),
                                       fg_color="transparent", hover_color="#d32f2f")
            delete_btn.pack(side="right")
            
            # Stock details
            details_frame = ctk.CTkFrame(stock_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            details_text = f"Shares: {stock['shares']:.2f} | Purchase: ${stock['purchase_price']:.2f} | Current: ${stock['current_price']:.2f}"
            details_label = ctk.CTkLabel(details_frame, text=details_text,
                                        font=ctk.CTkFont(size=12))
            details_label.pack(side="left")
            
            # Gain/Loss
            color = "green" if gain_loss >= 0 else "red"
            sign = "+" if gain_loss >= 0 else ""
            gain_text = f"{sign}${gain_loss:.2f} ({sign}{gain_loss_pct:.2f}%)"
            gain_label = ctk.CTkLabel(details_frame, text=gain_text,
                                     font=ctk.CTkFont(size=14, weight="bold"),
                                     text_color=color)
            gain_label.pack(side="right")
            
            # AI Analysis Section
            if analysis:
                analysis_frame = ctk.CTkFrame(stock_frame, fg_color="#1a1a1a", corner_radius=8)
                analysis_frame.pack(fill="x", padx=15, pady=(0, 10))
                
                # Signal
                signal = analysis.get('signal', {})
                signal_label = ctk.CTkLabel(analysis_frame, 
                                            text=f"AI Signal: {signal.get('recommendation', 'N/A')}",
                                            font=ctk.CTkFont(size=14, weight="bold"),
                                            text_color=signal.get('color', 'gray'))
                signal_label.pack(pady=8, padx=10, anchor="w")
                
                # Reasons
                reasons = signal.get('reasons', [])
                if reasons:
                    reasons_text = " | ".join(reasons[:3])  # Show top 3 reasons
                    reasons_label = ctk.CTkLabel(analysis_frame, text=reasons_text,
                                                 font=ctk.CTkFont(size=11),
                                                 text_color="#b0b0b0")
                    reasons_label.pack(pady=(0, 8), padx=10, anchor="w")
                
                # Technical indicators
                tech_text = f"RSI: {analysis.get('rsi', 0):.1f} | 7-Day MA: ${analysis.get('ma_7', 0):.2f} | Week Change: {analysis.get('week_change_pct', 0):.1f}%"
                tech_label = ctk.CTkLabel(analysis_frame, text=tech_text,
                                         font=ctk.CTkFont(size=10),
                                         text_color="#808080")
                tech_label.pack(pady=(0, 8), padx=10, anchor="w")
                
                # News
                news = analysis.get('news')
                if news:
                    news_frame = ctk.CTkFrame(analysis_frame, fg_color="#0d0d0d", corner_radius=5)
                    news_frame.pack(fill="x", padx=10, pady=(0, 8))
                    
                    news_label = ctk.CTkLabel(news_frame, 
                                             text=f"📰 Latest: {news['title'][:80]}...",
                                             font=ctk.CTkFont(size=10),
                                             text_color="#90caf9",
                                             wraplength=600,
                                             anchor="w")
                    news_label.pack(pady=5, padx=8, anchor="w")
        
        # Update summary
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost) * 100 if total_cost > 0 else 0
        
        self.total_value_label.configure(text=f"Total Value: ${total_value:,.2f}")
        
        gain_color = "green" if total_gain >= 0 else "red"
        sign = "+" if total_gain >= 0 else ""
        self.total_gain_label.configure(
            text=f"Total Gain/Loss: {sign}${total_gain:,.2f} ({sign}{total_gain_pct:.2f}%)",
            text_color=gain_color
        )
    
    def delete_stock(self, index):
        if 0 <= index < len(self.portfolio):
            self.portfolio.pop(index)
            self.save_portfolio()
            self.update_portfolio_display()
            self.status_label.configure(text="✅ Stock removed", text_color="green")
    
    def refresh_prices(self):
        if not self.portfolio:
            self.status_label.configure(text="❌ No stocks to refresh", text_color="red")
            return
        
        self.status_label.configure(text="🔄 Refreshing all data...", text_color="blue")
        self.update()
        
        def refresh_all():
            for stock in self.portfolio:
                analysis = self.get_stock_analysis(stock['symbol'])
                if analysis:
                    stock['current_price'] = analysis['current_price']
                    stock['analysis'] = analysis
            
            self.save_portfolio()
            self.update_portfolio_display()
            self.status_label.configure(text="✅ All data updated!", text_color="green")
        
        thread = threading.Thread(target=refresh_all)
        thread.daemon = True
        thread.start()
    
    def clear_portfolio(self):
        self.portfolio = []
        self.save_portfolio()
        self.update_portfolio_display()
        self.status_label.configure(text="✅ Portfolio cleared", text_color="green")
    
    def save_portfolio(self):
        with open('portfolio.json', 'w') as f:
            json.dump(self.portfolio, f, indent=4)
    
    def load_portfolio(self):
        if os.path.exists('portfolio.json'):
            try:
                with open('portfolio.json', 'r') as f:
                    self.portfolio = json.load(f)
            except:
                self.portfolio = []

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
