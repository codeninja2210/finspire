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
from streamlit_js_eval import streamlit_js_eval

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
             "body": ("Indian savings accounts pay ~3% interest. Inflation runs "
                      "at ~5–6% on average. Every year, ₹1,00,000 sitting in a "
                      "savings account loses roughly ₹2,000–₹3,000 of real "
                      "purchasing power — even though the number on your "
                      "passbook went up. To *build* wealth, your money must "
                      "grow faster than inflation."),
             "worked_example": ("₹1,00,000 in savings @ 3% for 10 years → "
                                "₹1,34,392.\n₹1,00,000 invested @ 12% for 10 "
                                "years → ₹3,10,585.\n₹1.76 lakh difference."),
             "pitfall": ("'Savings = safe, stocks = risky' is oversimplified. "
                         "Savings is safe from volatility but guaranteed to "
                         "lose to inflation.")},
            {"heading": "What a stock actually is (and isn't)",
             "body": ("A stock is fractional ownership. 10 Infosys shares = a "
                      "slice of every office, contract, and rupee of profit. "
                      "You didn't lend money — you became a co-owner. Two "
                      "payoff channels: price growth + dividends."),
             "worked_example": ("10 Infosys @ ₹1,500 = ₹15,000 invested.\n"
                                "Price rises to ₹1,900 → holding = ₹19,000 "
                                "(+₹4,000).\nPlus ₹18/share dividend = ₹180 "
                                "cash income."),
             "pitfall": ("Price ≠ company value. Price is what the last buyer "
                         "paid. Fundamentals are the underlying reality.")},
            {"heading": "Why companies sell shares",
             "body": ("Companies raise capital two ways: debt (must be repaid) "
                      "or equity (shareholders paid only if company succeeds). "
                      "High-growth ventures prefer equity because there's no "
                      "fixed repayment obligation."),
             "worked_example": ("Zomato's 2021 IPO raised ~₹9,375 crore, which "
                                "funded Blinkit acquisition and expansion."),
             "pitfall": ("'I don't want to bet on companies' — but keeping "
                         "everything in FDs is also a bet on inflation staying "
                         "low. Every decision is a bet.")},
            {"heading": "India's market infrastructure",
             "body": ("NSE (1992) + BSE (1875, Asia's oldest) are the exchanges. "
                      "SEBI regulates. You need a demat account (holds shares) "
                      "+ trading account (places orders) with a SEBI-registered "
                      "broker. NSDL/CDSL are the depositories."),
             "worked_example": ("Zerodha account → KYC in 24h → demat + trading "
                                "→ buy 5 Reliance on NSE → shares appear T+1 → "
                                "sellable 9:15 AM–3:30 PM IST."),
             "pitfall": ("Never open demat with unregistered 'advisory groups' "
                         "or WhatsApp tip brokers. Verify SEBI registration.")},
        ],
        "key_takeaways": [
            "Cash in savings is guaranteed to lose to inflation over time.",
            "A stock is fractional ownership — price + dividends are the two payoffs.",
            "Companies sell equity to raise capital without fixed repayment.",
            "NSE + BSE are exchanges; SEBI regulates; NSDL/CDSL hold shares.",
        ],
        "quiz": [
            {"q": "Owning a stock means…",
             "options": ["You lent money to the company",
                         "You own a small piece of the company",
                         "You work for the company"],
             "correct": 1,
             "explain_correct": ("Stock = equity = ownership. Legal claim on "
                                 "assets and future profits proportional to "
                                 "shareholding."),
             "explain_wrong": ("Lending = bond. Working = employment. Only "
                               "stock means ownership."),
             "mental_model": "Stock = slice of pie. Bond = IOU on pie."},
            {"q": "Why is keeping all money in a savings account risky?",
             "options": ["Banks steal it",
                         "Inflation erodes purchasing power faster than interest grows it",
                         "RBI freezes accounts"],
             "correct": 1,
             "explain_correct": ("Savings 3%, inflation 5–6%. Real return is "
                                 "negative. Money 'grows' on paper but buys "
                                 "less each year."),
             "explain_wrong": ("Banks don't steal (₹5L insured by DICGC). The "
                               "real risk is inflation."),
             "mental_model": "If return < inflation, 'safe' money is melting."},
            {"q": "Which Indian regulator oversees stock markets?",
             "options": ["RBI", "SEBI", "IRDAI"], "correct": 1,
             "explain_correct": ("SEBI — Securities and Exchange Board of India, "
                                 "est. 1992. Regulates exchanges, brokers, MFs, "
                                 "listed companies."),
             "explain_wrong": ("RBI = banks. IRDAI = insurance. AMFI = industry "
                               "body, not regulator."),
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
             "body": ("Every stock has a bid queue (buyers) and ask queue "
                      "(sellers). The gap = spread. Tight spread = liquid. "
                      "Wide spread = illiquid (slippage cost). Last traded "
                      "price = where a bid met an ask."),
             "worked_example": ("Bid ₹2,849.50 / Ask ₹2,850.00 → spread ₹0.50 "
                                "(0.017%).\nSmall-cap: Bid ₹99 / Ask ₹101 → "
                                "spread ₹2 (2%). Illiquid stocks tax every "
                                "trade."),
             "pitfall": ("Market orders in illiquid stocks cause 'slippage' — "
                         "fill price much worse than screen. Use limit orders "
                         "if spread > 0.5%.")},
            {"heading": "Indices — the market's heartbeat",
             "body": ("An index is a weighted basket. NIFTY 50 = top 50 NSE "
                      "companies by free-float market cap. SENSEX = top 30 BSE. "
                      "Bank NIFTY = 12 largest banks."),
             "worked_example": ("NIFTY up 0.8% = weighted average of Reliance "
                                "+1.5%, HDFC +0.3%, Infosys −0.2%, TCS +0.5%, "
                                "ITC +2.1%."),
             "pitfall": ("'Market up → my stock up' is wrong. Index correlates, "
                         "doesn't determine.")},
            {"heading": "Market hours and settlement (IST)",
             "body": ("NSE/BSE run 9:15 AM–3:30 PM Mon–Fri. Pre-open auction "
                      "9:00–9:15. Post-close 3:40–4:00 PM. Settlement T+1 — "
                      "India led globally in Jan 2023."),
             "worked_example": ("Buy 100 Infosys Monday 11 AM → cash debited "
                                "same day → 100 shares in demat Tuesday eve → "
                                "sellable Wednesday."),
             "pitfall": ("Can't sell same-day without intraday product. MIS "
                         "auto-squares at 3:20 PM.")},
            {"heading": "Who actually moves the market",
             "body": ("Retail trades millions of small orders. Direction is set "
                      "by FIIs (foreign institutions), DIIs (Indian MFs, LIC), "
                      "and proprietary desks. FII/DII data is public and free."),
             "worked_example": ("March 2020: FIIs sold ₹60,000 cr in a month. "
                                "NIFTY −38%. DIIs bought. Six months later, "
                                "NIFTY recovered 60%+."),
             "pitfall": ("Retail trading more doesn't beat the market. Brokerage "
                         "+ STT + slippage = 0.3–1% per round trip.")},
        ],
        "key_takeaways": [
            "Price = last trade. Bid/ask spread is your real cost.",
            "Indices summarize; don't dictate individual stock moves.",
            "India runs T+1 settlement — shares arrive next business day.",
            "FII/DII flows drive direction; retail drives volume.",
        ],
        "quiz": [
            {"q": "Bid = ₹99, Ask = ₹101. What is the spread?",
             "options": ["₹1", "₹2", "₹200"], "correct": 1,
             "explain_correct": ("Spread = ask − bid = ₹101 − ₹99 = ₹2. On a "
                                 "₹100 stock that's 2% — huge tax on frequent "
                                 "trading."),
             "explain_wrong": ("₹1 = midpoint offset. ₹200 = meaningless "
                               "multiplication."),
             "mental_model": "Spread = ask − bid."},
            {"q": "NIFTY 50 tracks how many companies?",
             "options": ["30", "50", "500"], "correct": 1,
             "explain_correct": ("NIFTY 50 = 50 NSE companies. SENSEX = 30 BSE. "
                                 "NIFTY 500 = 500 companies."),
             "explain_wrong": ("30 is SENSEX. 500 is NIFTY 500. Don't mix up."),
             "mental_model": "NIFTY 50 = NSE's 50. SENSEX = BSE's 30."},
            {"q": "What does T+1 settlement mean?",
             "options": ["Settles one day after execution",
                         "Settles after 1 week", "Settles instantly"],
             "correct": 0,
             "explain_correct": ("T = trade day. +1 = one business day for "
                                 "delivery. India adopted T+1 in Jan 2023."),
             "explain_wrong": ("T+0 is future. T+5 was old. T+1 = next business "
                               "day."),
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
             "body": ("A candle compresses Open, High, Low, Close. Body = "
                      "open↔close. Wicks = High/Low. Green = close>open. "
                      "Red = close<open."),
             "worked_example": ("Reliance: O=₹2,800, H=₹2,850, L=₹2,780, "
                                "C=₹2,840.\nBody +₹40 green. Upper wick ₹10, "
                                "lower wick ₹20 (buyers defended)."),
             "pitfall": ("Wick length is often more informative than body "
                         "color. Tiny green + huge upper wick = bearish.")},
            {"heading": "The three candles that matter most",
             "body": ("Doji = indecision. Hammer = long lower wick at lows "
                      "(bullish). Shooting Star = long upper wick at highs "
                      "(bearish). All depend on context — trend + level + "
                      "volume."),
             "worked_example": ("NIFTY hits 22,000 support. Candle O=22,050 "
                                "C=22,040, L=21,850. Lower wick ₹200 = buyers "
                                "smashed the rejection."),
             "pitfall": ("Dojis in a range mean nothing. Context is everything.")},
            {"heading": "Why volume is the truth serum",
             "body": ("Volume = participation. Breakouts on LOW volume are "
                      "traps. Same breakout on 2×+ volume is real. No volume, "
                      "no trade."),
             "worked_example": ("₹510 resistance. Day 1 crosses on 1.3× avg → "
                                "weak. Day 2 crosses on 5× avg → strong."),
             "pitfall": ("Low-volume breakouts are the #1 retail trap.")},
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
             "explain_correct": ("Long lower wick = sellers pushed down but "
                                 "buyers overwhelmed and closed near top. "
                                 "Bullish reversal at tested support."),
             "explain_wrong": ("'Sellers in control' = shooting star. Volume "
                               "always matters."),
             "mental_model": "Hammer at support = bulls planted a flag."},
            {"q": "A breakout on very low volume is usually…",
             "options": ["Very reliable", "A trap / weak signal", "Best entry"],
             "correct": 1,
             "explain_correct": ("Low volume = low conviction. Professionals "
                                 "wait for 1.5–2× average volume to confirm."),
             "explain_wrong": ("'Very reliable' is backwards. 'Best entry' "
                               "ignores failure rate."),
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
             "body": ("Uptrend = higher highs + higher lows. Downtrend = lower "
                      "highs + lower lows. Sideways = range-bound. Trade with "
                      "the trend until a structural break."),
             "worked_example": ("NIFTY 2023: 17,800 → 16,800 → 19,900 → 18,800 "
                                "→ 21,700. Swing highs rising, swing lows "
                                "rising = bullish structure."),
             "pitfall": ("'Red day = bearish' is wrong. Trends are measured "
                         "over swings, not days.")},
            {"heading": "The five drivers of trend",
             "body": ("1. FII/DII flows, 2. RBI policy, 3. Union Budget, "
                      "4. Earnings, 5. Global cues (US Fed, crude, China)."),
             "worked_example": ("May 2024: exit polls → NIFTY +3% in one "
                                "session. Driver: political stability → capex "
                                "continuity."),
             "pitfall": ("Chart patterns without macro context fail.")},
            {"heading": "Support, resistance, and why they matter",
             "body": ("Support = buyers step in. Resistance = sellers unload. "
                      "Broken support becomes resistance. Broken resistance "
                      "becomes support."),
             "worked_example": ("NIFTY holds 22,000 five times. 6th test "
                                "breaks to 21,700. Every rally back to 22,000 "
                                "gets sold — support flipped to resistance."),
             "pitfall": ("Heavily retested support is CLOSER to breaking, not "
                         "safer.")},
        ],
        "key_takeaways": [
            "Uptrend = HH + HL. Downtrend = LH + LL.",
            "Trends driven by flows, policy, budget, earnings, global cues.",
            "Broken support becomes resistance; vice versa.",
            "Heavily tested support is closer to breaking.",
        ],
        "quiz": [
            {"q": "Higher highs + higher lows = ?",
             "options": ["Bearish trend", "Bullish trend", "Sideways"],
             "correct": 1,
             "explain_correct": ("HH + HL = classic bullish structure. "
                                 "Intact until a lower low or lower high."),
             "explain_wrong": ("Bearish is opposite. Sideways is neither."),
             "mental_model": "HH + HL = bull."},
            {"q": "FIIs sold ₹10,000 cr in a day. Likely short-term impact?",
             "options": ["NIFTY up sharply", "NIFTY down / pressure", "No effect"],
             "correct": 1,
             "explain_correct": ("₹10k cr net selling = huge supply. DIIs "
                                 "absorb some but downward pressure dominates."),
             "explain_wrong": ("FIIs hold ~20% of NSE market cap. Flow "
                               "matters."),
             "mental_model": "Big money exits → market feels weight."},
            {"q": "Price bounces 5 times off ₹500 then breaks below. This is…",
             "options": ["Support holding", "Support breakdown — bearish",
                         "Bullish"],
             "correct": 1,
             "explain_correct": ("Heavily retested support weakens. Break "
                                 "becomes resistance. Sharp move due to stop "
                                 "clusters."),
             "explain_wrong": ("'Holding' would require a bounce. 'Bullish' is "
                               "the opposite."),
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
             "body": ("Risk 1–2% per trade max. 10 losses at 5% = −40% "
                      "(need +67% to recover). 10 losses at 1% = −10% (need "
                      "+11%). Survival math > win-rate vanity."),
             "worked_example": ("₹1,00,000 capital. 1% = ₹1,000 max loss. "
                                "5 losses = −₹5,000 = still alive.\n5% = "
                                "₹5,000 max loss. 5 losses = −₹25,000 = deep "
                                "hole."),
             "pitfall": ("Sizing by confidence is backwards. Size by risk.")},
            {"heading": "Position sizing — the formula that saves you",
             "body": ("Position Size = (Capital × Risk%) ÷ (Entry − Stop). "
                      "Numerator = money risk. Denominator = price risk per "
                      "share."),
             "worked_example": ("Capital ₹1L, risk 1% = ₹1,000. Entry ₹500, "
                                "stop ₹480, per-share risk ₹20. Position = "
                                "1000 ÷ 20 = 50 shares."),
             "pitfall": ("Buying round numbers instead of computed size.")},
            {"heading": "Risk:Reward — the only equation that matters",
             "body": ("1:1 R:R needs >50% win rate. 1:3 R:R needs only 25% win "
                      "rate. Minimum acceptable R:R = 1:2."),
             "worked_example": ("Strategy A: 60% win, 1:1 = +0.20R.\n"
                                "Strategy B: 40% win, 1:3 = +0.60R. B is 3× "
                                "more profitable."),
             "pitfall": ("Chasing high win rates misses the point.")},
            {"heading": "The rules that never bend",
             "body": ("1. Stop-loss always. 2. Never average a loser. 3. Two "
                      "losses → stop for day. 4. No FOMO. 5. Journal every "
                      "trade."),
             "worked_example": ("Entry ₹500, stop ₹490, target ₹530 (1:3). "
                                "Stop executed at ₹489.80 with slippage — "
                                "loss ₹10.20 instead of ₹10."),
             "pitfall": ("'I'll just watch it and exit if it drops' always "
                         "fails.")},
        ],
        "key_takeaways": [
            "Risk 1–2% per trade.",
            "Size = (Capital × Risk%) ÷ (Entry − Stop).",
            "R:R ≥ 1:2. 1:3 at 40% win = better than 1:1 at 60%.",
            "Stop-loss on every trade.",
        ],
        "quiz": [
            {"q": "Capital ₹50,000, risk 2%, entry ₹100, stop ₹95. Position size?",
             "options": ["100 shares", "200 shares", "500 shares"],
             "correct": 1,
             "explain_correct": ("Risk = 2% × 50k = ₹1,000. Per-share risk "
                                 "₹5. Position = 200 shares. Loss if stopped = "
                                 "₹1,000 = exactly 2%."),
             "explain_wrong": ("100 = 1% too small. 500 = 5% too much."),
             "mental_model": "Size = Capital×Risk ÷ (Entry−Stop)."},
            {"q": "Which R:R is usually profitable even at 40% win rate?",
             "options": ["1:1", "1:2", "1:0.5"], "correct": 1,
             "explain_correct": ("1:2 at 40% = +0.20R per trade. Positive "
                                 "expectancy with losing win rate."),
             "explain_wrong": ("1:1 at 40% = −0.20R. 1:0.5 = −0.40R. Both "
                               "losing."),
             "mental_model": "1:2 or better."},
            {"q": "When should you trade without a stop-loss?",
             "options": ["When very confident", "Never", "On small positions"],
             "correct": 1,
             "explain_correct": ("Never. Confidence isn't an edge. Stops = "
                                 "survival."),
             "explain_wrong": ("'Confident' trades lose big. Small positions "
                               "train bad habits."),
             "mental_model": "No stop = no trade."},
        ],
    },
    {
        "id": "ch6", "title": "Psychology & Drawdowns", "icon": "🧠",
        "reward": 20000, "practice": "bias_identifier",
        "hook": "The market isn't rigged against you. Your own brain is.",
        "deep_lesson": [
            {"heading": "The four biases that destroy portfolios",
             "body": ("FOMO — buying tops. Revenge trading — doubling down "
                      "after loss. Confirmation bias — only reading bullish "
                      "news. Anchoring — holding losers because 'it was "
                      "higher once'."),
             "worked_example": ("Zomato 2021 peak ~₹160. Trader buys ₹150, "
                                "refuses to sell at ₹100, ₹80, ₹60. Two years "
                                "later still holding −60%."),
             "pitfall": ("'I'm logical' — everyone says this. Everyone is "
                         "wrong.")},
            {"heading": "Drawdown math — why 50% down is not 50% up",
             "body": ("−50% needs +100% to recover. −75% needs +300%. −90% "
                      "needs +900%. Losses are asymmetric. Real Indian "
                      "drawdowns: 2008 −60%, 2020 −38%, 2022 −17%."),
             "worked_example": ("₹10L → ₹5L. Recovery at +12% CAGR = 6 years "
                                "just to flat. Inflation ran ~30% meanwhile."),
             "pitfall": ("'I'll wait it out' without a plan = panic-sell at "
                         "bottom.")},
            {"heading": "Why journaling works (and how to do it)",
             "body": ("Log: time, asset, size, reason, emotion, R:R, outcome, "
                      "lesson. Review weekly for behavioral patterns, not P&L."),
             "worked_example": ("30-day review reveals 12 of 15 losses came "
                                "after a previous loss. Diagnosis: revenge "
                                "trading. Fix: 30-min cool-down rule."),
             "pitfall": ("Journaling without reviewing is just record-keeping.")},
        ],
        "key_takeaways": [
            "FOMO, revenge, confirmation bias, anchoring — know them.",
            "50% drawdown needs +100% recovery.",
            "Journal every trade. Review weekly.",
            "Define max drawdown tolerance BEFORE investing.",
        ],
        "quiz": [
            {"q": "You lost ₹5,000 today and immediately double your next "
                  "trade to win it back. This is…",
             "options": ["Smart", "Revenge trading", "Position sizing"],
             "correct": 1,
             "explain_correct": ("Revenge trading — emotion hijacks decision. "
                                 "Trade based on 'getting even', not setup."),
             "explain_wrong": ("'Smart' doubles risk when compromised. "
                               "'Sizing' is disciplined; this is the opposite."),
             "mental_model": "After loss, size down or sit out."},
            {"q": "A 50% drawdown requires what gain to recover?",
             "options": ["50%", "75%", "100%"], "correct": 2,
             "explain_correct": ("₹100 → ₹50 needs +100% to return to ₹100. "
                                 "−75% needs +300%. −90% needs +900%."),
             "explain_wrong": ("50% of ₹50 = ₹25, not enough. 75% arbitrary."),
             "mental_model": "Lose 50% → need +100%."},
            {"q": "Holding a losing stock because 'it was higher once' is…",
             "options": ["Anchoring bias", "Good strategy", "Value investing"],
             "correct": 0,
             "explain_correct": ("Anchoring — clinging to a past price. Market "
                                 "doesn't know your entry. Evaluate on today's "
                                 "merits."),
             "explain_wrong": ("'Good' = no. 'Value investing' = fundamentals, "
                               "not price nostalgia."),
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
             "body": ("STCG (<12mo): 20% + surcharge + cess. LTCG (≥12mo): "
                      "12.5% above ₹1.25L annual exemption. Cliff at 12 "
                      "months."),
             "worked_example": ("100 shares @ ₹1,000 → sold 8 months @ ₹1,300: "
                                "+₹30,000 STCG = ₹6,000 tax.\nSold 13 months: "
                                "LTCG exemption unused = ₹0 tax. ₹6,000 saved "
                                "by waiting."),
             "pitfall": ("Selling on day 360 wastes 20% vs. 12.5% rate.")},
            {"heading": "Intraday & F&O — different tax world",
             "body": ("Treated as business income, not capital gains. Slab "
                      "rate 5–30%. Books required. Expenses deductible."),
             "worked_example": ("₹5L intraday + ₹15L salary = ₹20L total. "
                                "Intraday taxed at ~30% = ₹1,50,000.\nIf held "
                                "long-term LTCG: ₹5L − ₹1.25L × 12.5% = "
                                "₹46,875. Difference ₹1L+."),
             "pitfall": ("'F&O tax-free if not withdrawn' is false. Realized "
                         "gains in FY are taxed.")},
            {"heading": "The paperwork you must know",
             "body": ("AIS = IT Dept record of trades/dividends. TIS = summary. "
                      "STT auto-deducted. KYC mandatory. Schedule CG in ITR."),
             "worked_example": ("200 trades @ ₹50,000 turnover = ₹1cr. STT "
                                "@0.1% both sides ≈ ₹20,000. Plus brokerage + "
                                "GST."),
             "pitfall": ("Not reconciling AIS with your records = notice.")},
            {"heading": "What SEBI bans — the red lines",
             "body": ("Insider trading, market manipulation, unregistered "
                      "advisory, front-running. Fines + imprisonment up to "
                      "10 years."),
             "worked_example": ("2023: Telegram channel fined ₹40 cr for "
                                "unregistered advisory with 30k subscribers — "
                                "pump-and-dump."),
             "pitfall": ("'Just sharing analysis' for any consideration can be "
                         "unregistered advice.")},
        ],
        "key_takeaways": [
            "STCG 20%, LTCG 12.5% above ₹1.25L.",
            "Intraday & F&O = business income at slab rate.",
            "AIS/TIS auto-report trades.",
            "Insider trading = SEBI red line, criminal offense.",
        ],
        "quiz": [
            {"q": "Bought 1 Jan 2024, sold 1 Mar 2024. Tax type?",
             "options": ["LTCG", "STCG", "No tax"], "correct": 1,
             "explain_correct": ("Held ~2 months < 12 → STCG @ 20%. No 'no "
                                 "tax' threshold for STCG."),
             "explain_wrong": ("LTCG requires ≥12 months. STCG taxable from "
                               "rupee 1."),
             "mental_model": "Under 12 months = STCG."},
            {"q": "LTCG on equity above ₹1.25 lakh is taxed at…",
             "options": ["10%", "12.5%", "20%"], "correct": 1,
             "explain_correct": ("12.5% as per FY 2024-25 (was 10%). Exemption "
                                 "resets annually."),
             "explain_wrong": ("10% = old rate. 20% = STCG rate."),
             "mental_model": "LTCG equity = 12.5% above ₹1.25L."},
            {"q": "Which is illegal per SEBI?",
             "options": ["Long-term investing", "Insider trading", "Index funds"],
             "correct": 1,
             "explain_correct": ("Insider trading = criminal offense. Fines "
                                 "up to ₹25 cr or 3× profit + imprisonment "
                                 "up to 10 years."),
             "explain_wrong": ("Long-term investing and index funds are "
                               "encouraged by SEBI."),
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
             "body": ("Call (CE) = right to buy. Put (PE) = right to sell. "
                      "Buyer pays premium, has defined risk (max loss = "
                      "premium). Writer collects premium, has unlimited risk."),
             "worked_example": ("NIFTY spot 22,000. Buy 22,000 CE @ ₹100, lot "
                                "25 → cost ₹2,500.\nNIFTY → 22,300: CE ≈ ₹300 "
                                "→ +₹5,000.\nNIFTY → 21,700: CE = ₹0 → −₹2,500."),
             "pitfall": ("Options decay every day. Flat markets lose for "
                         "buyers.")},
            {"heading": "Greeks — the language of options",
             "body": ("Delta = price sensitivity per ₹1 move. Gamma = Δ's rate "
                      "of change. Theta = daily time decay (kills buyers). "
                      "Vega = IV sensitivity."),
             "worked_example": ("Δ=0.5, Θ=−15/day. NIFTY +100: gain ₹50. "
                                "NIFTY flat: lose ₹15/day. 5 flat days = "
                                "−₹75 per unit."),
             "pitfall": ("Buying before events → IV crush after. Even correct "
                         "direction can lose.")},
            {"heading": "Indian F&O market reality",
             "body": ("NIFTY weekly = Thu expiry, brutal theta. Bank NIFTY "
                      "monthly = last Thu. Lot sizes: NIFTY 25, Bank NIFTY 15. "
                      "SEBI 2023: 89% of retail F&O traders lost money."),
             "worked_example": ("10 trades/week @ ₹100 × 25 lots = ₹25,000 "
                                "premium. 6 losers = −₹15,000/wk = ₹60,000/mo. "
                                "Plus brokerage + STT."),
             "pitfall": ("'Just 1 lot to learn' = ₹2,500–₹5,000/trade. Paper "
                         "trade 3–6 months first.")},
            {"heading": "When options make sense",
             "body": ("Hedging (protective puts), covered calls (income), "
                      "portfolio protection. Naked writing is where retail "
                      "blows up — unlimited tail risk."),
             "worked_example": ("Hold ₹5L NIFTY stocks. Buy NIFTY put ₹2,500 "
                                "(0.5%). NIFTY −5% → stocks −₹25,000, put "
                                "+₹20,000 → net −₹7,500 instead of −₹25,000."),
             "pitfall": ("Naked writing looks like easy income until a tail "
                         "event wipes out months of premium.")},
        ],
        "key_takeaways": [
            "Options = rights not obligations. Buyers risk premium only.",
            "Theta kills buyers daily. Flat = loss for buyers.",
            "IV crush after events hurts even correct views.",
            "89% of Indian retail F&O traders lose money.",
        ],
        "quiz": [
            {"q": "You expect NIFTY to rise. What do you buy?",
             "options": ["Put (PE)", "Call (CE)", "Both"], "correct": 1,
             "explain_correct": ("Call = right to buy. Bullish bet with "
                                 "defined risk."),
             "explain_wrong": ("Put = bearish. Both = straddle, loses to theta "
                               "in flat markets."),
             "mental_model": "Bullish → Call. Bearish → Put."},
            {"q": "NIFTY 22,000 CE premium = ₹100. NIFTY ends 21,800. Loss?",
             "options": ["₹100 (premium)", "₹200", "Nothing"], "correct": 0,
             "explain_correct": ("CE expires worthless (spot < strike). Lose "
                                 "premium = max loss as buyer."),
             "explain_wrong": ("₹200 impossible as buyer. 'Nothing' wrong — "
                               "you lose premium."),
             "mental_model": "Buyer's max loss = premium."},
            {"q": "What is 'theta' in options?",
             "options": ["Interest rate", "Time decay of premium", "Volatility"],
             "correct": 1,
             "explain_correct": ("Theta = daily time decay. Accelerates near "
                                 "expiry — final week is brutal for buyers."),
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
# PERSISTENCE — per-browser via localStorage (survives refresh, isolated)
# ============================================================================
# NOTE: Streamlit Cloud runs all visitors in one shared container.
# Writing to disk would leak progress across users.
# localStorage is scoped to the user's own browser — perfect for this use case.

PERSIST_KEYS = [
    "xp", "completed_chapters", "chapter_stage", "unlocked_capital",
    "portfolio", "starting_capital", "achievements", "journal",
    "risk_profile", "leaderboard_name", "leaderboard_opt_in",
    "instrument_prices", "instrument_holdings", "instrument_history",
    "srs_schedule", "equity_curve", "max_drawdown", "round_number",
    "options_book", "options_history", "bias_flags", "onboarded",
]

_STORAGE_KEY = "finspire_v4_progress"

def _serialize_state():
    """Convert the relevant session state to a JSON string."""
    snapshot = {k: st.session_state.get(k) for k in PERSIST_KEYS}
    snapshot["_saved_at"] = datetime.now().isoformat()
    return json.dumps(snapshot, default=str, separators=(",", ":"))

def _deserialize_state(raw: str) -> bool:
    """Restore session state from a JSON string."""
    try:
        data = json.loads(raw)
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
    except Exception:
        return False

def save_to_local_storage():
    """Write the current state to the browser's localStorage."""
    payload = _serialize_state()
    safe = payload.replace("\\", "\\\\").replace("'", "\\'")
    js = f"window.localStorage.setItem('{_STORAGE_KEY}', '{safe}')"
    streamlit_js_eval(js_expressions=js, key="save_progress_js")

def load_from_local_storage():
    """Read state from localStorage and restore it if present."""
    raw = streamlit_js_eval(
        js_expressions=f"window.localStorage.getItem('{_STORAGE_KEY}')",
        key="load_progress_js",
    )
    if raw and isinstance(raw, str) and raw != "null":
        return _deserialize_state(raw)
    return False

def clear_local_storage():
    """Remove the saved state from this browser."""
    streamlit_js_eval(
        js_expressions=f"window.localStorage.removeItem('{_STORAGE_KEY}')",
        key="clear_progress_js",
    )


# ── Auto-restore from localStorage on first load (per browser) ──
# streamlit_js_eval is async: the first call returns None, and the real
# value arrives on the next rerun. So we trigger one rerun if needed.
if not st.session_state.get("_storage_checked"):
    _raw = streamlit_js_eval(
        js_expressions=f"window.localStorage.getItem('{_STORAGE_KEY}')",
        key="load_progress_js",
    )
    if _raw is not None:
        # JS responded — either restored data or confirmed empty
        st.session_state._storage_checked = True
        if isinstance(_raw, str) and _raw != "null":
            if _deserialize_state(_raw):
                st.toast("📂 Previous progress restored from this browser",
                         icon="💾")
    else:
        # JS hasn't responded yet — rerun to retry on the next pass
        st.rerun()


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
        st.markdown("#### 💾 Progress")
        if st.button("💾 Save to this browser", use_container_width=True):
            save_to_local_storage()
            st.success("Progress saved to this browser.")
        if st.button("📂 Restore from this browser", use_container_width=True):
            if load_from_local_storage():
                st.success("Progress restored.")
                st.rerun()
            else:
                st.warning("No saved progress found in this browser.")
        if st.button("🗑️ Clear saved progress", use_container_width=True):
            clear_local_storage()
            st.info("Saved progress cleared from this browser.")

        st.markdown("---")
        st.caption(f"XP: {st.session_state.xp} • "
                   f"Badges: {len(st.session_state.achievements)} • "
                   f"Journal: {len(st.session_state.journal)}")


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
        save_to_local_storage()
        st.rerun()
    if c2.button("Explore first (no risk profile)", use_container_width=True):
        st.session_state.risk_profile = "Balanced"
        st.session_state.onboarded = True
        save_to_local_storage()
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
                    save_to_local_storage()
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
            save_to_local_storage()

        if st.session_state.feedback:
            k, m = st.session_state.feedback
            (st.success if k == "ok" else st.error)(m)
            st.session_state.feedback = None

        if st.button(t("advance"), use_container_width=True):
            advance_market()
            save_to_local_storage()
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
                save_to_local_storage()
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
                save_to_local_storage()
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
                    save_to_local_storage()
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
        save_to_local_storage()
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
        save_to_local_storage()
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
                       mime="application/json")


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
