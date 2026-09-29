import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { Send } from 'lucide-react';

interface Props {
  symbol: string;
  onOrderSuccess: () => void;
}

export const PaperOrderForm: React.FC<Props> = ({ symbol, onOrderSuccess }) => {
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiClient.placeOrder({ symbol, side, quantity });
      onOrderSuccess();
    } catch (err: any) {
      setError(err.message || 'Order failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-[#151924] rounded-xl border border-[#232833] flex flex-col h-full">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-semibold text-gray-300 flex items-center">
          <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2 animate-pulse"></span>
          PAPER TRADING
        </h3>
      </div>

      <form onSubmit={handleSubmit} className="flex-1 flex flex-col">
        <div className="flex bg-[#0b0e14] p-1 rounded-lg border border-[#232833] mb-4">
          <button
            type="button"
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-colors ${side === 'BUY' ? 'bg-emerald-500/20 text-emerald-500' : 'text-gray-400 hover:text-gray-200'}`}
            onClick={() => setSide('BUY')}
          >
            BUY
          </button>
          <button
            type="button"
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-colors ${side === 'SELL' ? 'bg-rose-500/20 text-rose-500' : 'text-gray-400 hover:text-gray-200'}`}
            onClick={() => setSide('SELL')}
          >
            SELL
          </button>
        </div>

        <div className="mb-4">
          <label className="block text-xs text-gray-400 mb-1">Symbol</label>
          <input 
            type="text" 
            value={symbol} 
            disabled 
            className="w-full bg-[#0b0e14] border border-[#232833] rounded-lg px-3 py-2 text-gray-300 font-mono text-sm opacity-50 cursor-not-allowed"
          />
        </div>

        <div className="mb-6">
          <label className="block text-xs text-gray-400 mb-1">Quantity</label>
          <input 
            type="number" 
            min="1"
            value={quantity} 
            onChange={(e) => setQuantity(parseInt(e.target.value) || 0)}
            className="w-full bg-[#0b0e14] border border-[#232833] rounded-lg px-3 py-2 text-gray-100 font-mono focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div className="mt-auto">
          {error && <div className="text-rose-500 text-xs mb-3 p-2 bg-rose-500/10 rounded-lg border border-rose-500/20">{error}</div>}
          <button 
            type="submit"
            disabled={loading || quantity <= 0}
            className={`w-full py-3 rounded-lg font-bold flex items-center justify-center transition-colors
              ${side === 'BUY' 
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white disabled:bg-emerald-900 disabled:text-emerald-300/50' 
                : 'bg-rose-600 hover:bg-rose-500 text-white disabled:bg-rose-900 disabled:text-rose-300/50'}`}
          >
            {loading ? 'PROCESSING...' : <><Send className="w-4 h-4 mr-2" /> SUBMIT {side} ORDER</>}
          </button>
        </div>
      </form>
    </div>
  );
};
