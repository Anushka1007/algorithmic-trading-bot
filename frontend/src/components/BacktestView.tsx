import React, { useState } from 'react';
import { apiClient } from '../api/client';
import type { BacktestResult } from '../types/api';
import { Play } from 'lucide-react';

export const BacktestView: React.FC = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.runBacktest({
        symbol,
        interval: '1day',
        outputsize: 500,
        config: {
          initial_capital: 100000,
          fee_percentage: 0.1,
          slippage_percentage: 0.05
        }
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#151924] rounded-xl border border-[#232833] p-6">
      <div className="flex flex-col md:flex-row gap-6">
        
        {/* Form */}
        <div className="w-full md:w-1/3 space-y-4">
          <h3 className="font-semibold text-gray-300">Run Backtest</h3>
          <form onSubmit={handleRun} className="space-y-4">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Symbol</label>
              <input 
                type="text" 
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                className="w-full bg-[#0b0e14] border border-[#232833] rounded-lg px-3 py-2 text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            
            {error && <div className="text-rose-500 text-xs p-2 bg-rose-500/10 rounded-lg">{error}</div>}
            
            <button 
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold flex items-center justify-center transition-colors disabled:opacity-50"
            >
              {loading ? 'Running...' : <><Play className="w-4 h-4 mr-2" /> Start Backtest</>}
            </button>
          </form>
        </div>

        {/* Results */}
        <div className="w-full md:w-2/3">
          {result ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Total Return</div>
                <div className={`text-xl font-bold ${result.metrics.total_return_percent >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                  {result.metrics.total_return_percent.toFixed(2)}%
                </div>
              </div>
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Win Rate</div>
                <div className="text-xl font-bold text-gray-200">{result.metrics.win_rate_percent.toFixed(1)}%</div>
              </div>
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Total Trades</div>
                <div className="text-xl font-bold text-gray-200">{result.metrics.total_trades}</div>
              </div>
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Max Drawdown</div>
                <div className="text-xl font-bold text-rose-500">-{result.metrics.max_drawdown_percent.toFixed(2)}%</div>
              </div>
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Profit Factor</div>
                <div className="text-xl font-bold text-gray-200">{result.metrics.profit_factor.toFixed(2)}</div>
              </div>
              <div className="bg-[#0b0e14] p-4 rounded-lg border border-[#232833]">
                <div className="text-xs text-gray-400">Sharpe Ratio</div>
                <div className="text-xl font-bold text-gray-200">{result.metrics.sharpe_ratio.toFixed(2)}</div>
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 border border-dashed border-[#232833] rounded-lg">
              Run a backtest to see results
            </div>
          )}
        </div>
        
      </div>
    </div>
  );
};
