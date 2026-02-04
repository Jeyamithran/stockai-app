# 📈 StockAI Dashboard

**StockAI** is a lightweight, AI-powered financial analysis tool that combines traditional technical indicators with the reasoning capabilities of Large Language Models (LLMs). Built with **Flask** and **Perplexity AI**, it provides real-time insights into stock trends, fundamental valuation, and market sentiment.

## 🚀 Features

### 📊 Technical Analysis Engine
*   **Real-time Data**: Fetches live market data via `yfinance`.
*   **Indicators**: AUTOMATIC calculation of **SMA (9/20)**, **RSI**, **CCI**, and **VWAP**.
*   **Pattern Recognition**: Detects candlestick patterns like *Bullish/Bearish Engulfing* and *Doji* on the fly.
*   **Interactive Charts**: Visualized using **ApexCharts.js** for smooth interactions.

### 🧠 AI-Driven Insights (Powered by Perplexity Sonar-Pro)
*   **Technical Signal**: AI synthesizes indicator data to give a Buy/Sell/Hold rating.
*   **Fundamental Deep Dive**: Analyzes valuation, profitability, and solvency metrics.
*   **Risk Assessment**: Identifies key downside risks and volatility factors.
*   **News Sentiment**: Summarizes top global headlines and specific ticker news with sentiment scoring.

## 🛠️ Technology Stack

*   **Backend**: Python (Flask)
*   **AI/LLM**: Perplexity API (`sonar-pro`)
*   **Data Source**: Yahoo Finance (`yfinance`)
*   **Technical Lib**: Finta
*   **Frontend**: HTML5, CSS3, Vanilla JavaScript, ApexCharts

## ⚡ Quick Start

### Prerequisites
*   Python 3.8+
*   A Perplexity API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/Jeyamithran/stockai-app.git
    cd stockai-app
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```bash
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxx
    ```

4.  **Run the Application**
    ```bash
    python server.py
    ```
    Visit `http://localhost:5000` in your browser.

## 🔌 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/analysis` | `POST` | Returns technical indicators (RSI, VWAP, Patterns) and chart data. |
| `/api/ai-signal` | `POST` | Queries Perplexity AI for specific insights (Tech/Fund/Risk/News). |
| `/api/news` | `GET` | Fetches summarized global market news. |

## 🛡️ License

MIT License. Free for educational and personal use.
