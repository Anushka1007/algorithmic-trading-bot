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
    <div className="bg-[#151924] rounded-xl border border-[#232833] p-4 flex flex-col h-full justify-between">
      <div>
        <h3 className="font-semibold text-gray-300 flex items-center mb-4">
          <Activity className="w-4 h-4 mr-2" /> Paper Bot Engine
        </h3>
        <div className="flex items-center space-x-2 mb-4">
          <div className={`w-3 h-3 rounded-full ${running ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`}></div>
          <span className="text-sm font-mono text-gray-300">
            STATUS: {running ? 'RUNNING' : 'STOPPED'}
          </span>
        </div>
      </div>

      <div className="flex gap-2 mt-auto">
        <button 
          onClick={handleStart}
          disabled={running || loading}
          className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg font-bold flex items-center justify-center transition-colors"
        >
          <Play className="w-4 h-4 mr-2" /> Start
        </button>
        <button 
          onClick={handleStop}
          disabled={!running || loading}
          className="flex-1 py-2 bg-rose-600 hover:bg-rose-500 disabled:bg-gray-800 disabled:text-gray-500 text-white rounded-lg font-bold flex items-center justify-center transition-colors"
        >
          <Square className="w-4 h-4 mr-2" /> Stop
        </button>
      </div>
    </div>
  );
};
