import React, { useState } from 'react';
import { apiClient } from '../api/client';
import { Bot, Send } from 'lucide-react';

interface Props {
  symbol: string;
}

export const AIPanel: React.FC<Props> = ({ symbol }) => {
  const [messages, setMessages] = useState<{role: 'user' | 'ai', text: string}[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text }]);
    setInput('');
    setLoading(true);
    try {
      const res = await apiClient.chatAi(text, symbol);
      setMessages(prev => [...prev, { role: 'ai', text: res.reply }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'ai', text: `Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickPrompt = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="bg-[#151924] rounded-xl border border-[#232833] flex flex-col h-[500px]">
      <div className="p-4 border-b border-[#232833] flex justify-between items-center">
        <h3 className="font-semibold text-gray-300 flex items-center">
          <Bot className="w-4 h-4 mr-2 text-indigo-500" /> AI Assistant
        </h3>
        <span className="text-xs bg-indigo-500/20 text-indigo-400 px-2 py-1 rounded">Groq Llama-3</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-gray-500 text-sm flex flex-col items-center justify-center h-full space-y-4">
            <p>Ask me to analyze the market or explain your portfolio.</p>
            <div className="flex flex-wrap justify-center gap-2">
              {['Explain the current signal', 'Why is my portfolio down?', 'Explain RSI and MACD'].map(p => (
                <button key={p} onClick={() => handleQuickPrompt(p)} className="text-xs bg-[#232833] hover:bg-[#2d3342] text-gray-300 px-3 py-2 rounded-full transition-colors">
                  {p}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-lg p-3 text-sm flex gap-3 ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-[#232833] text-gray-200'}`}>
              {m.role === 'ai' && <Bot className="w-4 h-4 shrink-0 mt-0.5 text-indigo-400" />}
              <div className="whitespace-pre-wrap">{m.text}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-[#232833] text-gray-400 rounded-lg p-3 text-sm flex items-center">
              <Bot className="w-4 h-4 mr-2 animate-pulse" /> Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-[#232833]">
        <form onSubmit={(e) => { e.preventDefault(); sendMessage(input); }} className="flex relative">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask about strategy or portfolio..."
            className="w-full bg-[#0b0e14] border border-[#232833] rounded-lg pl-4 pr-12 py-3 text-sm text-white focus:outline-none focus:border-indigo-500"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="absolute right-2 top-2 p-1.5 text-gray-400 hover:text-indigo-500 disabled:opacity-50 transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
