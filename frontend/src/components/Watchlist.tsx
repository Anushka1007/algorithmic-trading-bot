import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { SignalResponse, Quote } from '../types/api';

const WATCHLIST_SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];

export const Watchlist: React.FC<{ onSelect: (sym: string) => void }> = ({ onSelect }) => {
  const [data, setData] = useState<Record<string, { quote?: Quote, signal?: SignalResponse }>>({});
  
  useEffect(() => {
    const fetchAll = async () => {
      for (const sym of WATCHLIST_SYMBOLS) {
        try {
          const [q, s] = await Promise.all([
            apiClient.getQuote(sym),
            apiClient.getSignal(sym)
          ]);
          setData(prev => ({ ...prev, [sym]: { quote: q, signal: s } }));
        } catch (e) {
          // Ignore failed symbols
        }
      }
    };
    fetchAll();
  }, []);

  return (
    <div className="bg-[#151924] rounded-xl border border-[#232833] overflow-hidden">
      <div className="p-4 border-b border-[#232833]">
        <h3 className="font-semibold text-gray-300">Watchlist</h3>
      </div>
      <div className="divide-y divide-[#232833]">
        {WATCHLIST_SYMBOLS.map(sym => {
          const item = data[sym];
          return (
            <button 
              key={sym}
              onClick={() => onSelect(sym)}
              className="w-full px-4 py-3 flex items-center justify-between hover:bg-[#1a1f2e] transition-colors text-left"
            >
              <div className="font-semibold text-gray-200">{sym}</div>
              <div className="flex items-center gap-4">
                <div className="font-mono text-gray-300">
                  {item?.quote ? `$${item.quote.price.toFixed(2)}` : '...'}
                </div>
                <div className={`text-xs font-bold px-2 py-1 rounded w-16 text-center ${
                  item?.signal?.signal === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 
                  item?.signal?.signal === 'SELL' ? 'bg-rose-500/10 text-rose-500' : 
                  'bg-gray-500/10 text-gray-400'
                }`}>
                  {item?.signal?.signal || '-'}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  );
};
