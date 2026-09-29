import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { PortfolioResponse, SignalResponse, Quote, HistoricalData, Trade } from '../types/api';
import { PortfolioPanel } from './PortfolioPanel';
import { SignalCard } from './SignalCard';
import { ChartPanel } from './ChartPanel';
import { PaperOrderForm } from './PaperOrderForm';
import { TradesTable } from './TradesTable';
import { BacktestView } from './BacktestView';
import { Watchlist } from './Watchlist';
import { RefreshCw, Search } from 'lucide-react';

export const Dashboard: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [searchInput, setSearchInput] = useState('AAPL');
  const [activeTab, setActiveTab] = useState<'TRADE' | 'BACKTEST'>('TRADE');
  
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [signal, setSignal] = useState<SignalResponse | null>(null);
  const [quote, setQuote] = useState<Quote | null>(null);
  const [history, setHistory] = useState<HistoricalData | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [port, trds, sig, qte, hist] = await Promise.all([
        apiClient.getPortfolio(),
        apiClient.getTrades(),
        apiClient.getSignal(symbol),
        apiClient.getQuote(symbol),
        apiClient.getHistory(symbol)
      ]);
      setPortfolio(port);
      setTrades(trds);
      setSignal(sig);
      setQuote(qte);
      setHistory(hist);
      setLastUpdated(new Date());
    } catch (err: any) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [symbol]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      setSymbol(searchInput.trim().toUpperCase());
    }
  };

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">Algorithmic Trading Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1 flex items-center">
            Last updated: {lastUpdated.toLocaleTimeString()} 
            <button onClick={fetchData} className="ml-3 hover:text-white transition-colors">
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </p>
        </div>

        <div className="flex gap-4 w-full md:w-auto">
          <div className="flex bg-[#151924] rounded-lg border border-[#232833] p-1">
            <button 
              className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${activeTab === 'TRADE' ? 'bg-[#232833] text-white' : 'text-gray-400 hover:text-gray-200'}`}
              onClick={() => setActiveTab('TRADE')}
            >
              Trade
            </button>
            <button 
              className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${activeTab === 'BACKTEST' ? 'bg-[#232833] text-white' : 'text-gray-400 hover:text-gray-200'}`}
              onClick={() => setActiveTab('BACKTEST')}
            >
              Backtest
            </button>
          </div>
          <form onSubmit={handleSearch} className="relative flex-1 md:w-64">
            <input 
              type="text" 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="w-full bg-[#151924] border border-[#232833] rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-indigo-500 transition-colors"
              placeholder="Symbol (e.g. MSFT)"
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
          </form>
        </div>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-4 rounded-lg">
          {error}
        </div>
      )}

      {activeTab === 'TRADE' ? (
        <>
          <PortfolioPanel portfolio={portfolio} />
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <Watchlist onSelect={(s) => { setSymbol(s); setSearchInput(s); }} />
            </div>
            
            <div className="lg:col-span-2 space-y-6">
              <ChartPanel history={history} />
              <TradesTable trades={trades} />
            </div>

            <div className="lg:col-span-1 space-y-6 flex flex-col h-full">
              <SignalCard signal={signal} quote={quote} symbol={symbol} />
              <PaperOrderForm symbol={symbol} onOrderSuccess={fetchData} />
            </div>
          </div>
        </>
      ) : (
        <BacktestView />
      )}
    </div>
  );
};
