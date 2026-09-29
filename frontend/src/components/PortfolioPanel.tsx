import React from 'react';
import type { PortfolioResponse } from '../types/api';
import { Wallet, TrendingUp, TrendingDown, Briefcase } from 'lucide-react';

interface Props {
  portfolio: PortfolioResponse | null;
}

export const PortfolioPanel: React.FC<Props> = ({ portfolio }) => {
  if (!portfolio) return <div className="p-4 bg-[#151924] rounded-xl border border-[#232833] animate-pulse h-32"></div>;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="p-4 bg-[#151924] rounded-xl border border-[#232833]">
        <div className="text-gray-400 text-sm flex items-center mb-2">
          <Briefcase className="w-4 h-4 mr-2" /> Portfolio Value
        </div>
        <div className="text-2xl font-semibold">${portfolio.portfolio_value.toFixed(2)}</div>
      </div>
      <div className="p-4 bg-[#151924] rounded-xl border border-[#232833]">
        <div className="text-gray-400 text-sm flex items-center mb-2">
          <Wallet className="w-4 h-4 mr-2" /> Available Cash
        </div>
        <div className="text-2xl font-semibold">${portfolio.cash.toFixed(2)}</div>
      </div>
      <div className="p-4 bg-[#151924] rounded-xl border border-[#232833]">
        <div className="text-gray-400 text-sm flex items-center mb-2">
          {portfolio.total_return >= 0 ? <TrendingUp className="w-4 h-4 mr-2 text-emerald-500" /> : <TrendingDown className="w-4 h-4 mr-2 text-rose-500" />} 
          Total Return
        </div>
        <div className={`text-2xl font-semibold ${portfolio.total_return >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
          {portfolio.total_return > 0 ? '+' : ''}{portfolio.total_return.toFixed(2)}%
        </div>
      </div>
      <div className="p-4 bg-[#151924] rounded-xl border border-[#232833]">
        <div className="text-gray-400 text-sm flex items-center mb-2">
          Realized P&L
        </div>
        <div className={`text-2xl font-semibold ${portfolio.realized_pnl >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
          ${portfolio.realized_pnl.toFixed(2)}
        </div>
      </div>
    </div>
  );
};
