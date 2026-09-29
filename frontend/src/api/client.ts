import type { 
  Quote, HistoricalData, SignalResponse, PortfolioResponse, 
  OrderRequest, Trade, BacktestRequest, BacktestResult
} from '../types/api';

export interface BotStatus {
  running: boolean;
  symbol: string;
  signal: string;
  last_check: string | null;
  next_check: string | null;
  last_action: string;
  error: string | null;
}

const API_BASE = 'http://localhost:8000/api';

export const apiClient = {
  getQuote: async (symbol: string): Promise<Quote> => {
    const res = await fetch(`${API_BASE}/market/quote/${symbol}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getHistory: async (symbol: string, interval = '1day'): Promise<HistoricalData> => {
    const res = await fetch(`${API_BASE}/market/history/${symbol}?interval=${interval}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getSignal: async (symbol: string): Promise<SignalResponse> => {
    const res = await fetch(`${API_BASE}/signals/${symbol}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getPortfolio: async (): Promise<PortfolioResponse> => {
    const res = await fetch(`${API_BASE}/paper/portfolio`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getTrades: async (): Promise<Trade[]> => {
    const res = await fetch(`${API_BASE}/paper/trades`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  placeOrder: async (order: OrderRequest): Promise<any> => {
    const res = await fetch(`${API_BASE}/paper/orders`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(order)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  resetPaper: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/paper/reset`, { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  runBacktest: async (req: BacktestRequest): Promise<BacktestResult> => {
    const res = await fetch(`${API_BASE}/backtest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req)
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  chatAi: async (message: string, symbol?: string): Promise<{ reply: string }> => {
    const res = await fetch(`${API_BASE}/ai/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, symbol })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  startBot: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/paper/bot/start`, { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  stopBot: async (): Promise<any> => {
    const res = await fetch(`${API_BASE}/paper/bot/stop`, { method: 'POST' });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  getBotStatus: async (): Promise<BotStatus> => {
    const res = await fetch(`${API_BASE}/paper/bot/status`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
};
