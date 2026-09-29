import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { HistoricalData } from '../types/api';

interface Props {
  history: HistoricalData | null;
}

export const ChartPanel: React.FC<Props> = ({ history }) => {
  if (!history) return <div className="p-4 bg-[#151924] rounded-xl border border-[#232833] animate-pulse h-[400px]"></div>;

  // Format data for Recharts, taking last 100 candles for clarity
  const data = history.data.slice(-100).map(d => ({
    time: d.datetime.split(' ')[0],
    price: d.close,
  }));

  // Calculate min/max for Y axis scale
  const minPrice = Math.min(...data.map(d => d.price)) * 0.99;
  const maxPrice = Math.max(...data.map(d => d.price)) * 1.01;

  return (
    <div className="p-4 bg-[#151924] rounded-xl border border-[#232833] h-[400px] flex flex-col">
      <h3 className="font-semibold mb-4 text-gray-300">Price History (Last 100 Periods)</h3>
      <div className="flex-1 w-full h-full min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#232833" vertical={false} />
            <XAxis 
              dataKey="time" 
              stroke="#4b5563" 
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(val) => val.substring(5)}
              minTickGap={30}
            />
            <YAxis 
              domain={[minPrice, maxPrice]} 
              stroke="#4b5563" 
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(val) => `$${val.toFixed(0)}`}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#0b0e14', borderColor: '#232833', borderRadius: '0.5rem', color: '#e2e8f0' }}
              itemStyle={{ color: '#e2e8f0' }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#6366f1" 
              strokeWidth={2} 
              dot={false}
              activeDot={{ r: 6, fill: '#6366f1', stroke: '#151924', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
