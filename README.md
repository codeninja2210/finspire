# 💎 FinSpire: Gamified Financial Literacy Platform

> **📌 For evaluators:** Live app → https://finspire-pcx6esauptv8whcxkarx8o.streamlit.app
> If the app shows a "waking up" spinner, wait ~30 seconds and refresh.
> To run locally: `pip install -r requirements.txt` then `streamlit run finspire.py`

> **Master the markets through interactive simulation. Learn. Earn. Trade.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-URL-HERE.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Educational-green)

**Live Demo:** [https://YOUR-APP-URL-HERE.streamlit.app](https://YOUR-APP-URL-HERE.streamlit.app) *(Replace this link with your actual Streamlit URL)*

---

## 📖 What is FinSpire?

FinSpire is a **production-ready, gamified financial literacy web application** designed specifically for the Indian market. It shifts the paradigm from boring text quizzes to **interactive micro-learning simulations**.

Instead of giving users a "fake" ₹10,000,000 portfolio to play with, FinSpire forces users to **earn their trading capital by proving their knowledge**. 

### 🎯 The Core Loop
1. **Learn:** Read deeply researched, India-specific chapters (e.g., NSE/BSE mechanics, STCG/LTCG tax rules, SEBI regulations).
2. **Practice:** Use interactive widgets (Candlestick builders, Risk calculators, Options payoff charts).
3. **Earn:** Pass quizzes to unlock actual trading capital.
4. **Trade:** Use your unlocked capital to trade real Indian tickers (RELIANCE, TCS, HDFCBANK, etc.) with live P&L tracking.
5. **Reflect:** Journal your trades. An AI-integrated keyword scanner detects cognitive biases (FOMO, Revenge Trading, Anchoring).

---

## ✨ Key Features

| Module | Description |
| :--- | :--- |
| **📚 8 Deep-Lesson Chapters** | From stock market basics to complex Options & F&O. Each lesson includes worked examples, pitfalls, and real Indian market case studies. |
| **💹 Instrument-Level Trading** | Trade specific NSE blue chips (RELIANCE, INFY) or other assets. Tracks real-time weighted average cost basis and unrealized P&L. |
| **🎰 Options Paper Trading** | Interactive Black-Scholes pricing engine with real-time Greeks (Δ, Γ, Θ, V). Paper trade NIFTY weekly options. |
| **📓 Bias-Detecting Journal** | Log your trade reasoning. Natural language processing scans your entry to flag FOMO, Anchoring, or Revenge Trading. |
| **⏮️ Backtest Sandbox** | Replay NIFTY/SENSEX history. Test moving-average crossover strategies with performance metrics (Sharpe, Sortino, Max Drawdown). |
| **🏛️ Prop Firm Challenge** | Unlocked after earning ₹95,000. Take a simulated funded challenge with strict drawdown limits to prove your risk management. |
| **🏆 Gamification** | 19 unique achievements, XP system, and anonymous opt-in leaderboards. |
| **🇮🇳 Bilingual Support** | Full support for English and हिन्दी (Hindi). |

---

## 🛠️ Technology Stack

*   **Frontend & Logic:** [Streamlit](https://streamlit.io/) (Pure Python, no HTML/CSS/JS files)
*   **Data Visualization:** [Plotly](https://plotly.com/python/) (Interactive charts, equity curves, payoff graphs)
*   **Data Handling:** Pandas, NumPy
*   **Live Market Data:** `yfinance` (with graceful fallback to simulated prices if offline)

---

## 🚀 Run Locally

Want to run FinSpire on your own machine? It takes less than 2 minutes.

### 1. Clone the repository
git clone https://github.com/codeninja2210/finspire.git
cd finspire

pip install -r requirements.txt

streamlit run finspire.py
