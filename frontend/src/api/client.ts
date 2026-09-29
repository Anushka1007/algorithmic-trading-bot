import type { 
  Quote, HistoricalData, SignalResponse, PortfolioResponse, 
  OrderRequest, Trade, BacktestRequest, BacktestResult
} from '../types/api';

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
  }
};
