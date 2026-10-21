"""
FinSpire v4.0 — Complete Financial Literacy & Trading Simulator (India)
=======================================================================
Learn · Earn · Trade · Journal · Options · Backtest · Prop · Leaderboard
Streamlit-native · India-focused · SEBI-compliant · Bilingual (EN/हिन्दी)

Author: Principal Python Engineer & UI Architect
License: Educational use
"""

import sys

# ============================================================================
# DEPENDENCY GUARD
# ============================================================================
_REQ = {"streamlit": "streamlit", "plotly": "plotly",
        "pandas": "pandas", "numpy": "numpy"}

def _has(m):
    try: __import__(m); return True
    except ImportError: return False

_miss = [p for m, p in _REQ.items() if not _has(m)]
if _miss:
    print(f"⚠️  Missing: {', '.join(_miss)}. Install: pip install {' '.join(_miss)}")
    sys.exit(1)

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import random, json, math, os, io
from datetime import datetime, timedelta, date
from collections import Counter, deque

HAS_YF = _has("yfinance")
if HAS_YF:
    import yfinance as yf

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="FinSpire | Learn. Earn. Trade.",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"about": "FinSpire v4 — Educational simulator. Not SEBI-registered."}
)

# ============================================================================
# MOBILE / PWA META INJECTION
# ============================================================================
components.html("""
<script>
    const meta = document.createElement('meta');
    meta.name = 'viewport';
    meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0';
    document.head.appendChild(meta);
    const themeColor = document.createElement('meta');
    themeColor.name = 'theme-color';
    themeColor.content = '#0a0f1e';
    document.head.appendChild(themeColor);
    const appleCapable = document.createElement('meta');
    appleCapable.name = 'apple-mobile-web-app-capable';
    appleCapable.content = 'yes';
    document.head.appendChild(appleCapable);
</script>
""", height=0)

