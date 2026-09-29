import React from 'react';
import type { SignalResponse, Quote } from '../types/api';
import { Activity } from 'lucide-react';

interface Props {
  signal: SignalResponse | null;
  quote: Quote | null;
  symbol: string;
}

export const SignalCard: React.FC<Props> = ({ signal, quote, symbol }) => {
  if (!signal) return <div className="p-4 bg-[#151924] rounded-xl border border-[#232833] animate-pulse h-64"></div>;

  const signalColor = signal.signal === 'BUY' ? 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20' 
                    : signal.signal === 'SELL' ? 'text-rose-500 bg-rose-500/10 border-rose-500/20'
                    : 'text-gray-400 bg-gray-500/10 border-gray-500/20';

  return (
    <div className="p-6 bg-[#151924] rounded-xl border border-[#232833] flex flex-col h-full">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-xl font-bold">{symbol}</h2>
          <div className="text-3xl font-light mt-1">${quote?.price?.toFixed(2) || '---'}</div>
        </div>
        <div className={`px-4 py-2 rounded-lg border font-bold text-lg ${signalColor}`}>
          {signal.signal}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="text-xs text-gray-400 mb-1">EMA 20</div>
          <div className="font-mono text-sm">{signal.indicators.ema20?.toFixed(2) || '-'}</div>
        </div>
        <div className="bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="text-xs text-gray-400 mb-1">EMA 50</div>
          <div className="font-mono text-sm">{signal.indicators.ema50?.toFixed(2) || '-'}</div>
        </div>
        <div className="bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="text-xs text-gray-400 mb-1">RSI (14)</div>
          <div className="font-mono text-sm">{signal.indicators.rsi?.toFixed(2) || '-'}</div>
        </div>
        <div className="bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="text-xs text-gray-400 mb-1">MACD</div>
          <div className="font-mono text-sm">{signal.indicators.macd?.toFixed(2) || '-'}</div>
        </div>
      </div>

      <div className="mt-auto">
        <div className="flex items-center text-sm text-gray-400 mb-2">
          <Activity className="w-4 h-4 mr-2" /> Analysis Reasoning
        </div>
        <ul className="text-sm space-y-2">
          {signal.reasons.map((r, i) => (
            <li key={i} className="flex items-start">
              <span className="text-indigo-500 mr-2">•</span>
              <span className="text-gray-300">{r}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
