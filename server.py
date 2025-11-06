import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import yfinance as yf
import pandas as pd
from finta import TA
from dotenv import load_dotenv
import requests

load_dotenv()
app = Flask(__name__)
CORS(app)

limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour"])
limiter.init_app(app)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
NEWS_CACHE = {"news": None, "ts": None}

TIMEFRAME_MAP = {
    "1d": {"period": "1d", "interval": "15m"},
    "1w": {"period": "5d", "interval": "1h"},
    "1mo": {"period": "1mo", "interval": "1d"},
}


def compute_vwap(df):
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    return (tp * df["Volume"]).cumsum() / df["Volume"].replace(0, pd.NA).cumsum()


def detect_pattern(df):
    if len(df) < 3:
        return "No clear pattern"
    c2, c3 = df.iloc[-2], df.iloc[-1]
    if c3["Close"] > c3["Open"] and c3["Close"] > c2["Close"]:
        return "Bullish Engulfing"
    if c3["Close"] < c3["Open"] and c3["Close"] < c2["Close"]:
        return "Bearish Engulfing"
    if abs(c3["Close"] - c3["Open"]) < (c3["High"] - c3["Low"]) * 0.1:
        return "Doji"
    return "No clear pattern"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/analysis", methods=["POST"])
def analysis():
    data = request.get_json() or {}
    symbol = (data.get("symbol") or "").upper().strip()
    timeframe = (data.get("timeframe") or "1d").strip().lower()

    if not symbol:
        return jsonify({"error": "Stock symbol missing"}), 400

    tf = TIMEFRAME_MAP.get(timeframe, TIMEFRAME_MAP["1d"])
    df = yf.Ticker(symbol).history(period=tf["period"], interval=tf["interval"])
    if df.empty:
        return jsonify({"error": f"No data for {symbol}"}), 400

    df["SMA9"] = df["Close"].rolling(9).mean()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["RSI"] = TA.RSI(df)
    df["CCI"] = TA.CCI(df)
    df["VWAP"] = compute_vwap(df)
    df = df.fillna(0).replace([float("inf"), float("-inf")], 0)

    latest = df.iloc[-1]
    candles = [
        {
            "x": str(i),
            "y": [round(r.Open, 2), round(r.High, 2), round(r.Low, 2), round(r.Close, 2)],
        }
        for i, r in enumerate(df.itertuples())
    ]

    result = {
        "symbol": symbol,
        "price": round(float(latest.Close), 2),
        "SMA9": round(float(latest.SMA9), 2),
        "SMA20": round(float(latest.SMA20), 2),
        "RSI": round(float(latest.RSI), 2),
        "CCI": round(float(latest.CCI), 2),
        "VWAP": round(float(latest.VWAP), 2),
        "VWAP_relation": "Above" if latest.Close >= latest.VWAP else "Below",
        "pattern_15m": detect_pattern(df),
        "candles": candles,
    }

    return jsonify(result)


def perplexity(prompt):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": "sonar-pro", "messages": [{"role": "user", "content": prompt}], "max_output_tokens": 400}
    r = requests.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
    return r.json()


@app.route("/api/ai-signal", methods=["POST"])
def ai_signal():
    data = request.get_json()
    symbol = data.get("symbol", "").upper()
    timeframe = data.get("timeframe", "1d")
    tab = data.get("tab", "technical")

    prompts = {
        "technical": f"Provide concise JSON with: signal, support, resistance, vwap_relation, pattern_15m, summary for {symbol} ({timeframe}).",
        "fundamental": f"Provide concise JSON with: signal, keyFundamentals (valuation, profitability, solvency), summary for {symbol}.",
        "risk": f"Provide concise JSON with: signal, keyRisks, summary for {symbol}.",
        "news": f"Summarize recent stock-related news sentiment for {symbol} in JSON (sentiment, topNews [headline, summary, sentiment], summary).",
    }
    return jsonify(perplexity(prompts[tab]))


@app.route("/api/news", methods=["GET"])
def news():
    if NEWS_CACHE["news"]:
        return jsonify({"news": NEWS_CACHE["news"]})
    prompt = "Give top 5 global market headlines with sentiment and summary as JSON."
    data = perplexity(prompt)
    summary = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    NEWS_CACHE["news"] = summary
    NEWS_CACHE["ts"] = datetime.utcnow().isoformat()
    return jsonify({"news": NEWS_CACHE["news"]})


if __name__ == "__main__":
    app.run(debug=True)
