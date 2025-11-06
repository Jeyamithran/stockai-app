document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("stockForm");
  const stockDataDiv = document.getElementById("stockData");
  const aiSignalDiv = document.getElementById("aiSignal");
  const chartDiv = document.getElementById("chart");
  const newsDiv = document.getElementById("newsContent");
  const tabs = document.querySelectorAll(".tab-button");
  const refreshNewsBtn = document.getElementById("refreshNews");
  let activeTab = "technical";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const symbol = document.getElementById("symbolInput").value.trim().toUpperCase();
    const timeframe = document.getElementById("timeframeSelect").value;
    if (!symbol) return alert("Enter a stock symbol");

    aiSignalDiv.innerHTML = "🔍 Loading AI analysis...";
    chartDiv.innerHTML = "";

    const res = await fetch("/api/analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, timeframe }),
    });
    const data = await res.json();
    if (data.error) {
      stockDataDiv.innerHTML = `<div class="error">${data.error}</div>`;
      return;
    }

    stockDataDiv.innerHTML = `
      <h3>${data.symbol} — $${data.price}</h3>
      <p>SMA9: ${data.SMA9} | SMA20: ${data.SMA20}<br>
      RSI: ${data.RSI} | CCI: ${data.CCI}<br>
      VWAP: ${data.VWAP} (${data.VWAP_relation})<br>
      Pattern (15m): ${data.pattern_15m}</p>
    `;

    renderChart(data.candles);
    fetchAISignal(symbol, timeframe, activeTab);
  });

  async function fetchAISignal(symbol, timeframe, tab) {
    aiSignalDiv.innerHTML = "🤖 Fetching AI insights...";
    const res = await fetch("/api/ai-signal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, timeframe, tab }),
    });
    const ai = await res.json();

    let content = ai?.choices?.[0]?.message?.content || JSON.stringify(ai, null, 2);
    content = content.replace(/```json|```/g, "").trim();

    let parsedHTML = "";
    try {
      const parsed = JSON.parse(content);
      if (Array.isArray(parsed)) {
        parsedHTML = parsed.map(item => formatObject(item)).join("");
      } else {
        parsedHTML = formatObject(parsed);
      }
    } catch {
      parsedHTML = `<pre>${content}</pre>`;
    }

    aiSignalDiv.innerHTML = `
      <h3>🤖 ${tab[0].toUpperCase() + tab.slice(1)} Analysis</h3>
      <div class="ai-card">${parsedHTML}</div>
    `;
  }

  function formatObject(obj) {
    let html = "<div class='json-block'>";
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === "object") {
        html += `<div class='json-sub'><strong>${key}:</strong> ${formatObject(value)}</div>`;
      } else {
        html += `<div><strong>${key}:</strong> ${value}</div>`;
      }
    }
    return html + "</div>";
  }

  function renderChart(candles) {
    if (!candles || candles.length === 0) return;

    const options = {
      series: [{ data: candles.map(c => ({ x: c.x, y: c.y })) }],
      chart: { type: "candlestick", height: 320, background: "transparent" },
      xaxis: { labels: { show: false } },
      yaxis: { tooltip: { enabled: true } },
      grid: { borderColor: "rgba(255,255,255,0.1)" },
    };

    chartDiv.innerHTML = "<h3>📊 Candlestick Chart</h3><div id='chart-container'></div>";
    const chartEl = document.getElementById("chart-container");
    new ApexCharts(chartEl, options).render();
  }

  tabs.forEach(btn => {
    btn.addEventListener("click", () => {
      tabs.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeTab = btn.dataset.type;

      const symbol = document.getElementById("symbolInput").value.trim().toUpperCase();
      const timeframe = document.getElementById("timeframeSelect").value;
      if (symbol) fetchAISignal(symbol, timeframe, activeTab);
    });
  });

  refreshNewsBtn.addEventListener("click", fetchNews);

  async function fetchNews() {
    newsDiv.innerHTML = "📰 Loading...";
    const res = await fetch("/api/news");
    const data = await res.json();
    let content = data.news?.replace(/```json|```/g, "").trim();
    try {
      const json = JSON.parse(content);
      const items = json.map(n => `
        <div class="news-item">
          <h4>${n.headline}</h4>
          <p>${n.summary}</p>
          <span class="sentiment ${n.sentiment}">${n.sentiment}</span>
        </div>`).join("");
      newsDiv.innerHTML = `<div class="news-list">${items}</div>`;
    } catch {
      newsDiv.innerHTML = `<pre>${content}</pre>`;
    }
  }

  fetchNews();
});
