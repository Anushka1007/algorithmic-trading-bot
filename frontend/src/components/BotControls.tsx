import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Play, Square, Activity } from 'lucide-react';

export const BotControls: React.FC = () => {
  const [running, setRunning] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const status = await apiClient.getBotStatus();
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
    setRunning(true);
    setLoading(false);
  };

  const handleStop = async () => {
    setLoading(true);
    await apiClient.stopBot();
    setRunning(false);
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
