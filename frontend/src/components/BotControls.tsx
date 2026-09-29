import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { BotStatus } from '../api/client';
import { Play, Square, Activity } from 'lucide-react';

export const BotControls: React.FC = () => {
  const [statusObj, setStatusObj] = useState<BotStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const status = await apiClient.getBotStatus();
      setStatusObj(status);
      setRunning(status.running);
    } catch (e) {
      // Ignore
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    setLoading(true);
    await apiClient.startBot();
    await fetchStatus();
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    await apiClient.stopBot();
    await fetchStatus();
    setLoading(false);
  };

  return (
    <div className="bg-[#151924] rounded-xl border border-[#232833] p-4 flex flex-col gap-4">
      <div>
        <h3 className="font-semibold text-gray-300 flex items-center mb-4">
          <Activity className="w-4 h-4 mr-2" /> Paper Bot Engine
        </h3>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${running ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`}></div>
          <span className="text-sm font-mono text-gray-300">
            STATUS: {running ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>
      </div>

      {statusObj && running && (
        <div className="text-xs text-gray-400 space-y-1.5 bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="flex justify-between"><span>Symbol:</span> <span className="text-white font-mono">{statusObj.symbol}</span></div>
          <div className="flex justify-between"><span>Signal:</span> <span className={`font-bold ${statusObj.signal === 'BUY' ? 'text-emerald-400' : statusObj.signal === 'SELL' ? 'text-rose-400' : 'text-gray-300'}`}>{statusObj.signal}</span></div>
          <div className="flex justify-between"><span>Last Check:</span> <span className="text-white font-mono">{statusObj.last_check || '-'}</span></div>
          <div className="flex justify-between"><span>Next Check:</span> <span className="text-white font-mono">{statusObj.next_check || '-'}</span></div>
          <div className="mt-2 pt-2 border-t border-[#232833]">
            <span className="block mb-1">Action:</span>
            {statusObj.error ? (
              <span className="text-rose-400 break-words font-medium">Error: {statusObj.error}</span>
            ) : (
              <span className="text-emerald-400 break-words font-medium">{statusObj.last_action}</span>
            )}
          </div>
        </div>
      )}
      
      {statusObj && !running && statusObj.last_check && (
        <div className="text-xs text-gray-400 space-y-1.5 bg-[#0b0e14] p-3 rounded-lg border border-[#232833]">
          <div className="flex justify-between"><span>Last Action:</span> <span className="text-white">{statusObj.last_action}</span></div>
          <div className="flex justify-between"><span>Last Check:</span> <span className="text-white font-mono">{statusObj.last_check}</span></div>
        </div>
      )}

      <div>
        {!running ? (
          <button 
            onClick={handleStart}
            disabled={loading}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg font-bold flex items-center justify-center transition-colors"
          >
            <Play className="w-5 h-5 mr-2" /> START BOT
          </button>
        ) : (
          <button 
            onClick={handleStop}
            disabled={loading}
            className="w-full py-3 bg-rose-600 hover:bg-rose-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg font-bold flex items-center justify-center transition-colors"
          >
            <Square className="w-5 h-5 mr-2" /> STOP BOT
          </button>
        )}
      </div>
    </div>
  );
};