# ============================================================================
# STYLING
# ============================================================================
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #0a0f1e 0%, #131a2e 100%); }
    .hero-title {
        font-size: 3rem; font-weight: 800; text-align: center;
        background: linear-gradient(90deg, #22d3ee, #a855f7, #f59e0b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    @media (max-width: 768px) { .hero-title { font-size: 2rem; } }
    .hero-sub { text-align: center; color: #94a3b8; font-size: 1rem;
                margin-bottom: 1.2rem; }
    .card {
        background: linear-gradient(135deg, #1a2332 0%, #243044 100%);
        border: 1px solid #2d3a50; border-radius: 16px; padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .metric-value { font-size: 1.7rem; font-weight: 700; color: #22d3ee;
                    margin: 0.3rem 0; }
    .metric-label { color: #94a3b8; font-size: 0.72rem;
                    text-transform: uppercase; letter-spacing: 1px; }
    .locked-card {
        background: #0f1729; border: 2px dashed #334155; border-radius: 14px;
        padding: 1.1rem; text-align: center; opacity: 0.65;
    }
    .unlocked-card {
        background: linear-gradient(135deg, #1a2332, #243044);
        border: 2px solid #10b981; border-radius: 14px; padding: 1.1rem;
    }
    .current-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        border: 2px solid #f59e0b; border-radius: 14px; padding: 1.1rem;
        box-shadow: 0 0 30px rgba(245, 158, 11, 0.3);
    }
    .insight {
        background: rgba(34,211,238,0.08); border-left: 4px solid #22d3ee;
        padding: 0.9rem 1rem; border-radius: 8px; margin: 0.9rem 0;
        color: #cbd5e1;
    }
    .danger {
        background: rgba(239,68,68,0.10); border-left: 4px solid #ef4444;
        padding: 0.85rem 1rem; border-radius: 8px; margin: 0.9rem 0;
        color: #fecaca; font-size: 0.9rem;
    }
    .bias-warning {
        background: rgba(245,158,11,0.10); border-left: 4px solid #f59e0b;
        padding: 0.7rem 1rem; border-radius: 8px; margin: 0.4rem 0;
        color: #fcd34d; font-size: 0.88rem;
    }
    .rupee-badge {
        display: inline-block;
        background: linear-gradient(90deg, #10b981, #059669);
        color: white; padding: 0.35rem 1rem; border-radius: 50px;
        font-weight: 700; font-size: 0.85rem;
    }
    .prop-badge {
        display: inline-block;
        background: linear-gradient(90deg, #a855f7, #ec4899);
        color: white; padding: 0.35rem 1rem; border-radius: 50px;
        font-weight: 700; font-size: 0.85rem;
    }
    .stage-chip {
        display: inline-block; padding: 0.28rem 0.75rem;
        border-radius: 50px; font-size: 0.75rem; font-weight: 600;
        margin-right: 0.3rem;
    }
    .stage-done { background: #10b981; color: white; }
    .stage-active { background: #f59e0b; color: white; }
    .stage-locked { background: #334155; color: #94a3b8; }
    .stButton > button {
        background: linear-gradient(90deg, #22d3ee, #a855f7); color: white;
        border: none; border-radius: 10px; padding: 0.5rem 1.3rem;
        font-weight: 600; width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(34,211,238,0.4);
    }
    .disclaimer-footer {
        background: rgba(15,23,42,0.9); border: 1px solid #334155;
        border-radius: 12px; padding: 0.9rem 1.2rem; margin-top: 2rem;
        color: #94a3b8; font-size: 0.78rem; line-height: 1.4;
    }
    .advisor-card {
        background: linear-gradient(135deg, #1a2332, #243044);
        border: 1px solid #2d3a50; border-radius: 12px;
        padding: 1rem; margin-bottom: 0.8rem;
    }
    .rank-row {
        display: flex; justify-content: space-between;
        padding: 0.6rem 1rem; border-radius: 10px;
        background: #1a2332; margin-bottom: 0.4rem;
    }
    .rank-1 { background: linear-gradient(90deg, #f59e0b, #b45309); color: white; }
    .rank-2 { background: linear-gradient(90deg, #94a3b8, #64748b); color: white; }
    .rank-3 { background: linear-gradient(90deg, #b45309, #78350f); color: white; }
    .hook-box {
        background: linear-gradient(135deg, rgba(34,211,238,0.12), rgba(168,85,247,0.08));
        border-left: 4px solid #22d3ee;
        padding: 1rem 1.2rem; border-radius: 10px; margin: 1rem 0 1.5rem 0;
        color: #e2e8f0; font-size: 1.05rem; font-style: italic;
        font-weight: 500;
    }
    .worked-example {
        background: linear-gradient(135deg, #1a2332, #243044);
        border-left: 4px solid #10b981;
        border-radius: 10px; padding: 1rem 1.2rem; margin: 0.8rem 0;
        color: #cbd5e1;
    }
    .worked-example pre {
        background: transparent; color: #cbd5e1; white-space: pre-wrap;
        font-family: inherit; font-size: 0.92rem; margin: 0.5rem 0 0 0;
        line-height: 1.55;
    }
    .pitfall-box {
        background: rgba(245,158,11,0.10); border-left: 4px solid #f59e0b;
        padding: 0.9rem 1.1rem; border-radius: 8px; margin: 0.8rem 0;
        color: #fcd34d; font-size: 0.92rem; line-height: 1.55;
    }
    .section-heading {
        color: #22d3ee; font-size: 1.15rem; font-weight: 700;
        margin: 1.8rem 0 0.6rem 0; padding-bottom: 0.4rem;
        border-bottom: 1px dashed #334155;
    }
    .takeaways-box {
        background: linear-gradient(135deg, rgba(16,185,129,0.10), rgba(34,211,238,0.05));
        border: 1px solid #10b981; border-radius: 12px;
        padding: 1rem 1.3rem; margin: 1.5rem 0;
    }
    .takeaways-box li { color: #cbd5e1; margin: 0.4rem 0; }
    .feedback-row {
        padding: 0.85rem 1rem; border-radius: 10px; margin: 0.6rem 0;
        font-size: 0.92rem; line-height: 1.55;
    }
    .feedback-correct {
        background: rgba(16,185,129,0.10);
        border-left: 4px solid #10b981; color: #d1fae5;
    }
    .feedback-wrong {
        background: rgba(239,68,68,0.08);
        border-left: 4px solid #ef4444; color: #fecaca;
    }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# BILINGUAL DICTIONARY
# ============================================================================
L = {
    "en": {
        "app_tagline": "Learn. Earn. Trade.",
        "curriculum": "Curriculum Progress",
        "capital": "Trading Capital",
        "nav": "Navigate",
        "learn": "Learn", "trade": "Trade Simulator",
        "options": "Options Paper Trade", "journal": "Journal",
        "backtest": "Backtest Sandbox", "achieve": "Achievements",
        "dash": "Dashboard", "prop": "Prop Firm",
        "leaderboard": "Leaderboard", "advisors": "Advisors",
        "read": "I've read this →",
        "practice_ready": "Ready for the quiz →",
        "submit_quiz": "Submit Answers",
        "pass_reward": "deposited into your trading account.",
        "pass_fail": "You need 2 of 3 correct to pass.",
        "next_chapter": "Next Chapter →",
        "buy": "Buy", "sell": "Sell",
        "place_order": "Place Order",
        "advance": "⏭️ Advance Market Round",
        "no_capital": "No trading capital yet. Complete Chapter 1 to earn your first ₹5,000.",
        "disclaimer_short": ("Educational simulation only. Not investment advice. "
                             "Not SEBI-registered. Past performance ≠ future returns."),
    },
    "hi": {
        "app_tagline": "सीखें। कमाएँ। ट्रेड करें।",
        "curriculum": "पाठ्यक्रम प्रगति",
        "capital": "ट्रेडिंग पूंजी",
        "nav": "नेविगेट",
        "learn": "सीखें", "trade": "ट्रेड सिम्युलेटर",
        "options": "ऑप्शन पेपर ट्रेड", "journal": "जर्नल",
        "backtest": "बैकटेस्ट सैंडबॉक्स", "achieve": "उपलब्धियाँ",
        "dash": "डैशबोर्ड", "prop": "प्रॉप फर्म",
        "leaderboard": "लीडरबोर्ड", "advisors": "सलाहकार",
        "read": "पढ़ लिया →",
        "practice_ready": "क्विज़ के लिए तैयार →",
        "submit_quiz": "उत्तर सबमिट करें",
        "pass_reward": "आपके ट्रेडिंग खाते में जमा हो गया।",
        "pass_fail": "पास होने के लिए 3 में से 2 सही चाहिए।",
        "next_chapter": "अगला अध्याय →",
        "buy": "खरीदें", "sell": "बेचें",
        "place_order": "ऑर्डर दें",
        "advance": "⏭️ बाज़ार आगे बढ़ाएँ",
        "no_capital": "अभी कोई पूंजी नहीं। पहला ₹5,000 कमाने के लिए अध्याय 1 पूरा करें।",
        "disclaimer_short": ("केवल शैक्षिक सिमुलेशन। निवेश सलाह नहीं। "
                             "SEBI-पंजीकृत नहीं।"),
    },
}

def t(k):
    return L[st.session_state.get("lang", "en")].get(k, L["en"].get(k, k))


# ============================================================================
# CURRICULUM — 8 CHAPTERS (Deep Lesson Format)
# ============================================================================
CURRICULUM = [
    {
        "id": "ch1", "title": "Foundations of Investing", "icon": "🌱",
        "reward": 5000, "practice": "calculator",
        "hook": "Your savings account is not a safe place for your money. "
                "It's a slow leak.",
        "deep_lesson": [
            {"heading": "The silent tax on idle money",
             "body": ("Most people in India are taught to keep their money in a savings account because it is 'safe'. "
                      "While it is true that your balance will not drop due to market crashes, keeping your wealth in cash is "
                      "actually a guaranteed way to get poorer over time.\n\n"
                      "This happens because of **inflation**—the rate at which the prices of everyday goods and services rise. "
                      "In India, savings accounts pay roughly 3% interest. However, inflation averages around 5% to 6%. "
                      "This means your 'real return' is negative. If your money grows by 3%, but the things you want to buy "
                      "become 6% more expensive, you have lost 3% of your purchasing power.\n\n"
                      "To actually build wealth, your money must grow faster than inflation. You need to put it into assets "
                      "like stocks, mutual funds, or real estate that have historically outpaced inflation."),
             "worked_example": ("Let's look at ₹1,00,000 over 10 years:\n"
                                "• In a savings account (3%): It grows to ₹1,34,392.\n"
                                "• Invested in an index fund (12% average): It grows to ₹3,10,585.\n"
                                "That is a difference of ₹1.76 Lakh just by moving your money out of a savings account."),
             "pitfall": ("Thinking 'Savings = Safe' and 'Stocks = Risky'. Savings is safe from volatility, but it is "
                         "guaranteed to lose to inflation. Stocks are volatile in the short term, but safe for building "
                         "wealth in the long term.")},
            {"heading": "What a stock actually is (and isn't)",
             "body": ("Many people think the stock market is just a digital casino. But buying a stock means you are buying "
                      "a real, physical piece of a business.\n\n"
                      "When you buy 10 shares of Infosys, you are not lending them money; you are becoming a part-owner "
                      "(a shareholder) of the company. You own a tiny slice of their offices, their computers, their contracts, "
                      "and their future profits.\n\n"
                      "Because you are an owner, you make money in two ways:\n"
                      "1. **Capital Appreciation:** If the company grows and becomes more valuable, other people will want to "
                      "buy your shares for a higher price.\n"
                      "2. **Dividends:** When the company makes a profit, they often share a portion of it with the owners "
                      "(you) as a cash payout."),
             "worked_example": ("You buy 10 shares of Infosys at ₹1,500 each (Total ₹15,000).\n"
                                "A year later, the company is doing great and the share price hits ₹1,900. Your holding is "
                                "now worth ₹19,000 (a profit of ₹4,000).\n"
                                "On top of that, they pay a dividend of ₹18 per share, putting an extra ₹180 directly into your bank account."),
             "pitfall": ("Confusing a stock's *price* with the company's *value*. The price is just what the last person "
                         "was willing to pay. The value is the actual health and profitability of the business. Don't let "
                         "short-term price swings blind you to the underlying business.")},
            {"heading": "Why companies sell shares",
             "body": ("If a company is making money, why would they sell pieces of it to the public? Because they need capital "
                      "to grow, and they have two ways to get it: Debt or Equity.\n\n"
                      "**Debt (Bonds):** They borrow from a bank. They have to pay it back with interest, regardless of whether "
                      "the business succeeds or fails.\n\n"
                      "**Equity (Stocks):** They sell a piece of ownership. They don't have to pay anything back! If the company "
                      "makes a profit, they share it with the shareholders. If they don't, they pay nothing.\n\n"
                      "High-growth companies (like tech startups) prefer selling equity because it is safer for their cash flow."),
             "worked_example": ("When Zomato had its Initial Public Offering (IPO) in 2021, it didn't go to a bank to take "
                                "a massive loan. Instead, it sold shares to the public and raised ~₹9,375 crore. They used this "
                                "money to acquire Blinkit and expand their business without being crushed by bank interest payments."),
             "pitfall": ("Thinking 'I don't want to bet on companies, I'll just keep my money in a Fixed Deposit.' Keeping "
                         "money in an FD is also a bet—it is a bet that inflation will stay low. Every financial decision is a bet.")},
            {"heading": "India's market infrastructure",
             "body": ("The Indian stock market is a massive, highly regulated machine. To trade in it, you need to know the "
                      "players:\n\n"
                      "• **NSE and BSE:** These are the stock exchanges. They are the digital marketplaces where buyers and "
                      "sellers meet (BSE is Asia's oldest exchange, established in 1875).\n"
                      "• **SEBI:** The regulator. They are the police of the market, ensuring no one cheats you.\n"
                      "• **Depositories (NSDL & CDSL):** These act like your bank, but for shares. When you buy a stock, "
                      "it is held electronically in your 'Demat' account here.\n"
                      "• **Brokers:** Companies like Zerodha or Groww that give you the app to actually place the buy/sell orders."),
             "worked_example": ("You open a Zerodha account (Broker) and complete your KYC (SEBI requirement). You transfer "
                                "money to your trading account. You place an order to buy 5 shares of Reliance on the NSE. "
                                "The next day (T+1), those 5 shares appear in your Demat account (NSDL)."),
             "pitfall": ("Never open a Demat account with unregistered 'advisory groups' or WhatsApp tip brokers. Always verify "
                         "that your broker is registered with SEBI. The official SEBI website has a list of authorized brokers.")},
        ],
        "key_takeaways": [
            "Cash in a savings account is guaranteed to lose purchasing power to inflation over time.",
            "A stock is fractional ownership. You make money from price growth and dividends.",
            "Companies sell equity to raise capital without being forced to make fixed loan repayments.",
            "NSE + BSE are exchanges; SEBI regulates; NSDL/CDSL hold your shares electronically.",
        ],
        "quiz": [
            {"q": "Owning a stock means…",
             "options": ["You lent money to the company",
                         "You own a small piece of the company",
                         "You work for the company"],
             "correct": 1,
             "explain_correct": ("Stock = equity = ownership. Legal claim on assets and future profits proportional to shareholding."),
             "explain_wrong": ("Lending = bond. Working = employment. Only stock means ownership."),
             "mental_model": "Stock = slice of pie. Bond = IOU on pie."},
            {"q": "Why is keeping all money in a savings account risky?",
             "options": ["Banks steal it",
                         "Inflation erodes purchasing power faster than interest grows it",
                         "RBI freezes accounts"],
             "correct": 1,
             "explain_correct": ("Savings 3%, inflation 5–6%. Real return is negative. Money 'grows' on paper but buys less each year."),
             "explain_wrong": ("Banks don't steal (₹5L insured by DICGC). The real risk is inflation."),
             "mental_model": "If return < inflation, 'safe' money is melting."},
            {"q": "Which Indian regulator oversees stock markets?",
             "options": ["RBI", "SEBI", "IRDAI"], "correct": 1,
             "explain_correct": ("SEBI — Securities and Exchange Board of India, est. 1992. Regulates exchanges, brokers, MFs, listed companies."),
             "explain_wrong": ("RBI = banks. IRDAI = insurance. AMFI = industry body, not regulator."),
             "mental_model": "Banking → RBI. Insurance → IRDAI. Markets → SEBI."},
        ],
    },
    {
        "id": "ch2", "title": "How Markets Actually Work", "icon": "🏛️",
        "reward": 7500, "practice": "orderbook",
        "hook": "The stock price you see is not 'the price'. It's the last "
                "price at which two strangers agreed to trade.",
        "deep_lesson": [
            {"heading": "The order book — where prices are born",
             "body": ("When you look at a stock chart, you see a single price. But behind that number is a constant war between "
                      "buyers and sellers called the **Order Book**.\n\n"
                      "At any second, there are two queues:\n"
                      "• The **Bid**: The highest price a buyer is currently willing to pay.\n"
                      "• The **Ask**: The lowest price a seller is currently willing to accept.\n\n"
                      "The difference between these two is called the **Spread**. The last traded price is simply the moment "
                      "when a buyer gave up and paid the Ask, or a seller gave up and accepted the Bid."),
             "worked_example": ("Reliance is trading with a Bid of ₹2,849.50 and an Ask of ₹2,850.00. The spread is 50 paise. "
                                "However, a tiny, unknown small-cap stock might have a Bid of ₹99 and an Ask of ₹101. The spread is ₹2 (2%). "
                                "If you buy and immediately sell that small-cap, you instantly lose 2% of your money."),
             "pitfall": ("Using 'Market Orders' on illiquid (low-volume) stocks. If the spread is wide and you place a market order, "
                         "you will experience 'slippage'—your order gets filled at a much worse price than what was on your screen. "
                         "Always use Limit Orders if the spread is wide.")},
            {"heading": "Indices — the market's heartbeat",
             "body": ("You constantly hear on the news: 'The market is up today!' But what does that mean?\n\n"
                      "They are usually referring to an **Index**. An index is a mathematical basket of the biggest and most "
                      "important companies. When the basket goes up, we say the 'market' is up.\n\n"
                      "• **NIFTY 50:** Tracks the 50 largest companies on the NSE.\n"
                      "• **SENSEX:** Tracks the top 30 companies on the BSE.\n"
                      "• **Bank NIFTY:** Tracks the 12 largest banks.\n\n"
                      "These indices use a 'weighted' system. If Reliance has a much larger market cap than ITC, Reliance's "
                      "price moves will affect the NIFTY much more than ITC's moves."),
             "worked_example": ("NIFTY goes up by 0.8%. This might be because Reliance went up 1.5%, HDFC went up 0.3%, Infosys "
                                "went down 0.2%, and ITC went up 2.1%. The total mathematical weight of the winners outweighed the losers."),
             "pitfall": ("Assuming 'Market up = My stock up'. Indices are just an average. It is very common for the NIFTY to be "
                         "up 1% while your specific stock is down 5% because of bad company news.")},
            {"heading": "Market hours and settlement (IST)",
             "body": ("The Indian stock market has strict timing rules (IST):\n\n"
                      "• **9:00 AM – 9:15 AM:** Pre-open market. You can place orders, but they only execute at 9:15.\n"
                      "• **9:15 AM – 3:30 PM:** Normal trading hours.\n"
                      "• **Settlement (T+1):** India adopted T+1 settlement in Jan 2023. This means if you buy a stock on "
                      "Monday (T), the actual shares are transferred to your Demat account on Tuesday (T+1)."),
             "worked_example": ("You buy 100 shares of Infosys on Monday at 11 AM. The cash leaves your bank account immediately. "
                                "On Tuesday evening, the 100 shares officially appear in your Demat. You can only sell them on Wednesday."),
             "pitfall": ("Expecting to sell shares the same day you bought them. Unless you are explicitly using the 'Intraday' "
                         "(MIS) product, you cannot sell delivery shares on the same day because they haven't been settled yet.")},
            {"heading": "Who actually moves the market",
             "body": ("Retail investors (you and me) trade in small numbers. We do not set the direction of the market. "
                      "The real power lies with the **Big Money**:\n\n"
                      "• **FIIs (Foreign Institutional Investors):** Huge global funds (like American or European pension funds) "
                      "that invest in India.\n"
                      "• **DIIs (Domestic Institutional Investors):** Indian mutual funds, LIC, and insurance companies.\n\n"
                      "When FIIs decide to pull their money out of India, the market drops because the supply of shares is massive. "
                      "DIIs usually step in to buy, but FII flows dominate the trend."),
             "worked_example": ("In March 2020 (COVID crash), FIIs sold ₹60,000 crore worth of Indian stocks in a single month. "
                                "The NIFTY dropped 38%. DIIs bought heavily, and six months later, the market recovered over 60%."),
             "pitfall": ("Trying to 'beat the market' by day trading constantly. Brokerage fees, STT (tax), and slippage usually "
                         "eat up 0.3% to 1% of your capital on every single round trip. The more you trade, the more you lose to friction.")},
        ],
        "key_takeaways": [
            "Price is just the last agreed trade. The bid/ask spread is a hidden tax on your trades.",
            "Indices summarize the market. They correlate with individual stocks, but don't dictate them.",
            "India runs on T+1 settlement. Shares arrive next business day.",
            "FII and DII flows dictate market direction; retail volume is just background noise.",
        ],
        "quiz": [
            {"q": "Bid = ₹99, Ask = ₹101. What is the spread?",
             "options": ["₹1", "₹2", "₹200"], "correct": 1,
             "explain_correct": ("Spread = ask − bid = ₹101 − ₹99 = ₹2. On a ₹100 stock that's 2% — huge tax on frequent trading."),
             "explain_wrong": ("₹1 = midpoint offset. ₹200 = meaningless multiplication."),
             "mental_model": "Spread = ask − bid."},
            {"q": "NIFTY 50 tracks how many companies?",
             "options": ["30", "50", "500"], "correct": 1,
             "explain_correct": ("NIFTY 50 = 50 NSE companies. SENSEX = 30 BSE. NIFTY 500 = 500 companies."),
             "explain_wrong": ("30 is SENSEX. 500 is NIFTY 500. Don't mix up."),
             "mental_model": "NIFTY 50 = NSE's 50. SENSEX = BSE's 30."},
            {"q": "What does T+1 settlement mean?",
             "options": ["Settles one day after execution",
                         "Settles after 1 week", "Settles instantly"],
             "correct": 0,
             "explain_correct": ("T = trade day. +1 = one business day for delivery. India adopted T+1 in Jan 2023."),
             "explain_wrong": ("T+0 is future. T+5 was old. T+1 = next business day."),
             "mental_model": "T+1 = trade today, own tomorrow."},
        ],
    },
    {
        "id": "ch3", "title": "Reading Candlesticks", "icon": "🕯️",
        "reward": 10000, "practice": "candle_builder",
        "hook": "Each candle is a fight. The wick shows where one side tried "
                "and got rejected.",
        "deep_lesson": [
            {"heading": "The four numbers in every candle",
             "body": ("If you look at a stock chart, you don't see lines—you see candles. A candlestick compresses a massive "
                      "amount of information into one little visual. It tells you exactly what happened during a specific time "
                      "period (e.g., one day).\n\n"
                      "Every candle contains four numbers:\n"
                      "• **Open:** The price when the period started.\n"
                      "• **Close:** The price when the period ended.\n"
                      "• **High:** The absolute highest price reached.\n"
                      "• **Low:** The absolute lowest price reached.\n\n"
                      "The thick part (the Body) shows the distance between Open and Close. The thin lines (the Wicks) show the High and Low.\n"
                      "Green = Close > Open (Buyers won). Red = Close < Open (Sellers won)."),
             "worked_example": ("Reliance today: Open = ₹2,800, High = ₹2,850, Low = ₹2,780, Close = ₹2,840.\n"
                                "The body is green because ₹2,840 (Close) is higher than ₹2,800 (Open).\n"
                                "The upper wick goes up to ₹2,850, and the lower wick goes down to ₹2,780."),
             "pitfall": ("Ignoring the wicks. A candle can be green (close > open), but if it has a massive upper wick, it means sellers "
                         "smashed the price down from the highs. The wick often tells a more important story than the body color.")},
            {"heading": "The three candles that matter most",
             "body": ("While there are hundreds of candlestick patterns, three are incredibly important for beginners:\n\n"
                      "1. **Doji:** A candle where the Open and Close are almost identical. It looks like a cross. It represents "
                      "total indecision. The buyers and sellers fought to a standstill.\n"
                      "2. **Hammer:** A small body with a long lower wick. It happens at the bottom of a downtrend. Sellers tried "
                      "to push it down, but buyers fought back hard. It suggests a bullish reversal.\n"
                      "3. **Shooting Star:** A small body with a long upper wick. It happens at the top of an uptrend. Buyers "
                      "tried to push it up, but sellers dumped it. It suggests a bearish reversal."),
             "worked_example": ("NIFTY drops to a support level of 22,000. It forms a candle that opens at 22,050, closes at 22,040, "
                                "but drops all the way to 21,850 during the day. This creates a massive ₹200 lower wick (a Hammer). "
                                "The buyers have clearly stepped in to defend this price."),
             "pitfall": ("Trading a Doji or Hammer in a vacuum. A Hammer in the middle of a random chart means nothing. These candles "
                         "ONLY matter if they appear at key support/resistance levels or moving averages.")},
            {"heading": "Why volume is the truth serum",
             "body": ("Volume is the number of shares traded during the candle's time period. If price is the engine, volume is the fuel.\n\n"
                      "A massive price move on low volume is a lie. It means a few retail traders pushed the price, but the big "
                      "institutions are not participating.\n\n"
                      "A breakout (when a stock breaks above a resistance level) is only valid if it happens on **high volume**. "
                      "If a stock crosses ₹500 but volume is lower than average, it is likely a 'fakeout' and will crash right back down."),
             "worked_example": ("A stock has been stuck at ₹510 resistance for weeks. On Tuesday, it crosses ₹510, but volume is "
                                "only 1.3x the average. It's weak. On Wednesday, it crosses ₹510 again, but this time volume is "
                                "5x the average. The breakout is real."),
             "pitfall": ("Falling for low-volume breakouts. This is the #1 trap for retail traders. If you don't see a massive spike "
                         "in volume, do not trust the price breakout.")},
        ],
        "key_takeaways": [
            "Every candle = OHLC. Body = open-to-close; wicks = rejections.",
            "Doji = indecision. Hammer = bullish reversal. Shooting Star = bearish.",
            "Wick length often matters more than body color.",
            "Breakouts need volume confirmation.",
        ],
        "quiz": [
            {"q": "A green candle means…",
             "options": ["Close < Open", "Close > Open", "Close = Open"],
             "correct": 1,
             "explain_correct": "Green = close above open (bulls won).",
             "explain_wrong": "Close<Open = red. Close=Open = Doji.",
             "mental_model": "Green = close above open."},
            {"q": "A hammer candle with long lower wick at support suggests…",
             "options": ["Sellers in control",
                         "Buyers defended the low — potential reversal up",
                         "Volume is irrelevant"],
             "correct": 1,
             "explain_correct": ("Long lower wick = sellers pushed down but buyers overwhelmed and closed near top. Bullish reversal at tested support."),
             "explain_wrong": ("'Sellers in control' = shooting star. Volume always matters."),
             "mental_model": "Hammer at support = bulls planted a flag."},
            {"q": "A breakout on very low volume is usually…",
             "options": ["Very reliable", "A trap / weak signal", "Best entry"],
             "correct": 1,
             "explain_correct": ("Low volume = low conviction. Professionals wait for 1.5–2× average volume to confirm."),
             "explain_wrong": ("'Very reliable' is backwards. 'Best entry' ignores failure rate."),
             "mental_model": "Volume is the engine."},
        ],
    },
    {
        "id": "ch4", "title": "Trends, Bulls & Bears", "icon": "🐂",
        "reward": 12500, "practice": "trend_spotter",
        "hook": "Trends don't end because they're 'due'. They end because the "
                "buyers or sellers run out of ammunition.",
        "deep_lesson": [
            {"heading": "Reading the three market states",
             "body": ("Markets are always in one of three states:\n\n"
                      "1. **Uptrend (Bull Market):** The price is making Higher Highs (peaks are higher than previous peaks) "
                      "and Higher Lows (dips are higher than previous dips). It looks like a staircase going up.\n"
                      "2. **Downtrend (Bear Market):** The price is making Lower Highs and Lower Lows. A staircase going down.\n"
                      "3. **Sideways (Range-bound):** The price bounces horizontally between two levels.\n\n"
                      "The golden rule of trading is 'The Trend is your Friend'. Do not try to fight the current trend."),
             "worked_example": ("In 2023, NIFTY moved: 17,800 → dropped to 16,800 → rallied to 19,900 → dipped to 18,800 → rallied "
                                "to 21,700. The dip stopped higher than the previous dip (18,800 > 16,800). The rally went higher than "
                                "the previous rally. It was a textbook uptrend."),
             "pitfall": ("Thinking a 'red day' means the market is bearish. Trends are measured over weeks and months using swing "
                         "highs and swing lows, not by looking at a single red candle.")},
            {"heading": "The five drivers of trend",
             "body": ("Why do trends start? What pushes millions of people to buy or sell? There are 5 macro drivers in India:\n\n"
                      "1. **FII/DII Flows:** Are the big institutions buying or selling?\n"
                      "2. **RBI Policy:** Interest rates. Low rates = cheap loans = market booms. High rates = market drops.\n"
                      "3. **Union Budget:** Government spending on infrastructure or taxes.\n"
                      "4. **Corporate Earnings:** Are companies actually making profits?\n"
                      "5. **Global Cues:** What is the US Federal Reserve doing? Are crude oil prices rising?"),
             "worked_example": ("May 2024: Exit polls predicted a stable government. The market rallied 3% in a single day. The driver "
                                "was political stability, which suggested continuity in government capex (infrastructure spending)."),
             "pitfall": ("Looking at technical charts without looking at the news. A beautiful chart pattern will completely fail if "
                         "the RBI announces a surprise interest rate hike.")},
            {"heading": "Support, resistance, and why they matter",
             "body": ("**Support** is a price floor where buyers aggressively step in. **Resistance** is a ceiling where sellers "
                      "aggressively unload.\n\n"
                      "But here is the magic of market psychology: when a level breaks, it flips.\n\n"
                      "• **Broken resistance becomes support:** People who missed the breakout buy the dip to get in.\n"
                      "• **Broken support becomes resistance:** People who bought at the floor are trapped and want to sell to "
                      "break even when the price comes back up."),
             "worked_example": ("NIFTY held the 22,000 level five times. On the sixth try, it broke down to 21,700. Every time it "
                                "rallied back up to 22,000, it got sold off. The old support (22,000) had become a new resistance."),
             "pitfall": ("Thinking heavily tested support is stronger. It's actually the opposite. Every time a support level is "
                         "tested, the buyers defending it get exhausted. The more times it is tested, the higher the chance it breaks.")},
        ],
        "key_takeaways": [
            "Uptrend = HH + HL. Downtrend = LH + LL.",
            "Trends are driven by flows, policy, budget, earnings, and global cues.",
            "Broken support becomes resistance; broken resistance becomes support.",
            "Heavily tested support is closer to breaking, not safer.",
        ],
        "quiz": [
            {"q": "Higher highs + higher lows = ?",
             "options": ["Bearish trend", "Bullish trend", "Sideways"],
             "correct": 1,
             "explain_correct": ("HH + HL = classic bullish structure. Intact until a lower low or lower high."),
             "explain_wrong": ("Bearish is opposite. Sideways is neither."),
             "mental_model": "HH + HL = bull."},
            {"q": "FIIs sold ₹10,000 cr in a day. Likely short-term impact?",
             "options": ["NIFTY up sharply", "NIFTY down / pressure", "No effect"],
             "correct": 1,
             "explain_correct": ("₹10k cr net selling = huge supply. DIIs absorb some but downward pressure dominates."),
             "explain_wrong": ("FIIs hold ~20% of NSE market cap. Flow matters."),
             "mental_model": "Big money exits → market feels weight."},
            {"q": "Price bounces 5 times off ₹500 then breaks below. This is…",
             "options": ["Support holding", "Support breakdown — bearish",
                         "Bullish"],
             "correct": 1,
             "explain_correct": ("Heavily retested support weakens. Break becomes resistance. Sharp move due to stop clusters."),
             "explain_wrong": ("'Holding' would require a bounce. 'Bullish' is the opposite."),
             "mental_model": "N tests = N reasons to break."},
        ],
    },
    {
        "id": "ch5", "title": "Strategy & Risk Management", "icon": "🎯",
        "reward": 15000, "practice": "position_sizer",
        "hook": "You don't get rich by picking winners. You get rich by not "
                "blowing up on the losers.",
        "deep_lesson": [
            {"heading": "The 1% rule (and why it's non-negotiable)",
             "body": ("Most beginners focus on 'How much money can I make?' Professionals focus on 'How much can I lose?'\n\n"
                      "The golden rule of trading is to **never risk more than 1% to 2% of your total capital on a single trade**.\n\n"
                      "Why? Because of the brutal math of drawdowns. If you lose 50% of your account, you need to make 100% just to "
                      "get back to where you started. If you risk 10% per trade and hit a losing streak of 5 trades, you are down 50%. "
                      "But if you risk 1% per trade, a 5-trade losing streak only puts you down 5%, which is easily recoverable."),
             "worked_example": ("You have ₹1,00,000. You risk 1% (₹1,000) per trade. You lose 5 trades in a row. You are down ₹5,000. "
                                "You still have ₹95,000.\n"
                                "If you risked 5% (₹5,000) per trade and lost 5 in a row, you would be down ₹25,000 (25% of your account)."),
             "pitfall": ("Sizing your trades based on how confident you feel. Confidence is an emotion. Position size must be "
                         "calculated mathematically based on your stop-loss distance, not your gut feeling.")},
            {"heading": "Position sizing — the formula that saves you",
             "body": ("How do you actually apply the 1% rule? You use a formula to calculate exactly how many shares to buy.\n\n"
                      "**The Formula:**\n"
                      "(Total Capital × Risk %) ÷ (Entry Price − Stop Loss Price) = Number of Shares\n\n"
                      "This ensures that if your stop loss is hit, you lose exactly the amount you planned to risk, no more."),
             "worked_example": ("Capital: ₹1,00,000. Risk: 1% (₹1,000).\n"
                                "You want to buy a stock at ₹500. Your stop loss is at ₹480.\n"
                                "Risk per share = ₹20.\n"
                                "Position Size = 1000 ÷ 20 = 50 shares.\n"
                                "If the stock drops to ₹480, you lose exactly ₹1,000."),
             "pitfall": ("Buying round numbers like 100 shares or 500 shares without calculating. If you buy 500 shares in the above "
                         "example, your risk is ₹10,000 (10% of your account). One bad trade could wipe out a month of gains.")},
            {"heading": "Risk:Reward — the only equation that matters",
             "body": ("You do not need to be right more than 50% of the time to make money. You just need a good **Risk:Reward (R:R) ratio**.\n\n"
                      "R:R compares how much you stand to gain vs how much you stand to lose.\n"
                      "• A 1:1 ratio means you risk ₹1 to make ₹1. You need >50% win rate to survive.\n"
                      "• A 1:2 ratio means you risk ₹1 to make ₹2. You only need a 34% win rate to break even!\n"
                      "• A 1:3 ratio means you risk ₹1 to make ₹3. You only need a 25% win rate."),
             "worked_example": ("Strategy A: Win rate 60%, but R:R is 1:1. Over 10 trades: 6 wins (+6) - 4 losses (-4) = +2 units profit.\n"
                                "Strategy B: Win rate 40%, but R:R is 1:3. Over 10 trades: 4 wins (+12) - 6 losses (-6) = +6 units profit.\n"
                                "Strategy B is 3x more profitable, even though you lose more often!"),
             "pitfall": ("Taking trades where the target is too close. If you risk ₹10 to make ₹5 (1:0.5), one single loss will wipe out "
                         "two of your wins. Never take a trade unless the potential reward is at least twice your risk (1:2).")},
            {"heading": "The rules that never bend",
             "body": ("To survive long-term, you must build rules and never break them:\n\n"
                      "1. **Always use a stop-loss.** No exceptions.\n"
                      "2. **Never average a loser.** If a stock goes against you, don't buy more to 'bring down the average'. Cut the loss.\n"
                      "3. **Two losses = stop for the day.** When you lose, emotion takes over. Protect yourself from revenge trading.\n"
                      "4. **No FOMO.** If you missed the move, let it go. There is always another trade."),
             "worked_example": ("You buy at ₹500 with a stop at ₹490. The next day, news breaks, the stock crashes, and you get filled at "
                                "₹489.80. Because you used a stop-loss, you lost ₹10.20 per share. If you didn't use a stop, that stock might "
                                "have dropped to ₹400, wiping out 20% of your account."),
             "pitfall": ("Thinking 'I will just watch it and sell if it drops too much.' Human psychology makes this impossible. When "
                         "you are losing money, your brain goes into denial. You will hold the loser until it becomes a disaster.")},
        ],
        "key_takeaways": [
            "Risk 1–2% of your total capital per trade.",
            "Size = (Capital × Risk%) ÷ (Entry − Stop).",
            "R:R ≥ 1:2. A 1:3 strategy at 40% win rate is better than a 1:1 at 60%.",
            "Stop-loss on every single trade.",
        ],
        "quiz": [
            {"q": "Capital ₹50,000, risk 2%, entry ₹100, stop ₹95. Position size?",
             "options": ["100 shares", "200 shares", "500 shares"],
             "correct": 1,
             "explain_correct": ("Risk = 2% × 50k = ₹1,000. Per-share risk ₹5. Position = 200 shares. Loss if stopped = ₹1,000 = exactly 2%."),
             "explain_wrong": ("100 = 1% too small. 500 = 5% too much."),
             "mental_model": "Size = Capital×Risk ÷ (Entry−Stop)."},
            {"q": "Which R:R is usually profitable even at 40% win rate?",
             "options": ["1:1", "1:2", "1:0.5"], "correct": 1,
             "explain_correct": ("1:2 at 40% = +0.20R per trade. Positive expectancy with losing win rate."),
             "explain_wrong": ("1:1 at 40% = −0.20R. 1:0.5 = −0.40R. Both losing."),
             "mental_model": "1:2 or better."},
            {"q": "When should you trade without a stop-loss?",
             "options": ["When very confident", "Never", "On small positions"],
             "correct": 1,
             "explain_correct": ("Never. Confidence isn't an edge. Stops = survival."),
             "explain_wrong": ("'Confident' trades lose big. Small positions train bad habits."),
             "mental_model": "No stop = no trade."},
        ],
    },
    {
        "id": "ch6", "title": "Psychology & Drawdowns", "icon": "🧠",
        "reward": 20000, "practice": "bias_identifier",
        "hook": "The market isn't rigged against you. Your own brain is.",
        "deep_lesson": [
            {"heading": "The four biases that destroy portfolios",
             "body": ("The hardest part of trading isn't math—it's psychology. Your brain is wired to make bad financial decisions:\n\n"
                      "• **FOMO (Fear of Missing Out):** Buying an asset just because it's going up fast and everyone is talking about it. You always buy the top.\n"
                      "• **Revenge Trading:** You lose ₹5,000, get angry, and immediately double your position size to win it back. You almost always lose more.\n"
                      "• **Confirmation Bias:** You bought a stock, so now you only read news articles that agree with you, ignoring all the red flags.\n"
                      "• **Anchoring:** You refuse to sell a stock because 'it used to be ₹500'. The market doesn't care what it used to be."),
             "worked_example": ("Zomato peaked around ₹160 in 2021. A trader bought at ₹150. It dropped to ₹100, but he refused to sell because he was 'anchored' to the ₹150 price. Two years later, it was at ₹60. He lost 60% of his money waiting to 'break even'."),
             "pitfall": ("Thinking 'I am a logical person, I won't fall for these'. Everyone says this. The human brain is biologically wired for these biases. You need rules to protect yourself from yourself.")},
            {"heading": "Drawdown math — why 50% down is not 50% up",
             "body": ("Losses in the market are asymmetric. This means it takes much more effort to recover from a loss than it does to make the money in the first place.\n\n"
                      "• If you lose 10%, you need a 11.1% gain to break even.\n"
                      "• If you lose 50%, you need a 100% gain to break even.\n"
                      "• If you lose 90%, you need a 900% gain to break even.\n\n"
                      "This is why protecting your capital is rule #1. A massive drawdown can trap you for decades."),
             "worked_example": ("You have ₹10 Lakhs. The market crashes and you drop to ₹5 Lakhs (a 50% drawdown). Your money now needs to double (a 100% return) just to get back to where you started. If the market averages a 12% return per year, it will take you 6 years just to break even, losing all that time to inflation."),
             "pitfall": ("Saying 'I will just hold and wait for it to recover' without a plan. If you don't have a stop-loss or risk management, you might panic and sell at the absolute bottom.")},
            {"heading": "Why journaling works (and how to do it)",
             "body": ("If you want to improve, you must keep a trading journal. But it's not just a record of your profits and losses.\n\n"
                      "For every trade, log:\n"
                      "• Why you entered the trade (the setup).\n"
                      "• How you were feeling (calm, angry, rushed?)\n"
                      "• The Risk:Reward ratio.\n\n"
                      "Once a week, review the journal. Look for behavioral patterns. Are your losses always happening after lunch? Are your biggest losses always right after a previous loss?"),
             "worked_example": ("A trader reviews his 30-day journal and realizes that 12 out of his 15 losing trades happened immediately after a previous loss. Diagnosis: Revenge trading. Solution: He implements a rule to wait 1 hour after any loss before taking a new trade."),
             "pitfall": ("Journaling but never reviewing it. A journal without a weekly review is just a diary. The magic is in finding the patterns and changing your behavior.")},
        ],
        "key_takeaways": [
            "FOMO, revenge trading, confirmation bias, and anchoring are constantly fighting your logic.",
            "A 50% drawdown requires a 100% gain just to recover.",
            "Journal every trade. Review it weekly to find your emotional patterns.",
            "Define your maximum drawdown tolerance BEFORE you invest.",
        ],
        "quiz": [
            {"q": "You lost ₹5,000 today and immediately double your next trade to win it back. This is…",
             "options": ["Smart", "Revenge trading", "Position sizing"],
             "correct": 1,
             "explain_correct": ("Revenge trading — emotion hijacks decision. Trade based on 'getting even', not setup."),
             "explain_wrong": ("'Smart' doubles risk when compromised. 'Sizing' is disciplined; this is the opposite."),
             "mental_model": "After loss, size down or sit out."},
            {"q": "A 50% drawdown requires what gain to recover?",
             "options": ["50%", "75%", "100%"], "correct": 2,
             "explain_correct": ("₹100 → ₹50 needs +100% to return to ₹100. −75% needs +300%. −90% needs +900%."),
             "explain_wrong": ("50% of ₹50 = ₹25, not enough. 75% arbitrary."),
             "mental_model": "Lose 50% → need +100%."},
            {"q": "Holding a losing stock because 'it was higher once' is…",
             "options": ["Anchoring bias", "Good strategy", "Value investing"],
             "correct": 0,
             "explain_correct": ("Anchoring — clinging to a past price. Market doesn't know your entry. Evaluate on today's merits."),
             "explain_wrong": ("'Good' = no. 'Value investing' = fundamentals, not price nostalgia."),
             "mental_model": "Market doesn't know your entry."},
        ],
    },
    {
        "id": "ch7", "title": "Indian Tax & Regulations", "icon": "📜",
        "reward": 25000, "practice": "tax_calculator",
        "hook": "The taxman is your silent partner. Learn his rules before he "
                "teaches them to you.",
        "deep_lesson": [
            {"heading": "STCG vs. LTCG — the 12-month line",
             "body": ("The Indian government taxes your stock market profits based on how long you hold the stock.\n\n"
                      "• **STCG (Short-Term Capital Gains):** If you hold a stock for less than 12 months, it is taxed at 20%.\n"
                      "• **LTCG (Long-Term Capital Gains):** If you hold it for more than 12 months, it is taxed at 12.5%, but you only pay tax on profits above ₹1.25 Lakh per year.\n\n"
                      "The government is rewarding you for being a long-term investor."),
             "worked_example": ("You buy shares at ₹1,000 and sell at ₹1,300 (a ₹30,000 profit).\n"
                                "• If you sell in 8 months (STCG), you pay 20% tax = ₹6,000.\n"
                                "• If you wait 13 months (LTCG), the first ₹1.25 Lakh of profits are tax-free. You pay ₹0 tax. You saved ₹6,000 just by waiting."),
             "pitfall": ("Selling a stock at 11 months just because you need the money. By holding for 30 more days, your tax rate drops dramatically. Always check your holding period before selling.")},
            {"heading": "Intraday & F&O — different tax world",
             "body": ("If you buy and sell a stock on the same day (Intraday), or trade Futures & Options (F&O), the tax rules change completely.\n\n"
                      "The government does not consider this 'investing'. They consider it a **business**.\n\n"
                      "This means your profits are added to your total income and taxed at your normal income tax slab rate (which can be 30%+ if you earn well). You also have to maintain books of accounts."),
             "worked_example": ("You make ₹5 Lakhs in F&O trading and have a ₹15 Lakh salary. Your total income is ₹20 Lakhs. The ₹5 Lakh is taxed at the highest slab (roughly 30%), meaning you owe ₹1.5 Lakh in tax. If you had held those trades as long-term investments, the tax would be much lower."),
             "pitfall": ("Thinking 'If I don't withdraw the money from my broker, it's not taxed'. Realized gains are taxed at the end of the financial year regardless of whether you withdrew the cash or left it in your trading account.")},
            {"heading": "The paperwork you must know",
             "body": ("The Income Tax Department of India is now highly automated.\n\n"
                      "• **AIS (Annual Information Statement):** A digital record the tax department keeps of all your stock trades, dividends, and mutual fund redemptions.\n"
                      "• **TIS (Taxpayer Information Summary):** A summary of your AIS.\n"
                      "• **STT (Securities Transaction Tax):** An automatic tax deducted by the broker on every trade."),
             "worked_example": ("If you make 200 trades in a year, the AIS automatically pulls this data from the stock exchange. When you file your ITR (Income Tax Return), you must reconcile your personal records with the AIS. If they don't match, the tax department sends you an automated notice."),
             "pitfall": ("Ignoring the AIS. Always download your AIS from the income tax portal before filing your returns to ensure the data matches your trading journal.")},
            {"heading": "What SEBI bans — the red lines",
             "body": ("SEBI is extremely strict about market integrity. If you cross these lines, you can face massive fines and jail time:\n\n"
                      "• **Insider Trading:** Trading on confidential information (like a company's earnings) before it is made public.\n"
                      "• **Market Manipulation:** Pumping up the price of a stock with fake news so you can sell your shares to unsuspecting people.\n"
                      "• **Unregistered Advisory:** Giving paid stock tips without a SEBI license."),
             "worked_example": ("In 2023, SEBI fined a Telegram channel ₹40 crore for running an unregistered advisory. They were pumping up small-cap stocks to their 30,000 subscribers, and then selling their own shares at the high prices (a pump-and-dump scheme)."),
             "pitfall": ("Paying for 'sure shot' stock tips on WhatsApp or Telegram. If the tip is truly guaranteed, the person would be a billionaire, not selling tips for ₹5,000 a month.")},
        ],
        "key_takeaways": [
            "STCG is 20%, LTCG is 12.5% above ₹1.25L.",
            "Intraday & F&O are treated as business income at your slab rate.",
            "The AIS/TIS auto-reports your trades to the tax department.",
            "Insider trading is a criminal offense with up to 10 years of imprisonment.",
        ],
        "quiz": [
            {"q": "Bought 1 Jan 2024, sold 1 Mar 2024. Tax type?",
             "options": ["LTCG", "STCG", "No tax"], "correct": 1,
             "explain_correct": ("Held ~2 months < 12 → STCG @ 20%. No 'no tax' threshold for STCG."),
             "explain_wrong": ("LTCG requires ≥12 months. STCG taxable from rupee 1."),
             "mental_model": "Under 12 months = STCG."},
            {"q": "LTCG on equity above ₹1.25 lakh is taxed at…",
             "options": ["10%", "12.5%", "20%"], "correct": 1,
             "explain_correct": ("12.5% as per FY 2024-25 (was 10%). Exemption resets annually."),
             "explain_wrong": ("10% = old rate. 20% = STCG rate."),
             "mental_model": "LTCG equity = 12.5% above ₹1.25L."},
            {"q": "Which is illegal per SEBI?",
             "options": ["Long-term investing", "Insider trading", "Index funds"],
             "correct": 1,
             "explain_correct": ("Insider trading = criminal offense. Fines up to ₹25 cr or 3× profit + imprisonment up to 10 years."),
             "explain_wrong": ("Long-term investing and index funds are encouraged by SEBI."),
             "mental_model": "Insider info + trade = jail."},
        ],
    },
    {
        "id": "ch8", "title": "Options & F&O Basics", "icon": "🎰",
        "reward": 30000, "practice": "options_payoff",
        "hook": "Options are not 'cheap stocks'. They are decaying bets on "
                "time, direction, and volatility.",
        "deep_lesson": [
            {"heading": "Options = rights, not obligations",
             "body": ("Options are one of the most misunderstood instruments in the market. They are not cheap stocks. They are contracts.\n\n"
                      "• **Call Option (CE):** The right to BUY a stock at a fixed price.\n"
                      "• **Put Option (PE):** The right to SELL a stock at a fixed price.\n\n"
                      "When you buy an option, you pay a fee (the **Premium**). You have the right to exercise the contract, but not the obligation. If the trade goes wrong, your maximum loss is just the premium you paid. If it goes right, the profits can be massive."),
             "worked_example": ("NIFTY is at 22,000. You buy a 22,000 Call Option for ₹100 (Lot size is 25, so you pay ₹2,500).\n"
                                "• If NIFTY shoots up to 22,300, the Call is worth ₹300. You make ₹7,500 (₹300 - ₹100 = ₹200 profit × 25).\n"
                                "• If NIFTY drops to 21,700, the Call expires worthless. You lose only the ₹2,500 you paid."),
             "pitfall": ("Thinking options are a 'get rich quick' scheme. Options are decaying assets. Every single day that passes, the premium loses value, even if the market stays flat. Flat market = you lose money.")},
            {"heading": "Greeks — the language of options",
             "body": ("To trade options, you must understand the Greeks. They measure how the option's price will change:\n\n"
                      "• **Delta:** How much the price changes if the market moves ₹1.\n"
                      "• **Theta:** Time decay. The amount of money the option loses every single day just from the passage of time.\n"
                      "• **Vega:** Volatility. How much the price changes based on fear/greed in the market.\n"
                      "• **Gamma:** The rate at which Delta changes."),
             "worked_example": ("You hold an option with a Delta of 0.5 and a Theta of -15. If the NIFTY goes up ₹100, you make ₹50 (because of Delta). If the NIFTY stays completely flat, you still lose ₹15 that day (because of Theta). Five flat days in a row = ₹75 loss per unit."),
             "pitfall": ("Buying options right before a major event (like an election or earnings). The market prices in massive volatility (high Vega), making the premium very expensive. Once the event passes, volatility crushes, and the premium drops instantly, even if the direction was correct.")},
            {"heading": "Indian F&O market reality",
             "body": ("The Futures and Options (F&O) segment is insanely popular in India, but the reality is brutal.\n\n"
                      "NIFTY options expire every Thursday. The last 2 days before expiry experience absolute brutal time decay (Theta). In a SEBI study from 2023, it was revealed that **89% of retail F&O traders lost money**. The average loss was ₹1.1 Lakh per trader."),
             "worked_example": ("You trade 10 options a week. Each trade costs ₹25,000 in premium. You win 4 and lose 6. Your winners bring in ₹20,000, but your losers wipe out ₹30,000. You are down ₹10,000 in one week. Add brokerage and STT, and the loss is even bigger."),
             "pitfall": ("Trading F&O with real money just because you watched a YouTube video. The lot sizes are massive (NIFTY = 25, Bank NIFTY = 15). One mistake can wipe out your entire trading capital. Always paper trade first.")},
            {"heading": "When options make sense",
             "body": ("If 89% of people lose money, why trade options at all?\n\n"
                      "Options are incredible tools for **Hedging** (protecting your portfolio).\n\n"
                      "If you have a ₹5 Lakh portfolio of NIFTY stocks and you are worried about a market crash, you can buy a Put Option. If the market crashes, your stocks lose value, but your Put option makes money, offsetting the loss. You can also use Covered Calls to generate extra income on stocks you already own."),
             "worked_example": ("You hold ₹5 Lakhs of NIFTY stocks. You buy a protective Put for ₹2,500. The market suddenly drops 5%. Your stocks lose ₹25,000. But your Put option gains ₹20,000. Your net loss is only ₹7,500 instead of ₹25,000."),
             "pitfall": ("Naked writing (selling options without holding the underlying asset). It feels like easy income—you collect premium every week. But one massive market crash can result in unlimited losses that wipe out months of gains in a single day.")},
        ],
        "key_takeaways": [
            "Options are rights, not obligations. Buyers risk only the premium.",
            "Theta (time decay) kills option buyers daily. A flat market = a loss.",
            "IV crush after events destroys premiums, even if your direction is right.",
            "89% of Indian retail F&O traders lose money. Paper trade before risking real cash.",
        ],
        "quiz": [
            {"q": "You expect NIFTY to rise. What do you buy?",
             "options": ["Put (PE)", "Call (CE)", "Both"], "correct": 1,
             "explain_correct": ("Call = right to buy. Bullish bet with defined risk."),
             "explain_wrong": ("Put = bearish. Both = straddle, loses to theta in flat markets."),
             "mental_model": "Bullish → Call. Bearish → Put."},
            {"q": "NIFTY 22,000 CE premium = ₹100. NIFTY ends 21,800. Loss?",
             "options": ["₹100 (premium)", "₹200", "Nothing"], "correct": 0,
             "explain_correct": ("CE expires worthless (spot < strike). Lose premium = max loss as buyer."),
             "explain_wrong": ("₹200 impossible as buyer. 'Nothing' wrong — you lose premium."),
             "mental_model": "Buyer's max loss = premium."},
            {"q": "What is 'theta' in options?",
             "options": ["Interest rate", "Time decay of premium", "Volatility"],
             "correct": 1,
             "explain_correct": ("Theta = daily time decay. Accelerates near expiry — final week is brutal for buyers."),
             "explain_wrong": ("Interest rate ≈ rho. Volatility ≈ vega."),
             "mental_model": "Theta = time tax on buyers."},
        ],
    },
]
# ============================================================================
# ACHIEVEMENTS
# ============================================================================
ACHIEVEMENTS = {
    "first_step":     {"name": "First Step",         "icon": "👣", "desc": "Complete Chapter 1"},
    "chart_reader":   {"name": "Chart Reader",       "icon": "🕯️", "desc": "Master candlesticks"},
    "trend_spotter":  {"name": "Trend Spotter",      "icon": "🐂", "desc": "Identify bull & bear"},
    "strategist":     {"name": "Strategist",         "icon": "🎯", "desc": "Complete risk module"},
    "disciplined":    {"name": "Disciplined",        "icon": "🧠", "desc": "Complete psychology"},
    "tax_aware":      {"name": "Tax Aware",          "icon": "📜", "desc": "Complete Indian tax"},
    "options_trader": {"name": "Options Trader",     "icon": "🎰", "desc": "Master F&O basics"},
    "graduate":       {"name": "FinSpire Graduate",  "icon": "🎓", "desc": "Finish all 8 chapters"},
    "first_trade":    {"name": "First Trade",        "icon": "🥇", "desc": "First trade executed"},
    "diversified":    {"name": "Diversified",        "icon": "🧩", "desc": "Hold all 4 asset classes"},
    "profitable":     {"name": "In the Green",       "icon": "💰", "desc": "Portfolio above start"},
    "journaler":      {"name": "Journaler",          "icon": "📓", "desc": "Log 5 journal entries"},
    "self_aware":     {"name": "Self Aware",         "icon": "🔍", "desc": "Bias detected in journal"},
    "prop_funded":    {"name": "Prop Funded",        "icon": "🏛️", "desc": "Pass prop firm challenge"},
    "risk_master":    {"name": "Risk Master",        "icon": "🛡️", "desc": "10 trades, <5% max DD"},
    "voice_trader":   {"name": "Voice Trader",       "icon": "🎙️", "desc": "Log a trade by voice"},
    "backtester":     {"name": "Backtester",         "icon": "⏮️", "desc": "Run a backtest"},
    "options_paper":  {"name": "Options Paper Pro",  "icon": "📝", "desc": "Paper trade an option"},
    "sharpe_shark":   {"name": "Sharpe Shark",       "icon": "📊", "desc": "Sharpe ratio > 1"},
}

# ============================================================================
# SEBI-REGISTERED ADVISOR DIRECTORY
# ============================================================================
ADVISORS = [
    {"name": "Zerodha Varsity", "type": "Free Educational",
     "url": "https://zerodha.com/varsity/",
     "note": "Free educational content. Not advice."},
    {"name": "SEBI RIA Search", "type": "Regulator Directory",
     "url": "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRecognisedFpi=yes&intmId=13",
     "note": "Official SEBI list of registered investment advisors."},
    {"name": "AMFI — Mutual Fund Distributors", "type": "Industry Body",
     "url": "https://www.amfiindia.com/",
     "note": "Find ARN-registered mutual fund distributors."},
    {"name": "NSE Investor Education", "type": "Exchange Resource",
     "url": "https://www.nseindia.com/investor-relations",
     "note": "NSE's official investor education portal."},
    {"name": "BSE Investor Services", "type": "Exchange Resource",
     "url": "https://www.bseindia.com/investors/",
     "note": "BSE investor resources and complaint redressal."},
]


# ============================================================================
# INSTRUMENT CATALOG (real NSE tickers per asset class)
# ============================================================================
INSTRUMENTS = {
    "Stocks": {
        "RELIANCE":  {"name": "Reliance Industries",   "base": 2850.0},
        "TCS":       {"name": "Tata Consultancy Svcs", "base": 4100.0},
        "HDFCBANK":  {"name": "HDFC Bank",             "base": 1680.0},
        "INFY":      {"name": "Infosys",               "base": 1850.0},
        "ITC":       {"name": "ITC Ltd",               "base": 445.0},
        "SBIN":      {"name": "State Bank of India",   "base": 820.0},
    },
    "Bonds": {
        "GSEC10Y":    {"name": "10-Yr G-Sec",         "base": 100.0},
        "SGB":        {"name": "Sovereign Gold Bond", "base": 6200.0},
        "LIQUIDBEES": {"name": "Liquid Bees ETF",     "base": 1000.0},
    },
    "Gold": {
        "GOLD24K":  {"name": "Gold 24K (per 10g)", "base": 72000.0},
        "GOLDBEES": {"name": "GoldBees ETF",       "base": 62.0},
    },
    "Crypto": {
        "BTC": {"name": "Bitcoin (INR)",  "base": 5800000.0},
        "ETH": {"name": "Ethereum (INR)", "base": 245000.0},
    },
}

def find_ticker_class(ticker):
    """Return the asset class a ticker belongs to, or None."""
    for cls, tickers in INSTRUMENTS.items():
        if ticker in tickers:
            return cls
    return None


# ============================================================================
# SESSION STATE
# ============================================================================
def init_state():
    defaults = {
        "lang": "en", "onboarded": False,
        "risk_profile": None,

        # Learning
        "completed_chapters": [], "chapter_stage": {},
        "quiz_results": {}, "unlocked_capital": 0.0,
        "srs_schedule": {},

        # Portfolio (legacy class buckets + new instrument system)
        "portfolio": {"Cash": 0.0, "Stocks": 0.0, "Bonds": 0.0,
                      "Gold": 0.0, "Crypto": 0.0},
        "starting_capital": 0.0,
        "prices": {"Stocks": 100.0, "Bonds": 50.0,
                   "Gold": 200.0, "Crypto": 1000.0},
        "price_history": {"Stocks": [], "Bonds": [],
                          "Gold": [], "Crypto": []},
        "round_number": 0, "equity_curve": [], "max_drawdown": 0.0,

        # Instrument-level trading (real NSE tickers)
        "instrument_prices": {},
        "instrument_holdings": {},
        "instrument_history": {},

        # Live data
        "live_prices": {}, "live_updated": None,

        # Journal
        "journal": [], "bias_flags": [],

        # Options paper trading
        "options_book": [], "options_history": [],

        # Backtest
        "bt_data": None, "bt_result": None,

        # Prop firm
        "prop_active": False, "prop_starting": 100000.0,
        "prop_target": 110000.0, "prop_max_dd": 0.05, "prop_failed": False,

        # Leaderboard
        "leaderboard_name": None,
        "leaderboard_opt_in": False,

        # Meta
        "xp": 0, "achievements": [], "page": "Learn",
        "selected_chapter": None, "feedback": None,
        "_restored_this_session": False,        
    }
    
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Populate instrument state (idempotent, safe against stale sessions) ──
if not st.session_state.get("instrument_prices"):
    st.session_state.instrument_prices = {
        tk: meta["base"]
        for cls, tickers in INSTRUMENTS.items()
        for tk, meta in tickers.items()
    }
if not isinstance(st.session_state.get("instrument_holdings"), dict):
    st.session_state.instrument_holdings = {}
if not st.session_state.get("instrument_history"):
    st.session_state.instrument_history = {
        tk: []
        for cls, tickers in INSTRUMENTS.items()
        for tk in tickers
    }

# ============================================================================
# PERSISTENCE — native JSON Export / Import (no localStorage, no loops)
# ============================================================================

PERSIST_KEYS = [
    "xp", "completed_chapters", "chapter_stage", "unlocked_capital",
    "portfolio", "starting_capital", "achievements", "journal",
    "risk_profile", "leaderboard_name", "leaderboard_opt_in",
    "instrument_prices", "instrument_holdings", "instrument_history",
    "srs_schedule", "equity_curve", "max_drawdown", "round_number",
    "options_book", "options_history", "bias_flags", "onboarded",
]

def export_progress_bytes():
    """Pack the current session state into a JSON file."""
    snapshot = {k: st.session_state.get(k) for k in PERSIST_KEYS}
    snapshot["_exported_at"] = datetime.now().isoformat()
    snapshot["_app"] = "FinSpire v4.0"
    return json.dumps(snapshot, indent=2, default=str).encode("utf-8")

def import_progress_from_bytes(raw: bytes) -> bool:
    """Restore session state from an uploaded JSON file."""
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        return False
    if not isinstance(data, dict):
        return False
    for k in PERSIST_KEYS:
        if k in data:
            st.session_state[k] = data[k]
    # Ensure instruments exist after import
    for cls, tickers in INSTRUMENTS.items():
        for tk, meta in tickers.items():
            st.session_state.instrument_prices.setdefault(tk, meta["base"])
            st.session_state.instrument_history.setdefault(tk, [])
    return True

def _handle_upload():
    """Callback to safely process the uploaded JSON."""
    uploaded = st.session_state.get("progress_uploader")
    if uploaded is not None:
        if import_progress_from_bytes(uploaded.read()):
            st.session_state._upload_success = True
        else:
            st.session_state._upload_success = False
# ============================================================================
# HELPERS
# ============================================================================
def get_chapter(cid):
    return next((c for c in CURRICULUM if c["id"] == cid), None)

def chapter_unlocked(i):
    return i == 0 or CURRICULUM[i-1]["id"] in st.session_state.completed_chapters

def chapter_completed(cid):
    return cid in st.session_state.completed_chapters

def active_chapter_index():
    for i, c in enumerate(CURRICULUM):
        if c["id"] not in st.session_state.completed_chapters:
            return i
    return len(CURRICULUM) - 1

def award_xp(n, reason=""):
    st.session_state.xp += n
    if reason: st.toast(f"+{n} XP — {reason}", icon="✨")

def unlock_ach(key):
    if key not in st.session_state.achievements:
        st.session_state.achievements.append(key)
        st.toast(f"🏆 {ACHIEVEMENTS[key]['name']} unlocked!", icon="🏆")
        award_xp(25, "Achievement")

def portfolio_value():
    """Total portfolio = cash + legacy class buckets + instrument holdings."""
    p = st.session_state.portfolio
    class_value = (
        p["Stocks"] * st.session_state.prices["Stocks"]
        + p["Bonds"] * st.session_state.prices["Bonds"]
        + p["Gold"] * st.session_state.prices["Gold"]
        + p["Crypto"] * st.session_state.prices["Crypto"]
    )
    inst_value = 0.0
    if "instrument_holdings" in st.session_state:
        for tk, h in st.session_state.instrument_holdings.items():
            price = st.session_state.instrument_prices.get(tk, 0)
            inst_value += h["units"] * price
    return p["Cash"] + class_value + inst_value

def instrument_pnl(ticker):
    """Return (units, avg_cost, current_price, unrealized_pnl, pnl_pct)."""
    holding = st.session_state.instrument_holdings.get(ticker)
    cur = st.session_state.instrument_prices.get(ticker, 0)
    if not holding or holding["units"] <= 0:
        return 0, 0, cur, 0, 0
    units = holding["units"]
    avg = holding["avg_cost"]
    pnl = (cur - avg) * units
    pct = ((cur / avg) - 1) * 100 if avg > 0 else 0
    return units, avg, cur, pnl, pct

def total_unrealized_pnl():
    total = 0
    for tk in st.session_state.instrument_holdings:
        _, _, _, pnl, _ = instrument_pnl(tk)
        total += pnl
    return total

def total_realized_pnl():
    return sum(e.get("realized_pnl", 0) for e in st.session_state.journal)

def grant_capital(a):
    st.session_state.portfolio["Cash"] += a
    st.session_state.unlocked_capital += a
    st.session_state.starting_capital += a

def inr(x):
    return f"₹{x:,.2f}"


# ============================================================================
# LIVE MARKET DATA
# ============================================================================
LIVE_TICKERS = {
    "NIFTY 50": "^NSEI", "SENSEX": "^BSESN",
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
}

@st.cache_data(ttl=300, show_spinner=False)
def fetch_live_prices():
    if not HAS_YF: return None
    try:
        syms = list(LIVE_TICKERS.values())
        data = yf.download(syms, period="2d", interval="1d",
                           progress=False, auto_adjust=True)
        out = {}
        for name, sym in LIVE_TICKERS.items():
            try:
                closes = data["Close"][sym].dropna()
                if len(closes):
                    out[name] = {
                        "price": float(closes.iloc[-1]),
                        "prev": float(closes.iloc[-2]) if len(closes) > 1
                                else float(closes.iloc[-1])
                    }
            except Exception: continue
        return out or None
    except Exception:
        return None

def render_live_ticker():
    if not HAS_YF:
        st.caption("ℹ️ Install `yfinance` for live NSE data.")
        return
    with st.spinner("Fetching live NSE…"):
        live = fetch_live_prices()
    if not live:
        st.caption("📡 Live unavailable — using simulated prices."); return
    st.session_state.live_prices = live
    st.session_state.live_updated = datetime.now().strftime("%H:%M:%S IST")
    cols = st.columns(len(live))
    for i, (name, d) in enumerate(live.items()):
        delta = d["price"] - d["prev"]
        pct = (delta / d["prev"] * 100) if d["prev"] else 0
        cols[i].metric(name, f"{d['price']:,.2f}", f"{pct:+.2f}%")
    st.caption(f"🟢 Live • Updated {st.session_state.live_updated}")


# ============================================================================
# BIAS DETECTION (JOURNAL)
# ============================================================================
BIAS_KEYWORDS = {
    "FOMO": ["everyone", "hyped", "trending", "twitter", "telegram",
             "tip", "sure shot", "guaranteed"],
    "Revenge trading": ["make it back", "recover", "revenge",
                        "double down", "win back", "lost yesterday"],
    "Anchoring": ["was higher", "used to be", "last year",
                  "all-time high", "peak"],
    "Overconfidence": ["can't lose", "obvious", "easy money", "no brainer"],
    "Confirmation bias": ["only good news", "already decided", "justifies"],
}

def detect_bias(text):
    if not text: return []
    tl = text.lower()
    return [b for b, kws in BIAS_KEYWORDS.items() if any(k in tl for k in kws)]


# ============================================================================
# BLACK-SCHOLES (for options paper-trading)
# ============================================================================
def _norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def bs_price(S, K, T, r, sigma, kind="call"):
    if T <= 0:
        intrinsic = max(0, S-K) if kind == "call" else max(0, K-S)
        return intrinsic, {"delta": 0, "gamma": 0, "theta": 0, "vega": 0}
    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    if kind == "call":
        price = S*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)
        delta = _norm_cdf(d1)
        theta = (-S*_norm_cdf(d1)*sigma/(2*math.sqrt(T))
                 - r*K*math.exp(-r*T)*_norm_cdf(d2)) / 365
    else:
        price = K*math.exp(-r*T)*_norm_cdf(-d2) - S*_norm_cdf(-d1)
        delta = _norm_cdf(d1) - 1
        theta = (-S*_norm_cdf(d1)*sigma/(2*math.sqrt(T))
                 + r*K*math.exp(-r*T)*_norm_cdf(-d2)) / 365
    gamma = _norm_cdf(d1) / (S*sigma*math.sqrt(T)) if S > 0 else 0
    vega = S*_norm_cdf(d1)*math.sqrt(T) / 100
    return max(0.05, price), {"delta": delta, "gamma": gamma,
                              "theta": theta, "vega": vega}


# ============================================================================
# BACKTEST ENGINE
# ============================================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_historical(ticker="^NSEI", start="2019-01-01", end="2024-12-31"):
    if not HAS_YF:
        dates = pd.date_range(start, end, freq="B")
        np.random.seed(42)
        rets = np.random.normal(0.0004, 0.011, len(dates))
        prices = 11000 * np.cumprod(1 + rets)
        return pd.DataFrame({"Date": dates, "Close": prices}).set_index("Date")
    try:
        df = yf.download(ticker, start=start, end=end,
                         progress=False, auto_adjust=True)
        if df.empty: return None
        df = df[["Close"]].dropna()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception:
        return None

def run_ma_crossover(df, fast=20, slow=50, initial=100000):
    df = df.copy()
    df["Fast"] = df["Close"].rolling(fast).mean()
    df["Slow"] = df["Close"].rolling(slow).mean()
    df["Signal"] = np.where(df["Fast"] > df["Slow"], 1, 0)
    df["Ret"] = df["Close"].pct_change().fillna(0)
    df["Strat"] = df["Signal"].shift(1).fillna(0) * df["Ret"]
    df["Equity"] = initial * (1 + df["Strat"]).cumprod()
    df["BH"] = initial * (1 + df["Ret"]).cumprod()

    total_ret = (df["Equity"].iloc[-1] / initial - 1) * 100
    bh_ret = (df["BH"].iloc[-1] / initial - 1) * 100
    daily = df["Strat"]
    sharpe = (daily.mean() / daily.std() * math.sqrt(252)) if daily.std() else 0
    downside = daily[daily < 0].std()
    sortino = (daily.mean() / downside * math.sqrt(252)) if downside else 0
    peak = df["Equity"].cummax()
    dd = (df["Equity"] - peak) / peak
    max_dd = dd.min() * 100
    win_rate = (daily[daily != 0] > 0).mean() * 100 if (daily != 0).any() else 0

    trades = int(df["Signal"].diff().abs().sum())
    return {
        "df": df, "total_ret": total_ret, "bh_ret": bh_ret,
        "sharpe": sharpe, "sortino": sortino, "max_dd": max_dd,
        "win_rate": win_rate, "trades": trades,
    }


# ============================================================================
# SIDEBAR
# ============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("## 💎 FinSpire")
        st.caption(t("app_tagline"))

        lc = st.radio("🌐 Language", ["English", "हिन्दी"],
                      index=0 if st.session_state.lang == "en" else 1,
                      horizontal=True, label_visibility="collapsed")
        nl = "en" if lc == "English" else "hi"
        if nl != st.session_state.lang:
            st.session_state.lang = nl; st.rerun()

        st.markdown("---")
        done = len(st.session_state.completed_chapters)
        total = len(CURRICULUM)
        st.markdown(f"**{t('curriculum')}** — {done}/{total}")
        st.progress(done/total)

        st.markdown("---")
        st.markdown(f"#### 🏦 {t('capital')}")
        cap = st.session_state.unlocked_capital
        if cap == 0:
            st.warning(t("no_capital"))
        else:
            st.markdown(f"<div class='rupee-badge'>"
                        f"Earned: {inr(cap)}</div>",
                        unsafe_allow_html=True)
            st.caption(f"Portfolio: {inr(portfolio_value())}")

        if st.session_state.prop_active and not st.session_state.prop_failed:
            st.markdown("<div class='prop-badge'>🏛️ PROP ACTIVE</div>",
                        unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"#### 🧭 {t('nav')}")
        nav = [
            ("Learn",            t("learn")),
            ("Trade Simulator",  t("trade")),
            ("Options",          t("options")),
            ("Journal",          t("journal")),
            ("Backtest",         t("backtest")),
            ("Prop Firm",        t("prop")),
            ("Leaderboard",      t("leaderboard")),
            ("Achievements",     t("achieve")),
            ("Advisors",         t("advisors")),
            ("Dashboard",        t("dash")),
        ]
        for key, label in nav:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.session_state.page = key
                st.session_state.selected_chapter = None
                st.rerun()

                st.markdown("---")
        st.markdown("#### 💾 Save / Load")
        
        st.download_button(
            "⬇️ Download Progress (.json)",
            data=export_progress_bytes(),
            file_name="finspire_progress.json",
            mime="application/json",
            use_container_width=True,
            help="Save to your device so you can restore after refreshing.",
            key="sidebar_download"
        )
        
        st.file_uploader(
            "⬆️ Restore Progress (.json)",
            type=["json"],
            label_visibility="collapsed",
            key="progress_uploader",
            on_change=_handle_upload
        )
        
        # ── The Fix: A manual confirmation button ──
        if st.session_state.get("_upload_success") is True:
            st.info("File loaded into memory. Click below to apply.")
            if st.button("✅ Apply Restored Progress", type="primary", use_container_width=True):
                st.session_state._upload_success = None
                st.rerun()
                
        elif st.session_state.get("_upload_success") is False:
            st.error("❌ Invalid file format.")
            st.session_state._upload_success = None

# ============================================================================
# ONBOARDING
# ============================================================================
def render_onboarding():
    if st.session_state.onboarded: return
    st.markdown("<h1 class='hero-title'>Welcome to FinSpire</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>A financial literacy simulator for India.</p>",
                unsafe_allow_html=True)

    st.markdown("""<div class='card'>
    <b style='color:#22d3ee;'>How FinSpire works</b>
    <ul style='color:#cbd5e1; line-height:1.7;'>
    <li>📖 <b>Learn</b> — 8 chapters, from stocks to options</li>
    <li>🧪 <b>Practice</b> — interactive tools, not passive quizzes</li>
    <li>💰 <b>Earn capital</b> — no free money; you trade what you unlock</li>
    <li>📓 <b>Journal</b> — voice or text, with bias alerts</li>
    <li>🎰 <b>Options</b> — paper trade NIFTY weekly with Greeks</li>
    <li>⏮️ <b>Backtest</b> — replay NIFTY history, test strategies</li>
    <li>🏛️ <b>Prop Firm</b> — after ₹95k, funded challenge</li>
    </ul></div>""", unsafe_allow_html=True)

    st.markdown("### 🎯 Risk Profile")
    profile = st.radio(
        "How would you describe yourself?",
        ["Conservative — protect capital first",
         "Balanced — steady growth with moderate risk",
         "Aggressive — higher risk for higher returns"],
        index=None
    )

    st.markdown("""<div class='danger'>
    ⚖️ <b>SEBI Disclaimer:</b> FinSpire is an <b>educational simulation</b>.
    Not SEBI-registered. Not investment advice. Simulated profits ≠ real outcomes.
    Markets carry risk of capital loss. Consult a SEBI-registered advisor before
    investing. By continuing you acknowledge these terms.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    if c1.button("I understand — start", use_container_width=True,
                 disabled=profile is None):
        st.session_state.risk_profile = profile.split(" — ")[0]
        st.session_state.onboarded = True
        st.rerun()
    if c2.button("Explore first (no risk profile)", use_container_width=True):
        st.session_state.risk_profile = "Balanced"
        st.session_state.onboarded = True
        st.rerun()


# ============================================================================
# PAGE: LEARN
# ============================================================================
def page_learn():
    st.markdown(f"<h1 class='hero-title'>{t('learn')}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<p class='hero-sub'>Each chapter rewards you with capital. "
                f"No free money — you earn it.</p>", unsafe_allow_html=True)

    if st.session_state.selected_chapter:
        render_chapter_detail(st.session_state.selected_chapter)
        return

    for i, ch in enumerate(CURRICULUM):
        unlocked = chapter_unlocked(i)
        completed = chapter_completed(ch["id"])
        active = (not completed) and unlocked and i == active_chapter_index()

        if completed:
            st.markdown(f"""<div class='unlocked-card'>
                <span style='font-size:1.7rem;'>{ch['icon']}</span>
                <b style='color:#10b981; font-size:1.05rem; margin-left:0.4rem;'>
                {ch['title']}</b>
                <span style='float:right; color:#10b981; font-weight:700;'>
                ✅ DONE</span>
                <div style='color:#94a3b8; margin-top:0.3rem; font-size:0.85rem;'>
                Earned: {inr(ch['reward'])}</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Revisit", key=f"rev_{ch['id']}",
                         use_container_width=True):
                st.session_state.selected_chapter = ch["id"]; st.rerun()
        elif active:
            st.markdown(f"""<div class='current-card'>
                <span style='font-size:1.7rem;'>{ch['icon']}</span>
                <b style='color:#f59e0b; font-size:1.05rem; margin-left:0.4rem;'>
                {ch['title']}</b>
                <span style='float:right; color:#f59e0b; font-weight:700;'>
                ▶ START</span>
                <div style='color:#cbd5e1; margin-top:0.3rem; font-size:0.85rem;'>
                Unlock {inr(ch['reward'])} by passing</div>
            </div>""", unsafe_allow_html=True)
            if st.button("Begin Chapter", key=f"start_{ch['id']}",
                         use_container_width=True):
                st.session_state.selected_chapter = ch["id"]
                if ch["id"] not in st.session_state.chapter_stage:
                    st.session_state.chapter_stage[ch["id"]] = "learn"
                st.rerun()
        else:
            st.markdown(f"""<div class='locked-card'>
                <span style='font-size:1.7rem;'>🔒</span>
                <b style='color:#64748b; font-size:1.05rem; margin-left:0.4rem;'>
                {ch['title']}</b>
                <div style='color:#64748b; margin-top:0.3rem; font-size:0.85rem;'>
                Locked — complete previous chapter</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("")

    due = [cid for cid, when in st.session_state.srs_schedule.items()
           if when <= date.today().isoformat()]
    if due:
        st.markdown(f"<div class='insight'>🧠 <b>Spaced repetition:</b> "
                    f"{len(due)} chapter(s) due for review.</div>",
                    unsafe_allow_html=True)


# ============================================================================
# CHAPTER DETAIL (deep-lesson rendering)
# ============================================================================
def render_chapter_detail(cid):
    ch = get_chapter(cid)
    if not ch:
        st.error("Chapter not found."); return

    if st.button("← Back"):
        st.session_state.selected_chapter = None; st.rerun()

    completed = chapter_completed(cid)
    stage = "done" if completed else st.session_state.chapter_stage.get(cid, "learn")

    st.markdown(f"<h1 class='hero-title'>{ch['icon']} {ch['title']}</h1>",
                unsafe_allow_html=True)

    stages = ["learn", "practice", "quiz", "done"]
    labels = ["📖 Learn", "🧪 Practice", "🎯 Quiz", "💰 Reward"]
    chips = ""
    for s, lab in zip(stages, labels):
        if stage == "done" or stages.index(stage) > stages.index(s):
            chips += f"<span class='stage-chip stage-done'>{lab} ✓</span>"
        elif stage == s:
            chips += f"<span class='stage-chip stage-active'>{lab} ●</span>"
        else:
            chips += f"<span class='stage-chip stage-locked'>{lab}</span>"
    st.markdown(chips, unsafe_allow_html=True)
    st.markdown("")

    if stage == "learn":
        if ch.get("hook"):
            st.markdown(f"<div class='hook-box'>{ch['hook']}</div>",
                        unsafe_allow_html=True)
        for i, sec in enumerate(ch.get("deep_lesson", [])):
            st.markdown(f"<div class='section-heading'>"
                        f"{i+1}. {sec['heading']}</div>",
                        unsafe_allow_html=True)
            st.markdown(sec["body"])
            if sec.get("worked_example"):
                st.markdown(
                    f"<div class='worked-example'>"
                    f"<b style='color:#10b981;'>📊 Worked example</b>"
                    f"<pre>{sec['worked_example']}</pre></div>",
                    unsafe_allow_html=True)
            if sec.get("pitfall"):
                st.markdown(
                    f"<div class='pitfall-box'>"
                    f"<b>⚠️ Common pitfall:</b> {sec['pitfall']}</div>",
                    unsafe_allow_html=True)
            st.markdown("")
        if ch.get("key_takeaways"):
            takeaways_html = "".join(f"<li>{k}</li>" for k in ch["key_takeaways"])
            st.markdown(
                f"<div class='takeaways-box'>"
                f"<b style='color:#10b981;'>🔑 Key takeaways</b>"
                f"<ul style='margin-top:0.5rem;'>{takeaways_html}</ul></div>",
                unsafe_allow_html=True)
        if st.button(t("read"), use_container_width=True):
            st.session_state.chapter_stage[cid] = "practice"
            award_xp(15, "Lesson read"); st.rerun()

    elif stage == "practice":
        run_practice(ch["practice"])
        if st.button(t("practice_ready"), use_container_width=True):
            st.session_state.chapter_stage[cid] = "quiz"; st.rerun()

    elif stage == "quiz":
        st.caption("2 of 3 correct to pass.")
        with st.form(f"quiz_{cid}"):
            answers = []
            for i, q in enumerate(ch["quiz"]):
                st.markdown(f"**Q{i+1}. {q['q']}**")
                a = st.radio(f"q{i}", q["options"], key=f"qa_{cid}_{i}",
                             index=None, label_visibility="collapsed")
                answers.append(a)
            submit = st.form_submit_button(t("submit_quiz"),
                                           use_container_width=True)

        if submit:
            if any(a is None for a in answers):
                st.error("Answer all questions.")
            else:
                correct = sum(1 for a, q in zip(answers, ch["quiz"])
                              if q["options"].index(a) == q["correct"])
                if correct >= 2:
                    st.session_state.chapter_stage[cid] = "done"
                    if cid not in st.session_state.completed_chapters:
                        st.session_state.completed_chapters.append(cid)
                    grant_capital(ch["reward"])
                    award_xp(50, "Chapter passed")
                    st.session_state.srs_schedule[cid] = \
                        (date.today() + timedelta(days=3)).isoformat()
                    ach_map = {"ch1": "first_step", "ch3": "chart_reader",
                               "ch4": "trend_spotter", "ch5": "strategist",
                               "ch6": "disciplined", "ch7": "tax_aware",
                               "ch8": "options_trader"}
                    if cid in ach_map: unlock_ach(ach_map[cid])
                    if len(st.session_state.completed_chapters) == len(CURRICULUM):
                        unlock_ach("graduate")
                    st.balloons()
                    st.success(f"🎉 {correct}/3! "
                               f"{inr(ch['reward'])} {t('pass_reward')}")
                    st.rerun()
                else:
                    st.error(f"{correct}/3. {t('pass_fail')}")
                    st.markdown("### 🔍 Let's review what went wrong")
                    for i, (a, q) in enumerate(zip(answers, ch["quiz"])):
                        picked_idx = q["options"].index(a)
                        if picked_idx == q["correct"]:
                            st.markdown(
                                f"<div class='feedback-row feedback-correct'>"
                                f"<b>Q{i+1} ✅ Correct.</b> "
                                f"You picked <b>{q['options'][picked_idx]}</b>. "
                                f"{q.get('explain_correct','')}</div>",
                                unsafe_allow_html=True)
                        else:
                            st.markdown(
                                f"<div class='feedback-row feedback-wrong'>"
                                f"<b>Q{i+1} ❌ You picked "
                                f"'{q['options'][picked_idx]}'.</b><br>"
                                f"{q.get('explain_wrong','')}<br><br>"
                                f"<b>✅ Correct answer:</b> "
                                f"{q['options'][q['correct']]} — "
                                f"{q.get('explain_correct','')}</div>",
                                unsafe_allow_html=True)
                        if q.get("mental_model"):
                            st.markdown(
                                f"<div class='insight'>🧠 "
                                f"<b>Remember:</b> {q['mental_model']}</div>",
                                unsafe_allow_html=True)
                        st.markdown("")

    else:
        st.success(f"✅ Complete! Earned {inr(ch['reward'])}.")
        st.markdown("### 📖 Full Answer Review")
        for i, q in enumerate(ch["quiz"]):
            st.markdown(f"**Q{i+1}.** {q['q']}")
            st.markdown(f"✅ **Correct:** {q['options'][q['correct']]}")
            st.markdown(f"*{q.get('explain_correct', q.get('explain',''))}*")
            if q.get("mental_model"):
                st.markdown(
                    f"<div class='insight'>🧠 <b>Remember:</b> "
                    f"{q['mental_model']}</div>",
                    unsafe_allow_html=True)
            st.markdown("")
        if st.button(t("next_chapter"), use_container_width=True):
            st.session_state.selected_chapter = None; st.rerun()


# ============================================================================
# PRACTICE MODULES
# ============================================================================
def run_practice(kind):
    if kind == "calculator":
        amt = st.slider("Amount (₹)", 1000, 100000, 10000, 1000)
        yrs = st.slider("Years", 1, 30, 10)
        rate = st.slider("Return %", 1, 20, 12)
        simple = amt * (1 + rate/100 * yrs)
        compound = amt * (1 + rate/100) ** yrs
        c1, c2 = st.columns(2)
        c1.metric("Simple", inr(simple))
        c2.metric("Compounded", inr(compound), f"+{inr(compound-simple)}")
        st.markdown("<div class='insight'>💡 Compounding rewards time.</div>",
                    unsafe_allow_html=True)

    elif kind == "orderbook":
        book = pd.DataFrame({
            "Side": ["Bid 3","Bid 2","Bid 1","Ask 1","Ask 2","Ask 3"],
            "Price": [98.5, 99.0, 99.5, 100.0, 100.5, 101.0],
            "Qty":   [500, 800, 1200, 900, 700, 400]})
        st.dataframe(book, hide_index=True, use_container_width=True)
        st.markdown("<div class='insight'>Best bid 99.5, ask 100 → spread ₹0.5</div>",
                    unsafe_allow_html=True)

    elif kind == "candle_builder":
        o = st.slider("Open ₹", 90, 110, 100)
        h = st.slider("High ₹", 90, 120, 108)
        l = st.slider("Low ₹", 80, 110, 95)
        c = st.slider("Close ₹", 90, 120, 105)
        color = "#10b981" if c >= o else "#ef4444"
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[0,0], y=[l,h], mode="lines",
                                 line=dict(color="#94a3b8", width=2)))
        fig.add_trace(go.Bar(x=[0], y=[abs(c-o)], base=[min(o,c)],
                             width=0.3, marker_color=color))
        fig.update_layout(template="plotly_dark", height=340,
                          paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showticklabels=False,
                                     range=[-0.5, 0.5]),
                          yaxis_title="₹", showlegend=False,
                          margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"**{'🟢 Bullish' if c>=o else '🔴 Bearish'} candle**")

    elif kind == "trend_spotter":
        if "trend_seq" not in st.session_state:
            base, seq = 100, []
            for _ in range(12):
                base += random.choice([-2,-1,0.5,1,2,3])
                seq.append(round(base,2))
            st.session_state.trend_seq = seq
        seq = st.session_state.trend_seq
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=seq, mode="lines+markers",
                                 line=dict(color="#22d3ee", width=3)))
        fig.update_layout(template="plotly_dark", height=280,
                          paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)
        guess = st.radio("Read:", ["Bullish","Bearish","Sideways"],
                         index=None, horizontal=True)
        if guess and st.button("Check"):
            slope = np.polyfit(np.arange(len(seq)), seq, 1)[0]
            actual = ("Bullish" if slope > 0.3
                      else "Bearish" if slope < -0.3 else "Sideways")
            (st.success if guess==actual else st.error)(f"Actual: **{actual}**")
            if guess==actual: award_xp(10, "Correct trend")

    elif kind == "position_sizer":
        cap = st.number_input("Capital ₹", 10000, 1000000, 100000, 10000)
        rp = st.slider("Risk %", 0.5, 5.0, 1.0, 0.5)
        entry = st.number_input("Entry ₹", 1.0, 10000.0, 500.0, 10.0)
        stop = st.number_input("Stop ₹", 0.5, 10000.0, 480.0, 10.0)
        risk_amt = cap * rp / 100
        per = abs(entry - stop)
        if per == 0:
            st.error("Entry ≠ Stop")
        else:
            shares = int(risk_amt / per)
            st.metric("Max loss", inr(risk_amt))
            st.metric("Risk/share", inr(per))
            st.metric("Shares", shares)
            st.metric("Deployed", inr(shares*entry))

    elif kind == "bias_identifier":
        scens = [
            ("You buy because 'everyone on Twitter is bullish'", "FOMO"),
            ("You only read positive news about your holding",
             "Confirmation bias"),
            ("You refuse to sell a loser because 'it was ₹800 last year'",
             "Anchoring"),
            ("After loss, you triple the next position", "Revenge trading"),
        ]
        if "bias_i" not in st.session_state:
            st.session_state.bias_i = 0
        scen, ans = scens[st.session_state.bias_i % len(scens)]
        st.markdown(f"> {scen}")
        opts = ["FOMO","Anchoring","Confirmation bias","Revenge trading"]
        pick = st.radio("Bias:", opts, index=None,
                        key=f"b{st.session_state.bias_i}")
        if pick and st.button("Check"):
            if pick == ans:
                st.success("✅"); award_xp(10, "Bias ID")
            else: st.error(f"❌ It's {ans}")

    elif kind == "tax_calculator":
        buy = st.number_input("Buy ₹", 1.0, 100000.0, 100.0, 10.0)
        sell = st.number_input("Sell ₹", 1.0, 100000.0, 120.0, 10.0)
        qty = st.number_input("Qty", 1, 10000, 100, 10)
        hold = st.selectbox("Holding", ["< 12 mo (STCG)", "≥ 12 mo (LTCG)"])
        gain = (sell - buy) * qty
        if gain <= 0:
            st.info(f"No tax. P/L {inr(gain)}")
        elif "STCG" in hold:
            tax = gain * 0.20
            st.metric("Gain", inr(gain))
            st.metric("Tax @ 20%", inr(tax))
            st.metric("Net", inr(gain - tax))
        else:
            ex = 125000
            tax = max(0, gain - ex) * 0.125
            st.metric("Gain", inr(gain))
            st.metric("Exemption", inr(min(gain, ex)))
            st.metric("Tax @ 12.5%", inr(tax))
            st.metric("Net", inr(gain - tax))

    elif kind == "options_payoff":
        strike = st.number_input("Strike ₹", 100, 30000, 22000, 100)
        premium = st.number_input("Premium ₹", 1, 5000, 100, 10)
        spot = st.slider("Spot at expiry ₹",
                         int(strike*0.9), int(strike*1.1),
                         int(strike), 50)
        intrinsic = max(0, spot - strike)
        pnl = intrinsic - premium
        st.metric("Intrinsic value", inr(intrinsic))
        st.metric("Net P&L per unit", inr(pnl))
        (st.success if pnl > 0 else st.error)(
            f"{'Profit' if pnl > 0 else 'Loss'} {inr(abs(pnl))}")
        spots = np.arange(int(strike*0.9), int(strike*1.1), 50)
        payoffs = [max(0, s - strike) - premium for s in spots]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spots, y=payoffs, mode="lines",
                                 line=dict(color="#22d3ee", width=3),
                                 name="P&L"))
        fig.add_hline(y=0, line=dict(color="#94a3b8", dash="dash"))
        fig.update_layout(template="plotly_dark", height=320,
                          paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_title="Spot", yaxis_title="P&L (₹)",
                          margin=dict(l=20,r=20,t=20,b=20))
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# PAGE: TRADE SIMULATOR
# ============================================================================
def page_trade():
    st.markdown(f"<h1 class='hero-title'>{t('trade')}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='danger'>⚖️ {t('disclaimer_short')}</div>",
                unsafe_allow_html=True)

    if st.session_state.unlocked_capital == 0:
        st.warning(f"🔒 {t('no_capital')}")
        if st.button("Go to Learn"):
            st.session_state.page = "Learn"; st.rerun()
        return

    st.markdown("### 📡 Live Market")
    render_live_ticker()
    st.markdown("---")

    pv = portfolio_value()
    gain = pv - st.session_state.starting_capital
    gpct = (gain/st.session_state.starting_capital*100) \
        if st.session_state.starting_capital else 0
    unrealized = total_unrealized_pnl()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Portfolio", inr(pv), f"{gpct:+.2f}%")
    c2.metric("Cash", inr(st.session_state.portfolio["Cash"]))
    c3.metric("Unrealized P&L", inr(unrealized),
              f"{(unrealized/max(pv,1)*100):+.2f}%")
    c4.metric("Round", st.session_state.round_number)
    c5.metric("Max DD", f"{st.session_state.max_drawdown*100:.2f}%")

    st.markdown("---")
    st.markdown("### 💹 Simulated Instrument Prices (per class)")
    for cls in INSTRUMENTS:
        st.markdown(f"**{cls}**")
        tickers_in_class = list(INSTRUMENTS[cls].keys())
        cols = st.columns(min(len(tickers_in_class), 6))
        for i, tk in enumerate(tickers_in_class):
            cur = st.session_state.instrument_prices.get(tk, 0)
            hist = st.session_state.instrument_history.get(tk, [])
            delta = cur - hist[-2] if len(hist) >= 2 else None
            cols[i % 6].metric(
                tk,
                f"₹{cur:,.0f}" if cur >= 100 else f"₹{cur:,.2f}",
                f"{delta:+.2f}" if delta is not None else None,
            )
    st.markdown("---")

    left, right = st.columns([1, 1.4])

    # ── LEFT: Order form ──────────────────────────────────────────────
    with left:
        st.markdown(f"### 🎯 {t('place_order')}")

        asset_class = st.selectbox(
            "Asset Class", list(INSTRUMENTS.keys()),
            key="trade_asset_class"
        )
        ticker_options = list(INSTRUMENTS[asset_class].keys())
        ticker_labels = {
            tk: f"{tk} — {INSTRUMENTS[asset_class][tk]['name']}"
            for tk in ticker_options
        }
        ticker = st.selectbox(
            "Instrument",
            ticker_options,
            format_func=lambda tk: ticker_labels[tk],
            key="trade_ticker",
        )
        inst_price = st.session_state.instrument_prices.get(
            ticker, INSTRUMENTS[asset_class][ticker]["base"]
        )
        st.caption(
            f"Current price: **{inr(inst_price)}**  •  "
            f"Class: {asset_class}  •  "
            f"{INSTRUMENTS[asset_class][ticker]['name']}"
        )

        with st.form("trade_form"):
            action = st.radio("Action", [t("buy"), t("sell")], horizontal=True)
            amt = st.number_input("Units", 1, 100000, 1, 1)
            reason = st.text_area("Why this trade? (journal)", height=60,
                                  placeholder="e.g., Breakout above resistance")
            st.caption(f"Est. total: **{inr(amt * inst_price)}**")
            submit = st.form_submit_button("Execute", use_container_width=True)

        if submit:
            handle_trade(asset_class, ticker, action, amt, inst_price, reason)

        if st.session_state.feedback:
            k, m = st.session_state.feedback
            (st.success if k == "ok" else st.error)(m)
            st.session_state.feedback = None

        if st.button(t("advance"), use_container_width=True):
            advance_market()
            st.rerun()

    # ── RIGHT: Price chart ────────────────────────────────────────────
    with right:
        st.markdown("### 📊 Price Chart")
        fig = go.Figure()
        colors = ["#22d3ee", "#10b981", "#f59e0b", "#a855f7",
                  "#ec4899", "#ef4444", "#94a3b8"]
        any_data = False
        for idx, (tk, hist) in enumerate(st.session_state.instrument_history.items()):
            if len(hist) >= 1:
                any_data = True
                base = hist[0] if hist[0] > 0 else 1
                norm = [(p/base - 1) * 100 for p in hist]
                fig.add_trace(go.Scatter(
                    x=list(range(1, len(hist)+1)), y=norm,
                    mode="lines+markers", name=tk,
                    line=dict(color=colors[idx % len(colors)], width=2.5),
                ))
        if any_data:
            fig.update_layout(
                template="plotly_dark", height=380,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Round", yaxis_title="% change",
                hovermode="x unified",
                margin=dict(l=20,r=20,t=20,b=40),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Advance a market round to see chart.")

    # ── FULL WIDTH: Positions table ───────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Your Positions — Live P&L")

    holdings = st.session_state.instrument_holdings
    active_holdings = {tk: h for tk, h in holdings.items() if h["units"] > 0}

    if not active_holdings:
        st.info("📭 No open positions yet. Buy an instrument above.")
    else:
        rows = []
        for tk, h in active_holdings.items():
            units, avg, cur, pnl, pct = instrument_pnl(tk)
            cls = find_ticker_class(tk) or "—"
            name = INSTRUMENTS.get(cls, {}).get(tk, {}).get("name", tk)
            rows.append({
                "Ticker": tk,
                "Name":   name,
                "Class":  cls,
                "Units":  units,
                "Avg Cost": avg,
                "Current": cur,
                "Invested": units * avg,
                "Value":    units * cur,
                "P&L (₹)":  pnl,
                "P&L (%)":  pct,
            })

        pos_df = pd.DataFrame(rows)
        total_invested = pos_df["Invested"].sum()
        total_value = pos_df["Value"].sum()
        total_pnl = pos_df["P&L (₹)"].sum()
        total_pct = ((total_value / total_invested) - 1) * 100 \
                    if total_invested > 0 else 0

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Invested", inr(total_invested))
        p2.metric("Current Value", inr(total_value))
        p3.metric("Unrealized P&L", inr(total_pnl), f"{total_pct:+.2f}%")
        p4.metric("Realized P&L (all-time)", inr(total_realized_pnl()))

        def color_pnl(val):
            if isinstance(val, (int, float)):
                if val > 0: return "color: #10b981; font-weight: 700;"
                elif val < 0: return "color: #ef4444; font-weight: 700;"
            return ""

        styled = pos_df.style.format({
            "Units":    "{:,.2f}",
            "Avg Cost": "₹{:,.2f}",
            "Current":  "₹{:,.2f}",
            "Invested": "₹{:,.2f}",
            "Value":    "₹{:,.2f}",
            "P&L (₹)":  "₹{:,.2f}",
            "P&L (%)":  "{:+.2f}%",
        }).map(color_pnl, subset=["P&L (₹)", "P&L (%)"])

        st.dataframe(styled, hide_index=True, use_container_width=True)

        if total_pnl > 0:
            st.markdown(
                f"<div class='insight'>📈 You're up "
                f"<b style='color:#10b981;'>{inr(total_pnl)}</b> "
                f"({total_pct:+.2f}%) on your open positions. "
                f"Realized so far: {inr(total_realized_pnl())}.</div>",
                unsafe_allow_html=True)
        elif total_pnl < 0:
            st.markdown(
                f"<div class='pitfall-box'>📉 You're down "
                f"<b style='color:#ef4444;'>{inr(abs(total_pnl))}</b> "
                f"({total_pct:+.2f}%) on your open positions. "
                f"This is unrealized — no money lost until you sell.</div>",
                unsafe_allow_html=True)
        else:
            st.caption("Portfolio flat — no unrealized P&L yet.")

    # Pie chart
    pie_df = pd.DataFrame([
        {"Asset": tk,
         "Value": h["units"] * st.session_state.instrument_prices.get(tk, 0)}
        for tk, h in active_holdings.items()
    ])
    if len(pie_df) > 0:
        st.markdown("### 🥧 Allocation")
        fig = px.pie(pie_df, values="Value", names="Asset", hole=0.55,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(template="plotly_dark", height=320,
                          paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)


# ============================================================================
# HANDLE TRADE
# ============================================================================
def handle_trade(asset_class, ticker, action, amt, price, reason):
    """Execute buy/sell on a specific instrument, tracking cost basis."""
    buy = action == t("buy") or action == "Buy"

    # Ensure holding record exists
    if ticker not in st.session_state.instrument_holdings:
        st.session_state.instrument_holdings[ticker] = {
            "units": 0.0, "avg_cost": 0.0
        }
    h = st.session_state.instrument_holdings[ticker]

    if buy:
        cost = amt * price
        if cost > st.session_state.portfolio["Cash"]:
            st.session_state.feedback = ("err", "Insufficient cash.")
            return
        # Weighted average cost basis
        old_units = h["units"]
        old_cost = old_units * h["avg_cost"]
        new_units = old_units + amt
        new_avg = (old_cost + cost) / new_units if new_units > 0 else 0
        h["units"] = new_units
        h["avg_cost"] = new_avg
        st.session_state.portfolio["Cash"] -= cost
        st.session_state.portfolio[asset_class] += amt
        realized = 0
    else:
        if amt > h["units"]:
            st.session_state.feedback = ("err", "Not enough units to sell.")
            return
        proceeds = amt * price
        realized = (price - h["avg_cost"]) * amt
        h["units"] -= amt
        if h["units"] <= 0:
            h["units"] = 0
            h["avg_cost"] = 0
        st.session_state.portfolio["Cash"] += proceeds
        st.session_state.portfolio[asset_class] -= amt

    # Journal entry
    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "asset": f"{ticker} ({asset_class})",
        "ticker": ticker,
        "action": "BUY" if buy else "SELL",
        "units": amt, "price": price, "value": amt * price,
        "reason": reason or "(no reason given)",
        "kind": "equity",
        "realized_pnl": realized,
    }
    biases = detect_bias(reason or "")
    entry["biases"] = biases
    st.session_state.journal.append(entry)
    if biases:
        st.session_state.bias_flags.extend(biases)
        unlock_ach("self_aware")
    if len(st.session_state.journal) >= 5:
        unlock_ach("journaler")

    unlock_ach("first_trade")
    held_classes = set()
    for tk, hh in st.session_state.instrument_holdings.items():
        if hh["units"] > 0:
            c = find_ticker_class(tk)
            if c: held_classes.add(c)
    if len(held_classes) == 4:
        unlock_ach("diversified")
    if portfolio_value() > st.session_state.starting_capital:
        unlock_ach("profitable")

    if buy:
        msg = f"✅ Bought {amt} {ticker} @ {inr(price)} — total {inr(amt*price)}"
    else:
        sign = "+" if realized >= 0 else "−"
        msg = (f"✅ Sold {amt} {ticker} @ {inr(price)} — "
               f"realized P&L {sign}{inr(abs(realized))}")
    st.session_state.feedback = ("ok", msg)
    award_xp(5, f"{entry['action']} {amt} {ticker}")


# ============================================================================
# ADVANCE MARKET (single, per-instrument)
# ============================================================================
def advance_market():
    st.session_state.round_number += 1

    vol_map = {"Stocks": 0.04, "Bonds": 0.008,
               "Gold": 0.02, "Crypto": 0.09}
    drift_map = {"Stocks": 0.008, "Bonds": 0.002,
                 "Gold": 0.004, "Crypto": 0.015}

    for asset_class, tickers in INSTRUMENTS.items():
        vol = vol_map.get(asset_class, 0.02)
        drift = drift_map.get(asset_class, 0.005)
        for tk in tickers:
            ch = np.random.normal(drift, vol)
            cur = st.session_state.instrument_prices.get(tk, tickers[tk]["base"])
            nw = max(1.0, cur * (1 + ch))
            st.session_state.instrument_prices[tk] = round(nw, 2)
            st.session_state.instrument_history.setdefault(tk, []).append(nw)
            if len(st.session_state.instrument_history[tk]) > 100:
                st.session_state.instrument_history[tk] = \
                    st.session_state.instrument_history[tk][-100:]

    pv = portfolio_value()
    st.session_state.equity_curve.append(pv)
    start = st.session_state.starting_capital or 1
    dd = (start - pv) / start if pv < start else 0
    if dd > st.session_state.max_drawdown:
        st.session_state.max_drawdown = dd

    if st.session_state.prop_active and not st.session_state.prop_failed:
        if pv < st.session_state.prop_starting * (1 - st.session_state.prop_max_dd):
            st.session_state.prop_failed = True
            st.session_state.prop_active = False
            st.error("❌ Prop challenge FAILED — max drawdown breached.")
        elif pv >= st.session_state.prop_target:
            st.session_state.prop_active = False
            unlock_ach("prop_funded")
            st.balloons()
            st.success("🎉 PROP CHALLENGE PASSED! You're funded.")

    award_xp(3, "Market round")


# ============================================================================
# PAGE: OPTIONS PAPER-TRADING
# ============================================================================
def page_options():
    st.markdown(f"<h1 class='hero-title'>{t('options')}</h1>",
                unsafe_allow_html=True)
    st.markdown(f"<div class='danger'>⚖️ Options are highly leveraged and risky. "
                f"90% of retail F&O traders lose money (SEBI study, 2023). "
                f"This is a paper-trading educational tool only.</div>",
                unsafe_allow_html=True)

    if "ch8" not in st.session_state.completed_chapters:
        st.markdown("""<div class='locked-card'>
            <div style='font-size:3rem;'>🔒</div>
            <b style='color:#f59e0b; font-size:1.1rem;'>
            Complete Chapter 8 (Options & F&O) to unlock</b>
        </div>""", unsafe_allow_html=True)
        return

    spot = 22000
    if st.session_state.live_prices.get("NIFTY 50"):
        spot = st.session_state.live_prices["NIFTY 50"]["price"]

    st.markdown(f"### 📈 NIFTY Spot: **{spot:,.2f}**")

    today = date.today()
    expiries = []
    d = today + timedelta(days=(3 - today.weekday()) % 7)
    for _ in range(4):
        expiries.append(d)
        d += timedelta(days=7)

    c1, c2, c3, c4 = st.columns(4)
    expiry = c1.selectbox("Expiry", [e.strftime("%d-%b-%Y (%a)") for e in expiries])
    exp_date = expiries[[e.strftime("%d-%b-%Y (%a)") for e in expiries].index(expiry)]
    T = max((exp_date - today).days / 365, 1/365)
    option_type = c2.selectbox("Type", ["Call (CE)", "Put (PE)"])
    strike = c3.number_input("Strike", int(spot*0.9), int(spot*1.1),
                             int(round(spot/100)*100), 100)
    iv = c4.slider("Implied Vol %", 10, 60, 18) / 100

    kind = "call" if "Call" in option_type else "put"
    r = 0.065
    price, greeks = bs_price(spot, strike, T, r, iv, kind)

    st.markdown("---")
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Premium", inr(price))
    g2.metric("Delta (Δ)", f"{greeks['delta']:+.3f}")
    g3.metric("Gamma (Γ)", f"{greeks['gamma']:.5f}")
    g4.metric("Theta (Θ)", f"{greeks['theta']:.2f}")
    g5.metric("Vega (V)", f"{greeks['vega']:.2f}")

    st.caption(f"ℹ️ Days to expiry: {(exp_date-today).days}. Lot size NIFTY = 25.")

    st.markdown("---")
    st.markdown("### 🎯 Paper Trade")
    lot_size = 25
    with st.form("opt_form"):
        lots = st.number_input("Lots", 1, 20, 1)
        side = st.radio("Side", ["Buy", "Sell (write)"], horizontal=True)
        action = st.form_submit_button("Open Position", use_container_width=True)

    if action:
        premium_total = price * lot_size * lots
        if side == "Buy":
            if premium_total > st.session_state.portfolio["Cash"]:
                st.error(f"Need {inr(premium_total)} for premium.")
            else:
                st.session_state.portfolio["Cash"] -= premium_total
                st.session_state.options_book.append({
                    "opened": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "expiry": exp_date.isoformat(),
                    "type": option_type, "strike": strike,
                    "premium": price, "lots": lots,
                    "spot_at_open": spot, "side": "BUY", "iv": iv,
                })
                unlock_ach("options_paper")
                award_xp(15, "Options paper trade opened")
                st.success(f"✅ Bought {lots} lot(s) {strike} {option_type} "
                           f"@ {inr(price)} — total {inr(premium_total)}")
                st.rerun()
        else:
            margin = 100000 * lots
            if margin > st.session_state.portfolio["Cash"]:
                st.error(f"Writing requires ~{inr(margin)} margin.")
            else:
                st.session_state.portfolio["Cash"] -= margin
                st.session_state.portfolio["Cash"] += premium_total
                st.session_state.options_book.append({
                    "opened": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "expiry": exp_date.isoformat(),
                    "type": option_type, "strike": strike,
                    "premium": price, "lots": lots,
                    "spot_at_open": spot, "side": "SELL",
                    "iv": iv, "margin": margin,
                })
                award_xp(15, "Options written")
                st.success(f"✅ Sold {lots} lot(s) — collected "
                           f"{inr(premium_total)}, margin blocked {inr(margin)}")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📒 Open Positions")
    if not st.session_state.options_book:
        st.info("No open positions. Open one above.")
    else:
        for i, pos in enumerate(st.session_state.options_book):
            today_d = date.today()
            exp_d = date.fromisoformat(pos["expiry"])
            T_now = max((exp_d - today_d).days / 365, 1/365)
            kind_pos = "call" if "Call" in pos["type"] else "put"
            cur_price, _ = bs_price(spot, pos["strike"], T_now, r,
                                    pos["iv"], kind_pos)
            entry_val = pos["premium"] * lot_size * pos["lots"]
            cur_val = cur_price * lot_size * pos["lots"]
            pnl = ((cur_val - entry_val) if pos["side"] == "BUY"
                   else (entry_val - cur_val))

            with st.expander(
                f"#{i+1} {pos['side']} {pos['strike']} {pos['type']} "
                f"@ {inr(pos['premium'])} — P&L {inr(pnl)}"):
                cc1, cc2, cc3 = st.columns(3)
                cc1.metric("Current premium", inr(cur_price),
                           f"{((cur_price/pos['premium'])-1)*100:+.1f}%")
                cc2.metric("P&L", inr(pnl))
                cc3.metric("Lots", pos["lots"])

                if st.button(f"Close position #{i+1}", key=f"close_opt_{i}"):
                    if pos["side"] == "BUY":
                        st.session_state.portfolio["Cash"] += cur_val
                    else:
                        st.session_state.portfolio["Cash"] += pos.get("margin", 0)
                        st.session_state.portfolio["Cash"] += pnl
                    st.session_state.options_history.append({
                        **pos, "closed": datetime.now().isoformat(),
                        "realized_pnl": pnl,
                    })
                    st.session_state.options_book.pop(i)
                    award_xp(10, "Options closed")
                    st.rerun()

    if st.session_state.options_history:
        st.markdown("---")
        st.markdown("### 📜 History")
        hist_df = pd.DataFrame([{
            "Opened": h["opened"], "Type": h["type"], "Strike": h["strike"],
            "Side": h["side"], "Lots": h["lots"],
            "Realized P&L": h["realized_pnl"],
        } for h in st.session_state.options_history])
        st.dataframe(hist_df.style.format({"Realized P&L": "₹{:,.2f}"}),
                     hide_index=True, use_container_width=True)


# ============================================================================
# PAGE: JOURNAL (voice + text)
# ============================================================================
def page_journal():
    st.markdown(f"<h1 class='hero-title'>{t('journal')}</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Every trade logged. Every bias surfaced.</p>",
                unsafe_allow_html=True)

    st.markdown("### 🎙️ Voice Journal")
    st.caption("Speak your trade reasoning — Chrome/Edge support Hindi & English.")
    voice_html = """
    <div style="background:#1a2332; border:1px solid #2d3a50;
                border-radius:12px; padding:1rem; color:#cbd5e1;">
      <button id="startBtn" style="background:linear-gradient(90deg,#22d3ee,#a855f7);
        color:white; border:none; padding:10px 20px; border-radius:8px;
        font-weight:700; cursor:pointer;">🎙️ Start Recording</button>
      <span id="status" style="margin-left:1rem; font-size:0.9rem;"></span>
      <div id="transcript" style="margin-top:1rem; padding:0.75rem;
        background:#0f1729; border-radius:8px; min-height:60px;
        font-style:italic; color:#94a3b8;"></div>
    </div>
    <script>
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const startBtn = document.getElementById('startBtn');
      const status = document.getElementById('status');
      const transcriptEl = document.getElementById('transcript');
      let finalText = '';
      if (!SR) {
        status.textContent = '⚠️ Speech API not supported in this browser.';
        startBtn.disabled = true;
      } else {
        const rec = new SR();
        rec.continuous = true; rec.interimResults = true; rec.lang = 'en-IN';
        rec.onstart = () => { status.textContent = '🔴 Listening…'; };
        rec.onend = () => { status.textContent = '⏹️ Stopped'; };
        rec.onresult = (e) => {
          let interim = '';
          for (let i = e.resultIndex; i < e.results.length; i++) {
            const tr = e.results[i][0].transcript;
            if (e.results[i].isFinal) finalText += tr + ' ';
            else interim += tr;
          }
          transcriptEl.textContent = finalText + interim;
        };
        startBtn.onclick = () => { finalText = ''; transcriptEl.textContent = ''; rec.start(); };
      }
    </script>
    """
    components.html(voice_html, height=220)

    typed = st.text_area("Or type your journal entry here:",
                         height=80, key="journal_typed")
    if typed and st.button("Add entry"):
        biases = detect_bias(typed)
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "asset": "—", "action": "NOTE", "units": 0,
            "price": 0, "value": 0, "reason": typed,
            "biases": biases, "kind": "note",
        }
        st.session_state.journal.append(entry)
        if biases:
            st.session_state.bias_flags.extend(biases)
            unlock_ach("self_aware")
        unlock_ach("voice_trader")
        award_xp(10, "Journal entry")
        st.success("✅ Entry logged.")
        st.rerun()

    if not st.session_state.journal:
        st.info("📓 No entries yet.")
        return

    st.markdown("---")
    df = pd.DataFrame(st.session_state.journal)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total entries", len(df))
    c2.metric("Trades", sum(1 for e in st.session_state.journal
                            if e.get("kind") != "note"))
    c3.metric("Biases flagged",
              sum(len(e.get("biases", [])) for e in st.session_state.journal))

    all_biases = [b for e in st.session_state.journal for b in e.get("biases", [])]
    if all_biases:
        st.markdown("### ⚠️ Bias Alerts")
        for bias, cnt in Counter(all_biases).most_common():
            advice = {
                "FOMO": "Wait 24h before acting on social signals.",
                "Revenge trading": "Stop for the day after 2 losses.",
                "Anchoring": "Judge by future, not past price.",
                "Overconfidence": "Size down. The market humbles.",
                "Confirmation bias": "Read a bear case before every buy.",
            }.get(bias, "")
            st.markdown(f"<div class='bias-warning'><b>{bias}</b> "
                        f"detected {cnt}× — {advice}</div>",
                        unsafe_allow_html=True)

    st.markdown("### 📜 Entries")
    for e in reversed(st.session_state.journal):
        tag = "⚠️" if e.get("biases") else ""
        with st.expander(f"{e['time']} — {e['action']} "
                         f"{e.get('asset','')} {tag}"):
            st.markdown(f"**Reason:** {e['reason']}")
            if e.get("biases"):
                st.markdown(f"**Biases:** {', '.join(e['biases'])}")
            if e.get("realized_pnl"):
                st.markdown(f"**Realized P&L:** {inr(e['realized_pnl'])}")

    csv = df.to_csv(index=False).encode()
    st.download_button("⬇️ Download journal (CSV)", csv,
                       file_name="finspire_journal.csv", mime="text/csv")


# ============================================================================
# PAGE: BACKTEST SANDBOX
# ============================================================================
def page_backtest():
    st.markdown(f"<h1 class='hero-title'>{t('backtest')}</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Replay NIFTY history. "
                "Test a moving-average crossover strategy.</p>",
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    ticker = c1.selectbox("Index / Stock",
                          ["NIFTY 50 (^NSEI)", "SENSEX (^BSESN)",
                           "RELIANCE", "TCS", "HDFCBANK", "INFY"])
    ticker_map = {
        "NIFTY 50 (^NSEI)": "^NSEI", "SENSEX (^BSESN)": "^BSESN",
        "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS",
        "HDFCBANK": "HDFCBANK.NS", "INFY": "INFY.NS",
    }
    fast = c2.slider("Fast MA", 5, 50, 20)
    slow = c3.slider("Slow MA", 20, 200, 50)
    initial = c4.number_input("Initial ₹", 10000, 10000000, 100000, 10000)

    period = st.select_slider("Period",
                              options=["1y", "3y", "5y", "2019-2024"],
                              value="5y")

    if fast >= slow:
        st.warning("Fast MA must be less than Slow MA.")
        return

    if st.button("▶️ Run Backtest", use_container_width=True):
        with st.spinner("Loading historical data…"):
            if period == "1y":
                start = (date.today() - timedelta(days=365)).isoformat()
                end = date.today().isoformat()
            elif period == "3y":
                start = (date.today() - timedelta(days=365*3)).isoformat()
                end = date.today().isoformat()
            elif period == "5y":
                start = (date.today() - timedelta(days=365*5)).isoformat()
                end = date.today().isoformat()
            else:
                start, end = "2019-01-01", "2024-12-31"

            df = load_historical(ticker_map[ticker], start, end)

        if df is None or df.empty:
            st.error("Could not load data. Try a different period.")
            return

        res = run_ma_crossover(df, fast=fast, slow=slow, initial=initial)

        st.markdown("---")
        st.markdown("### 📊 Results")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Strategy Return", f"{res['total_ret']:+.2f}%")
        m2.metric("Buy & Hold", f"{res['bh_ret']:+.2f}%")
        m3.metric("Sharpe", f"{res['sharpe']:.2f}")
        m4.metric("Max Drawdown", f"{res['max_dd']:.2f}%")
        m5.metric("Trades", res["trades"])

        m6, m7 = st.columns(2)
        m6.metric("Sortino", f"{res['sortino']:.2f}")
        m7.metric("Win Rate", f"{res['win_rate']:.1f}%")

        if res["sharpe"] > 1:
            unlock_ach("sharpe_shark")

        chart_df = res["df"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["Equity"],
                                 mode="lines", name="Strategy",
                                 line=dict(color="#22d3ee", width=2.5)))
        fig.add_trace(go.Scatter(x=chart_df.index, y=chart_df["BH"],
                                 mode="lines", name="Buy & Hold",
                                 line=dict(color="#f59e0b", width=2.5,
                                           dash="dot")))
        fig.update_layout(template="plotly_dark", height=420,
                          paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)",
                          yaxis_title="Portfolio ₹",
                          hovermode="x unified",
                          margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=chart_df.index, y=chart_df["Close"],
                                  mode="lines", name="Price",
                                  line=dict(color="#94a3b8", width=1.5)))
        fig2.add_trace(go.Scatter(x=chart_df.index, y=chart_df["Fast"],
                                  mode="lines", name=f"MA{fast}",
                                  line=dict(color="#22d3ee", width=2)))
        fig2.add_trace(go.Scatter(x=chart_df.index, y=chart_df["Slow"],
                                  mode="lines", name=f"MA{slow}",
                                  line=dict(color="#a855f7", width=2)))
        fig2.update_layout(template="plotly_dark", height=340,
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           hovermode="x unified",
                           margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""<div class='insight'>
        💡 <b>Insight:</b> MA crossover strategies lag in choppy markets and
        whipsaw during sideways phases. Note the trade count — each entry/exit
        incurs friction in real markets (brokerage + STT).
        </div>""", unsafe_allow_html=True)

        unlock_ach("backtester")
        award_xp(20, "Backtest run")


# ============================================================================
# PAGE: PROP FIRM
# ============================================================================
def page_prop():
    st.markdown(f"<h1 class='hero-title'>{t('prop')}</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Pass the challenge. Trade funded capital.</p>",
                unsafe_allow_html=True)

    if st.session_state.unlocked_capital < 95000:
        needed = 95000 - st.session_state.unlocked_capital
        st.markdown(f"""<div class='locked-card'>
            <div style='font-size:3rem;'>🔒</div>
            <b style='color:#f59e0b; font-size:1.1rem;'>
            Complete all 8 chapters to unlock</b>
            <div style='color:#94a3b8; margin-top:0.4rem;'>
            Need {inr(needed)} more earned capital</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown("""<div class='card'>
        <b style='color:#a855f7;'>🏛️ Prop Firm Challenge</b>
        <ul style='color:#cbd5e1; line-height:1.7;'>
        <li>Starting capital: <b>₹1,00,000</b></li>
        <li>Profit target: <b>+10% (₹1,10,000)</b></li>
        <li>Max drawdown: <b>5% (₹95,000 floor)</b></li>
        <li>No time limit</li>
        </ul></div>""", unsafe_allow_html=True)

    if st.session_state.prop_failed:
        st.error("❌ Previous challenge failed. Reset to try again.")
        if st.button("Retry challenge"):
            reset_prop_challenge(); st.rerun()
        return

    if st.session_state.prop_active:
        pv = portfolio_value()
        st.markdown("<div class='prop-badge'>CHALLENGE ACTIVE</div>",
                    unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Current value", inr(pv))
        c2.metric("Target", inr(st.session_state.prop_target),
                  f"{inr(st.session_state.prop_target - pv)} to go")
        floor = st.session_state.prop_starting * (1 - st.session_state.prop_max_dd)
        c3.metric("Drawdown floor", inr(floor))

        progress = ((pv - st.session_state.prop_starting) /
                    (st.session_state.prop_target - st.session_state.prop_starting))
        st.progress(max(0, min(1, progress)),
                    text=f"{progress*100:.1f}% to target")

        if st.button("Trade in funded mode →"):
            st.session_state.page = "Trade Simulator"; st.rerun()
    else:
        if st.button("Start Prop Challenge", use_container_width=True):
            start_prop_challenge(); st.rerun()


def start_prop_challenge():
    st.session_state.portfolio["Cash"] += 100000
    st.session_state.prop_active = True
    st.session_state.prop_failed = False
    st.session_state.prop_starting = portfolio_value()
    st.session_state.prop_target = st.session_state.prop_starting * 1.10
    st.toast("🏛️ Prop challenge started! Target +10%", icon="🎯")


def reset_prop_challenge():
    st.session_state.prop_failed = False
    st.session_state.prop_active = False
    st.session_state.prop_starting = 100000.0
    st.session_state.prop_target = 110000.0


# ============================================================================
# PAGE: LEADERBOARD
# ============================================================================
def page_leaderboard():
    st.markdown(f"<h1 class='hero-title'>{t('leaderboard')}</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Anonymous opt-in weekly P&L.</p>",
                unsafe_allow_html=True)

    st.markdown("""<div class='insight'>
    🔐 <b>Privacy first:</b> Only your chosen display name and return % are shared.
    No emails, no phone numbers, no linked accounts. You can opt out anytime.
    </div>""", unsafe_allow_html=True)

    with st.form("leaderboard_form"):
        name = st.text_input("Display name (anonymous ok)",
                             value=st.session_state.leaderboard_name or "")
        opt = st.checkbox("Opt-in to leaderboard",
                          value=st.session_state.leaderboard_opt_in)
        submitted = st.form_submit_button("Update")

    if submitted:
        st.session_state.leaderboard_name = name.strip() or "Anonymous"
        st.session_state.leaderboard_opt_in = opt
        st.success("Preferences updated.")

    st.markdown("---")
    st.markdown("### 🏆 This Week (simulated peers)")

    pv = portfolio_value()
    start = st.session_state.starting_capital or 1
    my_pct = ((pv - start) / start) * 100

    fake_peers = [
        {"name": "NiftyNinja",     "pct": 12.4},
        {"name": "DalalStBull",    "pct": 9.8},
        {"name": "RiskRani",       "pct": 7.2},
        {"name": "CandleKing",     "pct": 5.6},
        {"name": "ThetaGang",      "pct": 3.1},
        {"name": "LongTermLaxmi",  "pct": 1.9},
        {"name": "AveragingAnil",  "pct": -1.4},
        {"name": "FOMO_Farhan",    "pct": -4.2},
        {"name": "RevengeRavi",    "pct": -8.7},
    ]
    if st.session_state.leaderboard_opt_in and st.session_state.leaderboard_name:
        fake_peers.append({"name": st.session_state.leaderboard_name,
                           "pct": my_pct})
    fake_peers.sort(key=lambda x: x["pct"], reverse=True)

    for i, p in enumerate(fake_peers):
        cls = ""; medal = ""
        if i == 0: cls, medal = "rank-1", "🥇"
        elif i == 1: cls, medal = "rank-2", "🥈"
        elif i == 2: cls, medal = "rank-3", "🥉"
        me = (p["name"] == st.session_state.leaderboard_name
              and st.session_state.leaderboard_opt_in)
        display = ("⭐ " if me else "") + f"{medal} {p['name']}"
        st.markdown(f"""<div class='rank-row {cls}'>
            <span>{display}</span>
            <span><b>{p['pct']:+.2f}%</b></span>
        </div>""", unsafe_allow_html=True)

    st.caption("⚠️ Peer data is illustrative for educational motivation only. "
               "Rankings reset weekly.")


# ============================================================================
# PAGE: ACHIEVEMENTS
# ============================================================================
def page_achievements():
    st.markdown(f"<h1 class='hero-title'>{t('achieve')}</h1>",
                unsafe_allow_html=True)
    u = len(st.session_state.achievements); tot = len(ACHIEVEMENTS)
    st.progress(u/tot, text=f"{u}/{tot} unlocked")
    cols = st.columns(3)
    for i, (k, a) in enumerate(ACHIEVEMENTS.items()):
        with cols[i % 3]:
            if k in st.session_state.achievements:
                st.markdown(f"""<div class='unlocked-card'
                    style='padding:1rem; text-align:center;'>
                    <div style='font-size:2rem;'>{a['icon']}</div>
                    <b style='color:#10b981;'>{a['name']}</b>
                    <div style='color:#94a3b8; font-size:0.8rem;'>
                    {a['desc']}</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='locked-card' style='padding:1rem;'>
                    <div style='font-size:2rem; filter:grayscale(1);'>🔒</div>
                    <b style='color:#64748b;'>{a['name']}</b>
                    <div style='color:#64748b; font-size:0.8rem;'>
                    {a['desc']}</div></div>""", unsafe_allow_html=True)


# ============================================================================
# PAGE: ADVISORS
# ============================================================================
def page_advisors():
    st.markdown(f"<h1 class='hero-title'>{t('advisors')}</h1>",
                unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Curated SEBI-registered and educational "
                "resources. Non-monetized.</p>", unsafe_allow_html=True)

    st.markdown("""<div class='insight'>
    ℹ️ These links point to official SEBI directories and exchange education
    portals. FinSpire receives no compensation and endorses no specific
    provider. Always verify SEBI registration before engaging.
    </div>""", unsafe_allow_html=True)

    for a in ADVISORS:
        st.markdown(f"""<div class='advisor-card'>
            <b style='color:#22d3ee;'>{a['name']}</b>
            <span style='color:#94a3b8; font-size:0.82rem;'>
            — {a['type']}</span>
            <div style='color:#cbd5e1; font-size:0.9rem; margin-top:0.4rem;'>
            {a['note']}</div>
            <a href='{a["url"]}' target='_blank'
               style='color:#10b981; font-size:0.85rem;'>
            Open resource ↗</a>
        </div>""", unsafe_allow_html=True)


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================
def page_dashboard():
    st.markdown(f"<h1 class='hero-title'>{t('dash')}</h1>",
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='card'>
            <div class='metric-label'>Chapters</div>
            <div class='metric-value'>{len(st.session_state.completed_chapters)}/{len(CURRICULUM)}</div>
            </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='card'>
            <div class='metric-label'>Capital Earned</div>
            <div class='metric-value'>{inr(st.session_state.unlocked_capital)}</div>
            </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class='card'>
            <div class='metric-label'>XP</div>
            <div class='metric-value'>{st.session_state.xp}</div>
            </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class='card'>
            <div class='metric-label'>Risk Profile</div>
            <div class='metric-value' style='font-size:1.2rem;'>
            {st.session_state.risk_profile or '—'}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("### 📈 Chapter Rewards Earned")
    names = [f"{c['icon']} {c['title']}" for c in CURRICULUM]
    vals = [c["reward"] if c["id"] in st.session_state.completed_chapters else 0
            for c in CURRICULUM]
    fig = go.Figure(go.Bar(
        x=names, y=vals,
        marker_color=["#10b981" if v > 0 else "#334155" for v in vals],
        text=[inr(v) for v in vals], textposition="outside"))
    fig.update_layout(template="plotly_dark", height=360,
                      paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      yaxis_title="₹",
                      margin=dict(l=20, r=20, t=20, b=100))
    st.plotly_chart(fig, use_container_width=True)

    if st.session_state.equity_curve:
        st.markdown("### 💹 Equity Curve")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(y=st.session_state.equity_curve,
                                  mode="lines+markers",
                                  line=dict(color="#22d3ee", width=3),
                                  fill="tozeroy",
                                  fillcolor="rgba(34,211,238,0.1)"))
        fig2.update_layout(template="plotly_dark", height=300,
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           xaxis_title="Round", yaxis_title="₹",
                           margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 📊 Trading Analytics")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Max Drawdown", f"{st.session_state.max_drawdown*100:.2f}%")
    a2.metric("Trades", len([e for e in st.session_state.journal
                             if e.get("kind") != "note"]))
    a3.metric("Open Positions",
              sum(1 for h in st.session_state.instrument_holdings.values()
                  if h["units"] > 0))
    a4.metric("Achievements", f"{len(st.session_state.achievements)}/"
              f"{len(ACHIEVEMENTS)}")

    export = {
        "xp": st.session_state.xp,
        "capital": st.session_state.unlocked_capital,
        "chapters": st.session_state.completed_chapters,
        "achievements": st.session_state.achievements,
        "trades": len(st.session_state.journal),
        "risk_profile": st.session_state.risk_profile,
        "exported_at": datetime.now().isoformat(),
    }
    st.download_button("⬇️ Export progress (JSON)",
                       json.dumps(export, indent=2, default=str),
                       file_name="finspire_progress.json",
                       mime="application/json",
                       key="dashboard_download")


# ============================================================================
# DISCLAIMER FOOTER
# ============================================================================
def render_footer():
    st.markdown("""<div class='disclaimer-footer'>
        <b>⚖️ SEBI Disclaimer:</b> FinSpire is a strictly educational simulation.
        It is <b>not</b> a SEBI-registered investment advisor, research analyst,
        portfolio manager, or broker. Nothing here constitutes investment advice
        or a recommendation to buy/sell any security. Simulated performance does
        not reflect real market outcomes. Live market data, where shown, is
        provided by third-party sources for educational illustration only.
        Options/F&O trading is highly leveraged and SEBI's 2023 study shows
        ~90% of retail F&O traders incur losses. Please consult a SEBI-registered
        advisor before investing. Capital at risk.
    </div>""", unsafe_allow_html=True)


# ============================================================================
# MAIN ROUTER
# ============================================================================
def main():
    if not st.session_state.onboarded:
        render_onboarding()
        render_footer()
        return

    render_sidebar()
    pages = {
        "Learn":             page_learn,
        "Trade Simulator":   page_trade,
        "Options":           page_options,
        "Journal":           page_journal,
        "Backtest":          page_backtest,
        "Prop Firm":         page_prop,
        "Leaderboard":       page_leaderboard,
        "Achievements":      page_achievements,
        "Advisors":          page_advisors,
        "Dashboard":         page_dashboard,
    }
    pages.get(st.session_state.page, page_dashboard)()
    render_footer()


if __name__ == "__main__":
    main()
