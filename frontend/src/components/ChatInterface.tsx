'use client';

/**
 * Main Chat Interface Component
 * Real-time chat with RAG Mutual Funds bot
 * Enhanced with financial-themed design and animated background
 */
import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage, receiveResponse, chatError, clearChat } from '../lib/store';
import { ApiService } from '../lib/api';
import { Send, Bot, User, Trash2, ExternalLink, Loader2, BarChart3, DollarSign, Lock } from 'lucide-react';
import type { RootState, AppDispatch } from '../lib/store';

export default function ChatInterface() {
  const dispatch = useDispatch<AppDispatch>();
  const messages = useSelector((state: RootState) => state.chat.messages);
  const isLoading = useSelector((state: RootState) => state.chat.isLoading);
  const [input, setInput] = useState('');
  const [metadata, setMetadata] = useState<{ last_updated: string | null; vector_db_count: number | null } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch metadata on component mount
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const meta = await ApiService.getMetadata();
        setMetadata({
          last_updated: meta.last_updated,
          vector_db_count: meta.vector_db_count
        });
      } catch (error) {
        console.error('Failed to fetch metadata:', error);
      }
    };
    
    fetchMetadata();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const question = input.trim();
    setInput('');
    dispatch(sendMessage(question));

    try {
      const response = await ApiService.submitQuery(question, 5, true);
      
      dispatch(receiveResponse({
        answer: response.answer,
        citation: response.citation,
        confidence: response.confidence,
        chunks_retrieved: response.chunks_retrieved,
      }));
    } catch (error: any) {
      dispatch(chatError(error.message || 'Failed to get response'));
    }
  };

  const handleClearChat = () => {
    if (confirm('Are you sure you want to clear the conversation?')) {
      dispatch(clearChat());
    }
  };

  return (
    <div className="flex flex-col h-screen financial-bg relative">
      {/* Animated Financial Symbols Background */}
      <div className="financial-symbols">
        <span className="financial-symbol" style={{ top: '10%', left: '5%' }}>$</span>
        <span className="financial-symbol" style={{ top: '20%', left: '15%' }}>€</span>
        <span className="financial-symbol" style={{ top: '15%', left: '25%' }}>%</span>
        <span className="financial-symbol" style={{ top: '25%', left: '35%' }}>₹</span>
        <span className="financial-symbol" style={{ top: '12%', left: '45%' }}>¥</span>
        <span className="financial-symbol" style={{ top: '22%', left: '55%' }}>£</span>
        <span className="financial-symbol" style={{ top: '18%', left: '65%' }}>¢</span>
        <span className="financial-symbol" style={{ top: '28%', left: '75%' }}>₽</span>
        <span className="financial-symbol" style={{ top: '14%', left: '85%' }}>₩</span>
        <span className="financial-symbol" style={{ top: '8%', left: '95%' }}>₿</span>
        
        <span className="financial-symbol" style={{ top: '40%', left: '8%' }}>📈</span>
        <span className="financial-symbol" style={{ top: '45%', left: '18%' }}>💰</span>
        <span className="financial-symbol" style={{ top: '42%', left: '28%' }}>📊</span>
        <span className="financial-symbol" style={{ top: '48%', left: '38%' }}>💵</span>
        <span className="financial-symbol" style={{ top: '44%', left: '48%' }}>🏦</span>
        <span className="financial-symbol" style={{ top: '46%', left: '58%' }}>📉</span>
        <span className="financial-symbol" style={{ top: '41%', left: '68%' }}>💎</span>
        <span className="financial-symbol" style={{ top: '47%', left: '78%' }}>🪙</span>
        <span className="financial-symbol" style={{ top: '43%', left: '88%' }}>💹</span>
        
        <span className="financial-symbol" style={{ top: '65%', left: '12%' }}>ETF</span>
        <span className="financial-symbol" style={{ top: '68%', left: '22%' }}>SIP</span>
        <span className="financial-symbol" style={{ top: '62%', left: '32%' }}>NAV</span>
        <span className="financial-symbol" style={{ top: '70%', left: '42%' }}>CAGR</span>
        <span className="financial-symbol" style={{ top: '66%', left: '52%' }}>ROI</span>
        <span className="financial-symbol" style={{ top: '64%', left: '62%' }}>AUM</span>
        <span className="financial-symbol" style={{ top: '69%', left: '72%' }}>XIRR</span>
        <span className="financial-symbol" style={{ top: '67%', left: '82%' }}>DP</span>
        
        <span className="financial-symbol" style={{ top: '85%', left: '10%' }}>+</span>
        <span className="financial-symbol" style={{ top: '88%', left: '20%' }}>−</span>
        <span className="financial-symbol" style={{ top: '82%', left: '30%' }}>×</span>
        <span className="financial-symbol" style={{ top: '90%', left: '40%' }}>÷</span>
        <span className="financial-symbol" style={{ top: '86%', left: '50%' }}>=</span>
        <span className="financial-symbol" style={{ top: '84%', left: '60%' }}>↑</span>
        <span className="financial-symbol" style={{ top: '89%', left: '70%' }}>↓</span>
        <span className="financial-symbol" style={{ top: '87%', left: '80%' }}>→</span>
        <span className="financial-symbol" style={{ top: '83%', left: '90%' }}>↗</span>
      </div>

      {/* Header */}
      <header className="glass-effect border-b border-blue-500/20 relative z-10">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Mutual Fund Assistant
              </h1>
              <p className="text-xs text-blue-300/70">Your Intelligent Investment Companion</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {metadata?.last_updated && (
              <div className="hidden sm:flex items-center gap-2 text-xs text-blue-200/80 bg-blue-900/30 px-3 py-2 rounded-xl border border-blue-500/20 backdrop-blur-sm">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span>{new Date(metadata.last_updated).toLocaleDateString()}</span>
              </div>
            )}
            {metadata?.vector_db_count !== undefined && metadata.vector_db_count !== null && (
              <div className="hidden sm:flex items-center gap-2 text-xs text-blue-200/80 bg-blue-900/30 px-3 py-2 rounded-xl border border-blue-500/20 backdrop-blur-sm">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>{metadata.vector_db_count} docs</span>
              </div>
            )}
            <button
              onClick={handleClearChat}
              className="flex items-center gap-2 px-3 py-2 text-xs text-red-300/80 hover:text-red-400 hover:bg-red-900/30 transition-all rounded-xl border border-transparent hover:border-red-500/20"
              title="Clear conversation"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <main className="flex-1 overflow-y-auto relative z-10">
        <div className="max-w-3xl mx-auto px-4 py-8">
          {messages.length === 0 ? (
            <div className="text-center py-16">
              {/* Welcome Header */}
              <div className="mb-12">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 via-purple-600 to-cyan-500 mx-auto mb-6 flex items-center justify-center shadow-2xl shadow-blue-500/40 animate-pulse">
                  <Bot className="w-12 h-12 text-white" />
                </div>
                <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent mb-3">
                  Welcome to your Mutual Fund Assistant
                </h2>
                <p className="text-lg text-blue-200/60 max-w-md mx-auto">
                  Get instant answers about mutual funds, SIPs, expense ratios, and more
                </p>
              </div>
              
              {/* Sample Questions */}
              <div className="space-y-4 max-w-2xl mx-auto mb-8">
                <button
                  onClick={() => setInput("What's the expense ratio of HDFC ELSS?")}
                  className="w-full p-4 text-left glass-effect rounded-2xl hover:bg-blue-900/40 hover:border-blue-400/40 transition-all group gradient-border"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg group-hover:shadow-blue-500/50 transition-shadow">
                      <BarChart3 className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-base text-blue-50 group-font-medium">What's the expense ratio of HDFC ELSS?</span>
                  </div>
                </button>

                <button
                  onClick={() => setInput("Show SIP options for small cap funds")}
                  className="w-full p-4 text-left glass-effect rounded-2xl hover:bg-purple-900/40 hover:border-purple-400/40 transition-all group gradient-border"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg group-hover:shadow-purple-500/50 transition-shadow">
                      <DollarSign className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-base text-purple-50 group-font-medium">Show SIP options for small cap funds</span>
                  </div>
                </button>

                <button
                  onClick={() => setInput("Is there any lock-in period?")}
                  className="w-full p-4 text-left glass-effect rounded-2xl hover:bg-cyan-900/40 hover:border-cyan-400/40 transition-all group gradient-border"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center flex-shrink-0 shadow-lg group-hover:shadow-cyan-500/50 transition-shadow">
                      <Lock className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-base text-cyan-50 group-font-medium">Is there any lock-in period?</span>
                  </div>
                </button>
              </div>

              {/* Disclaimer */}
              <div className="mt-8 p-4 rounded-xl bg-blue-900/20 border border-blue-500/10 backdrop-blur-sm max-w-md mx-auto">
                <p className="text-xs text-blue-300/70">
                  💡 Facts-only information. Not investment advice.
                </p>
              </div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 mb-6 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/30">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                )}
                
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-600/30'
                      : 'glass-effect border border-blue-500/20 text-slate-100 backdrop-blur-sm'
                  }`}
                >
                  {message.role === 'assistant' && message.citation ? (
                    <>
                      {/* Answer Section */}
                      <div className="mb-4 pb-4 border-b border-blue-500/20">
                        <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                      </div>
                      
                      {/* Source Information */}
                      <div className="bg-blue-900/30 rounded-xl p-3 border border-blue-500/20 backdrop-blur-sm">
                        <div className="flex items-start gap-3">
                          <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                          </svg>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-blue-400 mb-2">Source Document</p>
                            <a
                              href={message.citation}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs text-blue-200/80 hover:text-blue-300 break-all transition-colors flex items-center gap-2 group"
                            >
                              <span className="truncate">{message.citation}</span>
                              <ExternalLink className="w-3.5 h-3.5 group-hover:text-blue-400 transition-colors" />
                            </a>
                          </div>
                        </div>
                      </div>
                    </>
                  ) : (
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
                  )}
                </div>

                {message.role === 'user' && (
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-600 to-slate-700 flex items-center justify-center flex-shrink-0 shadow-lg">
                    <User className="w-5 h-5 text-slate-200" />
                  </div>
                )}
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex gap-3 justify-start mb-6">
              <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center backdrop-blur-sm border border-blue-500/30">
                <Bot className="w-6 h-6 text-blue-400 animate-pulse" />
              </div>
              <div className="glass-effect border border-blue-500/20 rounded-2xl px-4 py-3 backdrop-blur-sm">
                <div className="flex items-center gap-3 text-blue-300 text-sm">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="font-medium">Processing your query...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="glass-effect border-t border-blue-500/20 relative z-10 backdrop-blur-lg">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about mutual funds, SIPs, NAV, or any investment query..."
              className="flex-1 px-4 py-3.5 bg-blue-900/30 border border-blue-500/30 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 text-slate-100 placeholder-blue-300/40 text-sm backdrop-blur-sm transition-all"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-6 py-3.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-blue-600/30 hover:shadow-blue-600/50 flex items-center gap-2 font-medium"
            >
              <Send className="w-5 h-5" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
          <p className="mt-3 text-xs text-blue-300/50 text-center flex items-center justify-center gap-1">
            <span>⚠️</span>
            <span>Facts-only information. Not investment advice. Please consult a SEBI registered advisor before investing.</span>
          </p>
        </form>
      </footer>
    </div>
  );
}
