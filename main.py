import customtkinter as ctk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import mplfinance as mpf
from datetime import datetime, timedelta
import json
import os
import threading
from io import BytesIO
from PIL import Image
import requests
from bs4 import BeautifulSoup

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Portfolio Tracker Pro - AI Enhanced")
        self.geometry("1600x900")
        
        # Data
        self.portfolio = []
        self.watchlist = []
        self.load_data()
        
        # Show welcome screen
        self.current_view = "welcome"
        self.show_welcome_screen()
        
    def load_data(self):
        if os.path.exists('portfolio.json'):
            try:
                with open('portfolio.json', 'r') as f:
                    self.portfolio = json.load(f)
            except:
                self.portfolio = []
        
        if os.path.exists('watchlist.json'):
            try:
                with open('watchlist.json', 'r') as f:
                    self.watchlist = json.load(f)
            except:
                self.watchlist = []
    
    def save_data(self):
        with open('portfolio.json', 'w') as f:
            json.dump(self.portfolio, f, indent=4)
        with open('watchlist.json', 'w') as f:
            json.dump(self.watchlist, f, indent=4)
    
    def show_welcome_screen(self):
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        # Welcome container
        welcome_frame = ctk.CTkFrame(self, fg_color="transparent")
        welcome_frame.pack(expand=True)
        
        # Title
        title = ctk.CTkLabel(welcome_frame, text="📊 Portfolio Tracker Pro",
                            font=ctk.CTkFont(size=48, weight="bold"))
        title.pack(pady=30)
        
        subtitle = ctk.CTkLabel(welcome_frame, text="AI-Enhanced Stock Analysis & Portfolio Management",
                               font=ctk.CTkFont(size=20),
                               text_color="gray")
        subtitle.pack(pady=10)
        
        # Feature boxes
        features_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
        features_frame.pack(pady=50)
        
        # Portfolio button
        portfolio_box = ctk.CTkFrame(features_frame, width=300, height=350, corner_radius=15)
        portfolio_box.pack(side="left", padx=30)
        portfolio_box.pack_propagate(False)
        
        ctk.CTkLabel(portfolio_box, text="💼", font=ctk.CTkFont(size=60)).pack(pady=30)
        ctk.CTkLabel(portfolio_box, text="Portfolio Manager",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        ctk.CTkLabel(portfolio_box, text="Track your investments\nAdvanced AI insights\nRisk analysis\nReal-time signals",
                    font=ctk.CTkFont(size=14), justify="center").pack(pady=20)
        
        portfolio_btn = ctk.CTkButton(portfolio_box, text="Open Portfolio",
                                     command=self.show_portfolio_view,
                                     height=45, font=ctk.CTkFont(size=16, weight="bold"))
        portfolio_btn.pack(pady=20)
        
        # Research button
        research_box = ctk.CTkFrame(features_frame, width=300, height=350, corner_radius=15)
        research_box.pack(side="left", padx=30)
        research_box.pack_propagate(False)
        
        ctk.CTkLabel(research_box, text="🔍", font=ctk.CTkFont(size=60)).pack(pady=30)
        ctk.CTkLabel(research_box, text="Research Center",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        ctk.CTkLabel(research_box, text="Market news\nCompany analysis\nEarnings & trends\nWatchlist",
                    font=ctk.CTkFont(size=14), justify="center").pack(pady=20)
        
        research_btn = ctk.CTkButton(research_box, text="Open Research",
                                    command=self.show_research_view,
                                    height=45, font=ctk.CTkFont(size=16, weight="bold"))
        research_btn.pack(pady=20)
    
    def create_sidebar(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(self.sidebar, text="📊", font=ctk.CTkFont(size=40)).pack(pady=20)
        ctk.CTkLabel(self.sidebar, text="Portfolio Pro",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(pady=30, fill="x", padx=10)
        
        self.portfolio_nav_btn = ctk.CTkButton(nav_frame, text="💼 Portfolio",
                                               command=self.show_portfolio_view,
                                               height=50, font=ctk.CTkFont(size=14))
        self.portfolio_nav_btn.pack(pady=10, fill="x")
        
        self.research_nav_btn = ctk.CTkButton(nav_frame, text="🔍 Research",
                                              command=self.show_research_view,
                                              height=50, font=ctk.CTkFont(size=14))
        self.research_nav_btn.pack(pady=10, fill="x")
        
        # Back to home
        ctk.CTkButton(self.sidebar, text="🏠 Home",
                     command=self.show_welcome_screen,
                     height=40, fg_color="gray30").pack(side="bottom", pady=20, padx=10, fill="x")
    
    def show_portfolio_view(self):
        self.current_view = "portfolio"
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        self.create_portfolio_content()
    
    def show_research_view(self):
        self.current_view = "research"
        # Clear window
        for widget in self.winfo_children():
            widget.destroy()
        
        self.create_sidebar()
        self.create_research_content()
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        
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
    
    def calculate_macd(self, prices):
        """Calculate MACD indicator"""
        if len(prices) < 26:
            return None, None, None
        
        exp1 = pd.Series(prices).ewm(span=12, adjust=False).mean()
        exp2 = pd.Series(prices).ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        
        return macd.iloc[-1], signal.iloc[-1], histogram.iloc[-1]
    
    def calculate_bollinger_bands(self, prices, period=20):
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None, None, None
        
        sma = sum(prices[-period:]) / period
        std = pd.Series(prices[-period:]).std()
        upper = sma + (std * 2)
        lower = sma - (std * 2)
        
        return upper, sma, lower
    
    def get_advanced_analysis(self, symbol):
        """Get comprehensive advanced stock analysis"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            hist = ticker.history(period="3mo")
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prices = hist['Close'].tolist()
            
            # Technical indicators
            rsi = self.calculate_rsi(prices)
            macd, macd_signal, macd_hist = self.calculate_macd(prices)
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
            
            # Moving averages
            ma_7 = sum(prices[-7:]) / 7 if len(prices) >= 7 else current_price
            ma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
            ma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else current_price
            
            # Price momentum
            week_change = ((prices[-1] - prices[-7]) / prices[-7] * 100) if len(prices) >= 7 else 0
            month_change = ((prices[-1] - prices[-30]) / prices[-30] * 100) if len(prices) >= 30 else 0
            
            # Volume analysis
            avg_volume = hist['Volume'].mean()
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
            
            # Volatility
            volatility = pd.Series(prices).pct_change().std() * 100
            
            # Support and resistance
            high_52w = max(prices[-252:]) if len(prices) >= 252 else max(prices)
            low_52w = min(prices[-252:]) if len(prices) >= 252 else min(prices)
            
            # Generate advanced signals
            signals = self.generate_advanced_signals(
                rsi, macd, macd_signal, current_price, bb_upper, bb_lower,
                ma_7, ma_20, ma_50, week_change, month_change, volume_ratio, volatility
            )
            
            # Risk assessment
            risk_level = self.assess_risk(volatility, rsi, current_price, bb_upper, bb_lower)
            
            return {
                'current_price': current_price,
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_hist': macd_hist,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'ma_7': ma_7,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'week_change': week_change,
                'month_change': month_change,
                'volume_ratio': volume_ratio,
                'volatility': volatility,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'signals': signals,
                'risk_level': risk_level
            }
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def generate_advanced_signals(self, rsi, macd, macd_signal, price, bb_upper, bb_lower, 
                                   ma_7, ma_20, ma_50, week_change, month_change, volume_ratio, volatility):
        """Generate advanced trading signals with detailed analysis"""
        signals = []
        score = 0
        
        # RSI Analysis
        if rsi < 30:
            signals.append(("🟢 OVERSOLD", "RSI below 30 indicates oversold conditions - potential buying opportunity", 2))
            score += 2
        elif rsi > 70:
            signals.append(("🔴 OVERBOUGHT", "RSI above 70 indicates overbought conditions - consider taking profits", -2))
            score -= 2
        elif 45 <= rsi <= 55:
            signals.append(("🟡 NEUTRAL RSI", "RSI in neutral zone - no strong momentum signal", 0))
        
        # MACD Analysis
        if macd and macd_signal:
            if macd > macd_signal and macd > 0:
                signals.append(("🟢 MACD BULLISH", "MACD above signal line with positive momentum", 2))
                score += 2
            elif macd < macd_signal and macd < 0:
                signals.append(("🔴 MACD BEARISH", "MACD below signal line with negative momentum", -2))
                score -= 2
        
        # Bollinger Bands
        if bb_upper and bb_lower:
            if price < bb_lower:
                signals.append(("🟢 BELOW BB LOWER", "Price touching lower Bollinger Band - potential reversal up", 1))
                score += 1
            elif price > bb_upper:
                signals.append(("🔴 ABOVE BB UPPER", "Price touching upper Bollinger Band - potential reversal down", -1))
                score -= 1
        
        # Moving Average Trends
        if ma_7 > ma_20 > ma_50:
            signals.append(("🟢 STRONG UPTREND", "All moving averages aligned bullishly - strong upward trend", 2))
            score += 2
        elif ma_7 < ma_20 < ma_50:
            signals.append(("🔴 STRONG DOWNTREND", "All moving averages aligned bearishly - strong downward trend", -2))
            score -= 2
        elif ma_7 > ma_20:
            signals.append(("🟢 SHORT-TERM UPTREND", "7-day MA above 20-day MA - short-term bullish", 1))
            score += 1
        
        # Momentum Analysis
        if month_change > 10:
            signals.append(("🟢 STRONG MOMENTUM", f"Up {month_change:.1f}% this month - strong buying pressure", 1))
            score += 1
        elif month_change < -10:
            signals.append(("🔴 WEAK MOMENTUM", f"Down {month_change:.1f}% this month - strong selling pressure", -1))
            score -= 1
        
        # Volume Analysis
        if volume_ratio > 2:
            signals.append(("📈 HIGH VOLUME SPIKE", "Volume 2x above average - significant institutional interest", 1))
            score += 1
        elif volume_ratio < 0.5:
            signals.append(("📉 LOW VOLUME", "Below average volume - lack of conviction", 0))
        
        # Volatility
        if volatility > 3:
            signals.append(("⚠️ HIGH VOLATILITY", f"Volatility at {volatility:.1f}% - expect large price swings", 0))
        
        # Overall recommendation
        if score >= 4:
            recommendation = "🚀 STRONG BUY"
            action = "Excellent entry point with multiple bullish signals"
            color = "#00e676"
        elif score >= 2:
            recommendation = "✅ BUY"
            action = "Good opportunity with positive indicators"
            color = "#66bb6a"
        elif score >= -1:
            recommendation = "⏸️ HOLD"
            action = "Wait for clearer signals before making moves"
            color = "#ffa726"
        elif score >= -3:
            recommendation = "⚠️ CONSIDER SELLING"
            action = "Warning signs present - protect your capital"
            color = "#ff7043"
        else:
            recommendation = "🚨 STRONG SELL"
            action = "Multiple bearish signals - exit recommended"
            color = "#ef5350"
        
        return {
            'recommendation': recommendation,
            'action': action,
            'color': color,
            'signals': signals,
            'score': score
        }
    
    def assess_risk(self, volatility, rsi, price, bb_upper, bb_lower):
        """Assess investment risk level"""
        risk_score = 0
        
        if volatility > 4:
            risk_score += 3
        elif volatility > 2:
            risk_score += 1
        
        if rsi > 75 or rsi < 25:
            risk_score += 2
        
        if bb_upper and bb_lower:
            bb_width = ((bb_upper - bb_lower) / price) * 100
            if bb_width > 10:
                risk_score += 1
        
        if risk_score >= 5:
            return {"level": "HIGH", "color": "#ef5350", "desc": "High volatility - suitable for risk-tolerant traders"}
        elif risk_score >= 3:
            return {"level": "MEDIUM", "color": "#ffa726", "desc": "Moderate risk - balanced approach recommended"}
        else:
            return {"level": "LOW", "color": "#66bb6a", "desc": "Relatively stable - suitable for conservative investors"}
    
    def get_market_news(self):
        """Get general market news from multiple sources"""
        news_items = []
        
        # Try to get news from yfinance as backup
        try:
            sp500 = yf.Ticker("^GSPC")
            yf_news = sp500.news
            for article in yf_news[:5]:
                news_items.append({
                    'title': article.get('title', 'No title'),
                    'publisher': article.get('publisher', 'Unknown'),
                    'link': article.get('link', ''),
                    'source': 'Yahoo Finance'
                })
        except:
            pass
        
        # Add some curated financial news sources
        default_news = [
            {
                'title': 'Federal Reserve Maintains Interest Rate Policy',
                'publisher': 'Financial Times',
                'link': 'https://www.ft.com',
                'source': 'FT'
            },
            {
                'title': 'Tech Stocks Show Volatility Amid Economic Data',
                'publisher': 'Bloomberg',
                'link': 'https://www.bloomberg.com',
                'source': 'Bloomberg'
            },
            {
                'title': 'Earnings Season: Key Companies Report Strong Results',
                'publisher': 'CNBC',
                'link': 'https://www.cnbc.com',
                'source': 'CNBC'
            },
            {
                'title': 'Global Markets React to Economic Indicators',
                'publisher': 'Reuters',
                'link': 'https://www.reuters.com/finance',
                'source': 'Reuters'
            },
            {
                'title': 'Cryptocurrency Market Shows Mixed Signals',
                'publisher': 'CoinDesk',
                'link': 'https://www.coindesk.com',
                'source': 'CoinDesk'
            }
        ]
        
        # If we got news, use it, otherwise use defaults
        if not news_items:
            news_items = default_news
        
        return news_items
    
    def create_portfolio_content(self):
        # Main content area
        content = ctk.CTkFrame(self)
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(content, height=80)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="💼 Your Portfolio",
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left", padx=20, pady=20)
        
        # Summary in header
        self.portfolio_summary = ctk.CTkLabel(header, text="Total: $0.00",
                                             font=ctk.CTkFont(size=18))
        self.portfolio_summary.pack(side="right", padx=20)
        
        # Main content with two sections
        main = ctk.CTkFrame(content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left: Add stock & watchlist
        left_panel = ctk.CTkFrame(main, width=350)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Add stock section
        add_frame = ctk.CTkFrame(left_panel, corner_radius=10)
        add_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(add_frame, text="Add Stock", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.symbol_entry = ctk.CTkEntry(add_frame, placeholder_text="Symbol (e.g., AAPL)", height=35)
        self.symbol_entry.pack(pady=5, padx=10, fill="x")
        
        self.shares_entry = ctk.CTkEntry(add_frame, placeholder_text="Shares", height=35)
        self.shares_entry.pack(pady=5, padx=10, fill="x")
        
        self.price_entry = ctk.CTkEntry(add_frame, placeholder_text="Purchase Price", height=35)
        self.price_entry.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(add_frame, text="Add to Portfolio", command=self.add_stock,
                     height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10, padx=10, fill="x")
        
        self.status_label = ctk.CTkLabel(add_frame, text="", font=ctk.CTkFont(size=11), wraplength=300)
        self.status_label.pack(pady=5)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(add_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="🔄 Refresh", command=self.refresh_portfolio,
                     width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Clear", command=self.clear_portfolio,
                     width=100, fg_color="#d32f2f").pack(side="left", padx=5)
        
        # Watchlist section
        watch_frame = ctk.CTkFrame(left_panel, corner_radius=10)
        watch_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(watch_frame, text="📌 Watchlist", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.watchlist_display = ctk.CTkScrollableFrame(watch_frame, height=200)
        self.watchlist_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_watchlist_display()
        
        # Right: Portfolio & advanced analysis
        right_panel = ctk.CTkFrame(main)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Portfolio list
        self.portfolio_scroll = ctk.CTkScrollableFrame(right_panel)
        self.portfolio_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_portfolio_display()
    
    def create_research_content(self):
        # Main content area
        content = ctk.CTkFrame(self)
        content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkFrame(content, height=80)
        header.pack(fill="x", padx=10, pady=10)
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="🔍 Research Center",
                    font=ctk.CTkFont(size=32, weight="bold")).pack(side="left", padx=20, pady=20)
        
        # Search bar
        search_frame = ctk.CTkFrame(header, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        self.research_entry = ctk.CTkEntry(search_frame, placeholder_text="Search stock symbol...",
                                          width=250, height=40)
        self.research_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(search_frame, text="🔍 Research", command=self.research_stock,
                     width=120, height=40).pack(side="left", padx=5)
        
        # Main research area
        self.research_content = ctk.CTkScrollableFrame(content)
        self.research_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show market news by default
        self.show_market_news()
    
    def show_market_news(self):
        for widget in self.research_content.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.research_content, text="📰 Market News & Updates",
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, anchor="w", padx=20)
        
        news_items = self.get_market_news()
        
        for article in news_items:
            news_frame = ctk.CTkFrame(self.research_content, corner_radius=10)
            news_frame.pack(fill="x", padx=20, pady=10)
            
            title = ctk.CTkLabel(news_frame, text=article.get('title', 'No title'),
                                font=ctk.CTkFont(size=16, weight="bold"),
                                wraplength=800, anchor="w")
            title.pack(pady=10, padx=15, anchor="w")
            
            publisher = article.get('publisher', 'Unknown')
            source = article.get('source', 'News')
            ctk.CTkLabel(news_frame, text=f"📡 {source} • {publisher}",
                       font=ctk.CTkFont(size=12), text_color="gray").pack(padx=15, anchor="w")
            
            link = article.get('link', '')
            if link:
                ctk.CTkLabel(news_frame, text=f"🔗 {link[:70]}...",
                           font=ctk.CTkFont(size=10), text_color="#64b5f6").pack(pady=(5, 10), padx=15, anchor="w")
    
    def research_stock(self):
        symbol = self.research_entry.get().upper().strip()
        if not symbol:
            return
        
        for widget in self.research_content.winfo_children():
            widget.destroy()
        
        loading = ctk.CTkLabel(self.research_content, text=f"🔄 Researching {symbol}...",
                              font=ctk.CTkFont(size=18))
        loading.pack(pady=50)
        
        def fetch_research():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Clear loading
                for widget in self.research_content.winfo_children():
                    widget.destroy()
                
                # Header with add to watchlist
                header_frame = ctk.CTkFrame(self.research_content, fg_color="transparent")
                header_frame.pack(fill="x", padx=20, pady=20)
                
                company_name = info.get('longName', symbol)
                ctk.CTkLabel(header_frame, text=f"{symbol} - {company_name}",
                           font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
                
                ctk.CTkButton(header_frame, text="⭐ Add to Watchlist",
                            command=lambda: self.add_to_watchlist(symbol),
                            height=40).pack(side="right")
                
                # Company stats
                stats_frame = ctk.CTkFrame(self.research_content, corner_radius=10)
                stats_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(stats_frame, text="📊 Company Overview",
                           font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15, padx=20, anchor="w")
                
                # Key stats grid
                stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
                stats_grid.pack(fill="x", padx=20, pady=10)
                
                market_cap = info.get('marketCap', 0)
                market_cap_str = f"${market_cap/1e9:.2f}B" if market_cap > 1e9 else f"${market_cap/1e6:.2f}M"
                
                stats = [
                    ("Current Price", f"${info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))}"),
                    ("Market Cap", market_cap_str),
                    ("PE Ratio", f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else 'N/A'),
                    ("52 Week High", f"${info.get('fiftyTwoWeekHigh', 'N/A')}"),
                    ("52 Week Low", f"${info.get('fiftyTwoWeekLow', 'N/A')}"),
                    ("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else 'N/A'),
                    ("Volume", f"{info.get('volume', 0):,}"),
                    ("Avg Volume", f"{info.get('averageVolume', 0):,}"),
                    ("Beta", f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get('beta'), (int, float)) else 'N/A'),
                    ("EPS", f"${info.get('trailingEps', 'N/A'):.2f}" if isinstance(info.get('trailingEps'), (int, float)) else 'N/A'),
                    ("Sector", info.get('sector', 'N/A')),
                    ("Industry", info.get('industry', 'N/A'))
                ]
                
                row = 0
                col = 0
                for label, value in stats:
                    stat_box = ctk.CTkFrame(stats_grid, width=250, height=70)
                    stat_box.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
                    
                    ctk.CTkLabel(stat_box, text=label, font=ctk.CTkFont(size=11),
                               text_color="gray").pack(pady=(10, 0))
                    ctk.CTkLabel(stat_box, text=str(value), font=ctk.CTkFont(size=16, weight="bold")).pack()
                    
                    col += 1
                    if col > 2:
                        col = 0
                        row += 1
                
                # Earnings & trends
                earnings_frame = ctk.CTkFrame(self.research_content, corner_radius=10)
                earnings_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(earnings_frame, text="💰 Financial Performance",
                           font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15, padx=20, anchor="w")
                
                revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
                earnings_growth = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
                profit_margins = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
                roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
                
                trends_text = f"""Revenue Growth: {revenue_growth:.2f}%
Earnings Growth: {earnings_growth:.2f}%
Profit Margins: {profit_margins:.2f}%
Return on Equity: {roe:.2f}%
Debt to Equity: {info.get('debtToEquity', 'N/A')}
"""
                
                ctk.CTkLabel(earnings_frame, text=trends_text.strip(),
                           font=ctk.CTkFont(size=14), justify="left").pack(padx=20, pady=(0, 15), anchor="w")
                
                # Analyst recommendations
                if info.get('recommendationKey'):
                    rec_frame = ctk.CTkFrame(self.research_content, corner_radius=10)
                    rec_frame.pack(fill="x", padx=20, pady=10)
                    
                    ctk.CTkLabel(rec_frame, text="🎯 Analyst Consensus",
                               font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15, padx=20, anchor="w")
                    
                    rec = info.get('recommendationKey', 'N/A').upper()
                    target_high = info.get('targetHighPrice', 'N/A')
                    target_low = info.get('targetLowPrice', 'N/A')
                    target_mean = info.get('targetMeanPrice', 'N/A')
                    
                    rec_color = {
                        'STRONG_BUY': '#00e676',
                        'BUY': '#66bb6a',
                        'HOLD': '#ffa726',
                        'SELL': '#ff7043',
                        'STRONG_SELL': '#ef5350'
                    }.get(rec, 'gray')
                    
                    ctk.CTkLabel(rec_frame, text=f"Rating: {rec.replace('_', ' ')}",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color=rec_color).pack(padx=20, anchor="w")
                    
                    if target_mean != 'N/A':
                        ctk.CTkLabel(rec_frame, text=f"Price Target: ${target_mean:.2f} (Range: ${target_low:.2f} - ${target_high:.2f})",
                                   font=ctk.CTkFont(size=14)).pack(padx=20, pady=(5, 15), anchor="w")
                
                # News section
                news_frame = ctk.CTkFrame(self.research_content, corner_radius=10)
                news_frame.pack(fill="x", padx=20, pady=10)
                
                ctk.CTkLabel(news_frame, text="📰 Recent Company News",
                           font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15, padx=20, anchor="w")
                
                try:
                    news = ticker.news
                    if news and len(news) > 0:
                        for article in news[:5]:
                            article_frame = ctk.CTkFrame(news_frame, fg_color="#1a1a1a")
                            article_frame.pack(fill="x", padx=20, pady=5)
                            
                            ctk.CTkLabel(article_frame, text=article.get('title', 'No title'),
                                       font=ctk.CTkFont(size=14), wraplength=700, anchor="w").pack(pady=8, padx=15, anchor="w")
                            
                            ctk.CTkLabel(article_frame, text=f"📅 {article.get('publisher', 'Unknown')}",
                                       font=ctk.CTkFont(size=11), text_color="gray").pack(padx=15, pady=(0, 8), anchor="w")
                    else:
                        ctk.CTkLabel(news_frame, text="No recent news available for this stock.",
                                   text_color="gray", font=ctk.CTkFont(size=12)).pack(padx=20, pady=10, anchor="w")
                except:
                    ctk.CTkLabel(news_frame, text="News temporarily unavailable. Check back later.",
                               text_color="gray", font=ctk.CTkFont(size=12)).pack(padx=20, pady=10, anchor="w")
                
            except Exception as e:
                for widget in self.research_content.winfo_children():
                    widget.destroy()
                ctk.CTkLabel(self.research_content, text=f"❌ Error: Could not research {symbol}\n{str(e)}",
                           text_color="red", font=ctk.CTkFont(size=16)).pack(pady=50)
        
        thread = threading.Thread(target=fetch_research)
        thread.daemon = True
        thread.start()
    
    def add_to_watchlist(self, symbol):
        if symbol not in self.watchlist:
            self.watchlist.append(symbol)
            self.save_data()
            self.update_watchlist_display()
            if hasattr(self, 'status_label'):
                self.status_label.configure(text=f"✅ Added {symbol} to watchlist", text_color="green")
    
    def update_watchlist_display(self):
        for widget in self.watchlist_display.winfo_children():
            widget.destroy()
        
        if not self.watchlist:
            ctk.CTkLabel(self.watchlist_display, text="No stocks in watchlist",
                        text_color="gray").pack(pady=20)
            return
        
        for symbol in self.watchlist:
            watch_item = ctk.CTkFrame(self.watchlist_display)
            watch_item.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(watch_item, text=symbol, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
            
            ctk.CTkButton(watch_item, text="❌", width=30, command=lambda s=symbol: self.remove_from_watchlist(s),
                         fg_color="transparent", hover_color="#d32f2f").pack(side="right", padx=5)
    
    def remove_from_watchlist(self, symbol):
        if symbol in self.watchlist:
            self.watchlist.remove(symbol)
            self.save_data()
            self.update_watchlist_display()
    
    def add_stock(self):
        symbol = self.symbol_entry.get().upper().strip()
        shares_text = self.shares_entry.get().strip()
        price_text = self.price_entry.get().strip()
        
        if not symbol or not shares_text or not price_text:
            self.status_label.configure(text="❌ Fill all fields", text_color="red")
            return
        
        try:
            shares = float(shares_text)
            purchase_price = float(price_text)
            
            if shares <= 0 or purchase_price <= 0:
                self.status_label.configure(text="❌ Values must be positive", text_color="red")
                return
        except ValueError:
            self.status_label.configure(text="❌ Invalid numbers", text_color="red")
            return
        
        self.status_label.configure(text="⏳ Analyzing stock...", text_color="blue")
        self.update()
        
        def fetch_and_add():
            try:
                analysis = self.get_advanced_analysis(symbol)
                
                if not analysis:
                    self.status_label.configure(text=f"❌ Invalid symbol", text_color="red")
                    return
                
                stock_data = {
                    'symbol': symbol,
                    'shares': shares,
                    'purchase_price': purchase_price,
                    'current_price': analysis['current_price'],
                    'date_added': datetime.now().strftime("%Y-%m-%d"),
                    'analysis': analysis
                }
                
                self.portfolio.append(stock_data)
                self.save_data()
                self.update_portfolio_display()
                
                self.symbol_entry.delete(0, 'end')
                self.shares_entry.delete(0, 'end')
                self.price_entry.delete(0, 'end')
                
                self.status_label.configure(text=f"✅ Added {symbol}!", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"❌ Error adding stock", text_color="red")
        
        thread = threading.Thread(target=fetch_and_add)
        thread.daemon = True
        thread.start()
    
    def update_portfolio_display(self):
        for widget in self.portfolio_scroll.winfo_children():
            widget.destroy()
        
        if not self.portfolio:
            ctk.CTkLabel(self.portfolio_scroll, text="No stocks in portfolio\nAdd your first stock!",
                        font=ctk.CTkFont(size=16), text_color="gray").pack(pady=50)
            self.portfolio_summary.configure(text="Total: $0.00")
            return
        
        total_value = 0
        total_cost = 0
        
        for i, stock in enumerate(self.portfolio):
            stock_frame = ctk.CTkFrame(self.portfolio_scroll, corner_radius=10)
            stock_frame.pack(fill="x", pady=10, padx=5)
            
            current_value = stock['shares'] * stock['current_price']
            cost_basis = stock['shares'] * stock['purchase_price']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            total_value += current_value
            total_cost += cost_basis
            
            # Header
            header = ctk.CTkFrame(stock_frame, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(header, text=stock['symbol'],
                        font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
            
            ctk.CTkButton(header, text="❌", width=30,
                         command=lambda idx=i: self.delete_stock(idx),
                         fg_color="transparent", hover_color="#d32f2f").pack(side="right")
            
            # Price info
            price_frame = ctk.CTkFrame(stock_frame, fg_color="transparent")
            price_frame.pack(fill="x", padx=15, pady=5)
            
            details = f"💼 {stock['shares']:.2f} shares | 📊 Bought at ${stock['purchase_price']:.2f} | 💵 Now ${stock['current_price']:.2f}"
            ctk.CTkLabel(price_frame, text=details, font=ctk.CTkFont(size=13)).pack(side="left")
            
            # Gain/loss
            color = "#00e676" if gain_loss >= 0 else "#ef5350"
            sign = "+" if gain_loss >= 0 else ""
            gain_frame = ctk.CTkFrame(stock_frame, fg_color="transparent")
            gain_frame.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(gain_frame, text=f"{sign}${gain_loss:.2f} ({sign}{gain_loss_pct:.2f}%)",
                        font=ctk.CTkFont(size=18, weight="bold"),
                        text_color=color).pack(side="left")
            
            # Advanced analysis section
            analysis = stock.get('analysis')
            if analysis:
                analysis_frame = ctk.CTkFrame(stock_frame, fg_color="#1a1a1a", corner_radius=8)
                analysis_frame.pack(fill="x", padx=15, pady=10)
                
                # AI Signal
                signals = analysis.get('signals', {})
                recommendation = signals.get('recommendation', 'N/A')
                action = signals.get('action', '')
                signal_color = signals.get('color', 'gray')
                
                signal_header = ctk.CTkFrame(analysis_frame, fg_color="transparent")
                signal_header.pack(fill="x", padx=15, pady=10)
                
                ctk.CTkLabel(signal_header, text=f"🤖 AI Signal: {recommendation}",
                           font=ctk.CTkFont(size=16, weight="bold"),
                           text_color=signal_color).pack(side="left")
                
                # Risk level
                risk = analysis.get('risk_level', {})
                risk_text = f"⚠️ Risk: {risk.get('level', 'N/A')}"
                ctk.CTkLabel(signal_header, text=risk_text,
                           font=ctk.CTkFont(size=13),
                           text_color=risk.get('color', 'gray')).pack(side="right")
                
                # Action recommendation
                ctk.CTkLabel(analysis_frame, text=action,
                           font=ctk.CTkFont(size=12), text_color="#b0b0b0",
                           wraplength=700).pack(padx=15, pady=(0, 10), anchor="w")
                
                # Key signals (top 3)
                signal_list = signals.get('signals', [])
                if signal_list:
                    signals_text = ""
                    for sig_name, sig_desc, sig_score in signal_list[:3]:
                        signals_text += f"{sig_name}: {sig_desc}\n"
                    
                    ctk.CTkLabel(analysis_frame, text=signals_text.strip(),
                               font=ctk.CTkFont(size=11), text_color="#90caf9",
                               justify="left", wraplength=700).pack(padx=15, pady=(0, 10), anchor="w")
                
                # Technical indicators
                tech_frame = ctk.CTkFrame(analysis_frame, fg_color="#0d0d0d", corner_radius=5)
                tech_frame.pack(fill="x", padx=15, pady=(0, 10))
                
                rsi = analysis.get('rsi', 0)
                rsi_color = "#00e676" if rsi < 30 else "#ef5350" if rsi > 70 else "#ffa726"
                
                tech_text = f"📊 RSI: {rsi:.1f} | MA(7): ${analysis.get('ma_7', 0):.2f} | MA(20): ${analysis.get('ma_20', 0):.2f} | Volatility: {analysis.get('volatility', 0):.2f}%"
                ctk.CTkLabel(tech_frame, text=tech_text,
                           font=ctk.CTkFont(size=10), text_color="#808080").pack(pady=8, padx=10)
        
        # Update summary
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost) * 100 if total_cost > 0 else 0
        sign = "+" if total_gain >= 0 else ""
        
        self.portfolio_summary.configure(
            text=f"Total: ${total_value:,.2f} | {sign}${total_gain:,.2f} ({sign}{total_gain_pct:.1f}%)")
    
    def delete_stock(self, index):
        if 0 <= index < len(self.portfolio):
            self.portfolio.pop(index)
            self.save_data()
            self.update_portfolio_display()
    
    def refresh_portfolio(self):
        if not self.portfolio:
            return
        
        self.status_label.configure(text="🔄 Refreshing all stocks...", text_color="blue")
        self.update()
        
        def refresh():
            for stock in self.portfolio:
                analysis = self.get_advanced_analysis(stock['symbol'])
                if analysis:
                    stock['current_price'] = analysis['current_price']
                    stock['analysis'] = analysis
            
            self.save_data()
            self.update_portfolio_display()
            self.status_label.configure(text="✅ Portfolio updated!", text_color="green")
        
        thread = threading.Thread(target=refresh)
        thread.daemon = True
        thread.start()
    
    def clear_portfolio(self):
        self.portfolio = []
        self.save_data()
        self.update_portfolio_display()
        self.status_label.configure(text="✅ Portfolio cleared", text_color="green")

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
