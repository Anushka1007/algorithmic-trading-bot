import React from 'react';
import type { Trade } from '../types/api';

interface Props {
  trades: Trade[];
}

export const TradesTable: React.FC<Props> = ({ trades }) => {
  return (
    <div className="bg-[#151924] rounded-xl border border-[#232833] overflow-hidden">
      <div className="p-4 border-b border-[#232833]">
        <h3 className="font-semibold text-gray-300">Recent Trades</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-[#0b0e14] text-gray-400 border-b border-[#232833]">
            <tr>
              <th className="px-4 py-3 font-medium">Time</th>
              <th className="px-4 py-3 font-medium">Symbol</th>
              <th className="px-4 py-3 font-medium">Side</th>
              <th className="px-4 py-3 font-medium text-right">Qty</th>
              <th className="px-4 py-3 font-medium text-right">Price</th>
              <th className="px-4 py-3 font-medium text-right">Fees</th>
              <th className="px-4 py-3 font-medium text-right">P&L</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#232833]">
            {trades.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-gray-500">No trades yet</td>
              </tr>
            ) : (
              trades.slice(0, 10).map((t) => (
                <tr key={t.id} className="hover:bg-[#1a1f2e] transition-colors">
                  <td className="px-4 py-3 text-gray-400">{new Date(t.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                  <td className="px-4 py-3 font-semibold text-gray-200">{t.symbol}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${t.side === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                      {t.side}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-gray-300">{t.quantity}</td>
                  <td className="px-4 py-3 text-right font-mono text-gray-300">${t.price.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-mono text-gray-400">${t.fees.toFixed(2)}</td>
                  <td className={`px-4 py-3 text-right font-mono font-semibold ${t.realized_pnl > 0 ? 'text-emerald-500' : t.realized_pnl < 0 ? 'text-rose-500' : 'text-gray-400'}`}>
                    {t.realized_pnl !== 0 ? (t.realized_pnl > 0 ? '+' : '') + '$' + t.realized_pnl.toFixed(2) : '-'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
