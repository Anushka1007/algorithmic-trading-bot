# Algorithmic Trading Bot

This is a full-stack algorithmic trading and paper-trading platform combining live market data, deterministic technical-analysis signals, simulated paper trading, and historical backtesting. The platform features an autonomous background trading bot for continuous execution and a context-aware AI assistant to explain strategy decisions and portfolio performance.

> **Disclaimer**: This is a paper-trading and research project built for educational purposes. It executes simulated trades against live market data but **does not execute real-money trades** or connect to live brokerage accounts.

---

## Features

- **Market Data Integration**: Real-time and historical market data powered by the Twelve Data API, utilizing efficient memory caching to conserve rate limits.
- **Technical Indicators**: Pandas-based calculations for industry standard metrics including Simple Moving Averages (SMA), Exponential Moving Averages (EMA), Relative Strength Index (RSI), and Moving Average Convergence Divergence (MACD).
- **Algorithmic Signals**: Deterministic trading strategy that processes historical data to emit strict `BUY`, `SELL`, or `HOLD` action signals.
- **Paper Trading Engine**: A robust simulated execution environment with order matching, slippage/fee estimation, SQLite persistence, and risk management (position sizing, stop-loss, and take-profit checks).
- **Portfolio & P&L Tracking**: Live monitoring of Available Cash, Total Portfolio Value, Open Positions, and Realized P&L.
- **Autonomous Paper Bot**: An async background execution loop that continuously polls the strategy and places simulated trades autonomously based on emitted signals.
- **Bot Observability**: Granular visibility into the autonomous bot's internal state—including next scheduled check, emitted signals, execution errors, and last executed action.
- **Historical Backtesting**: A built-in backtesting engine allowing users to simulate the trading strategy over historical datasets to analyze hypothetical drawdowns, win rates, and P&L curves.
- **AI Assistant**: A floating, context-aware AI chat widget powered by Groq (Llama) that can analyze the current portfolio, explain why a specific signal was triggered, and answer technical analysis questions.
- **Automated Tests**: A robust backend test suite (`pytest` + `pytest-asyncio`) verifying core logic, market data mocking, and paper-trading mechanics.

---

## Screenshots

![Dashboard](screenshots/dashboard.png)

![Bot Observability](screenshots/bot.png)

![Backtesting Engine](screenshots/backtest.png)

![AI Assistant](screenshots/ai-assistant.png)

---

## Technologies Used

**Backend (Python):**
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance async API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for SQLite database interactions
- [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/) - Data structures for indicator math and market analysis
- [Groq](https://groq.com/) - High-speed LLM inference provider for the AI Assistant
- [Pytest](https://docs.pytest.org/) - Framework for backend unit and integration testing

**Frontend (TypeScript):**
- [React](https://react.dev/) - UI Library
- [Vite](https://vitejs.dev/) - Frontend tooling and bundler
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework for layout and styling
- [Recharts](https://recharts.org/) - Composable charting library for historical price trends
- [Lucide React](https://lucide.dev/) - Beautiful, consistent icon set

---

## Architecture

The system is separated into a decoupled REST API backend and a React Single Page Application (SPA).

1. **Market Data Layer**: Connects to the Twelve Data REST API. Utilizes a global memory cache with a TTL to prevent redundant requests across dashboard polls and the bot loop.
2. **Strategy Engine**: Pure deterministic functions that ingest pandas DataFrames and output actionable signals with descriptive reasoning.
3. **Execution Layer**:
   - **Manual Orders**: Users can manually buy/sell via the dashboard UI.
   - **Autonomous Bot**: An `asyncio` background task checks market conditions every 60 seconds and interfaces directly with the `PaperTrader` to execute strategy logic.
4. **Data Persistence**: A local SQLite database managed by SQLAlchemy stores complete historical logs of `Orders`, `Trades`, and active `Positions`.
5. **AI Layer**: Securely routes frontend prompts through the FastAPI backend to Groq. The backend injects raw system context (current portfolio state, open positions, active signals) into the system prompt to ground the AI's responses.

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Twelve Data API Key](https://twelvedata.com/) (Free tier is supported)
- [Groq API Key](https://console.groq.com/keys) (For the AI Assistant)

### 1. Environment Setup

Copy the example environment variables and add your API keys.

```bash
cp .env.example .env
```

Ensure `.env` contains:
```env
TWELVE_DATA_API_KEY=your_real_key
GROQ_API_KEY=your_real_key
AI_MODEL=openai/gpt-oss-120b
```

*(Note: API keys must never be committed to version control).*

### 2. Run the Backend

Navigate to the project root, set up your virtual environment, install dependencies, and run the FastAPI server.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start the API server
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run the Frontend

In a new terminal window, navigate to the frontend directory, install dependencies, and start Vite.

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` (or the port Vite outputs) in your browser.

### 4. Running Tests

To verify the backend logic:
```bash
source .venv/bin/activate
pytest -q
```

---

## Limitations & Future Scope

- **Paper Trading Only**: This system does not include broker integrations (e.g., Alpaca, Interactive Brokers) for live execution.
- **Quota Constraints**: The free tier of Twelve Data has strict rate limits. The application heavily utilizes caching to protect against `HTTP 429` errors, but aggressively trading multiple volatile symbols simultaneously may exhaust the quota.
- **Persistence**: Currently utilizes SQLite. For a production deployment with high-frequency ticks, migrating to PostgreSQL or a time-series database (like TimescaleDB) would be necessary.
- **Single Strategy**: The deterministic strategy logic is currently hardcoded for technical indicators. A plugin architecture could be introduced in the future to support dynamically swappable trading algorithms.
