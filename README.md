# 📊 Portfolio Tracker Pro - AI Enhanced

An intelligent stock portfolio tracker with AI-powered buy/sell signals, technical analysis, and live news integration.

## 🚀 Features
- Real-time stock price tracking
- AI-powered buy/sell recommendations
- Technical indicators (RSI, Moving Averages)
- Live news feed for each stock
- Calculate portfolio gains/losses
- Beautiful dark mode GUI

## 📦 Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Run the app:
```bash
python3 main.py
```

## 💡 How to Use
1. Enter a stock symbol (e.g., AAPL, TSLA, MSFT)
2. Input number of shares and purchase price
3. Click "Add to Portfolio"
4. View AI analysis, buy/sell signals, and latest news
5. Click "Refresh" to update all prices and analysis

## 🛠️ Tech Stack
- **Python 3**
- **CustomTkinter** - Modern GUI
- **yFinance** - Live stock data
- **Pandas** - Data analysis
- **Matplotlib** - Visualizations

## 📝 License
MIT License

## 👨‍💻 Created for [Hackathon Name]
```

### 4. **.gitignore**
Create this to exclude unnecessary files:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Portfolio data (optional - include if you don't want to save user data)
portfolio.json

# OS files
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
