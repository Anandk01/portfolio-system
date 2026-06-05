"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sliders, CheckCircle, ArrowRight, TrendingUp, ShieldCheck, PieChart } from 'lucide-react';
import api from '@/lib/api';
import { useSession } from 'next-auth/react';

export default function OptimizationPanel({ holdings }: { holdings: any[] }) {
    const { data: session } = useSession();
    const [strategy, setStrategy] = useState<"aggressive" | "conservative">("aggressive");
    const [result, setResult] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const runOptimization = async () => {
        if (!holdings || holdings.length < 2) return;
        setLoading(true);
        try {
            // holdings needs to be passed, but we also need to pass the strategy
            // The API expects holdings in body and strategy as query param
            const response = await api.post(`/api/analytics/optimize?strategy=${strategy}`, holdings, {
                headers: { Authorization: `Bearer ${(session as any).accessToken}` }
            });
            setResult(response.data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-bold text-lg flex items-center gap-2">
                        <Sliders className="w-5 h-5 text-purple-400" />
                        AI Suggested Allocation
                    </h3>
                    <p className="text-xs text-gray-500">MPT-based Efficient Frontier Solver</p>
                </div>
            </div>

            {/* Strategy Selection */}
            <div className="grid grid-cols-2 gap-3 mb-6">
                <button
                    onClick={() => { setStrategy("conservative"); setResult(null); }}
                    className={`p-3 rounded-xl border text-left transition ${strategy === "conservative"
                        ? "bg-purple-500/20 border-purple-500/50 text-white"
                        : "bg-white/5 border-white/5 text-gray-400 hover:bg-white/10"
                        }`}
                >
                    <div className="flex items-center gap-2 mb-1">
                        <ShieldCheck className="w-4 h-4" />
                        <span className="font-bold text-sm">Conservative</span>
                    </div>
                    <p className="text-[10px] opacity-70">Minimize Volatility</p>
                </button>

                <button
                    onClick={() => { setStrategy("aggressive"); setResult(null); }}
                    className={`p-3 rounded-xl border text-left transition ${strategy === "aggressive"
                        ? "bg-purple-500/20 border-purple-500/50 text-white"
                        : "bg-white/5 border-white/5 text-gray-400 hover:bg-white/10"
                        }`}
                >
                    <div className="flex items-center gap-2 mb-1">
                        <TrendingUp className="w-4 h-4" />
                        <span className="font-bold text-sm">Aggressive</span>
                    </div>
                    <p className="text-[10px] opacity-70">Maximize Sharpe</p>
                </button>
            </div>

            {/* Action Button */}
            {!result && (
                <button
                    onClick={runOptimization}
                    disabled={loading || holdings.length < 2}
                    className="w-full py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? "Solving Efficient Frontier..." : "Run Optimization"}
                </button>
            )}

            {/* Results */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-white/5 rounded-xl border border-white/10 overflow-hidden"
                    >
                        <div className="p-4 bg-purple-500/10 border-b border-white/5 flex justify-between items-center">
                            <span className="text-xs font-bold text-purple-300 uppercase tracking-widest">AI Suggested Weights</span>
                            <button onClick={() => setResult(null)} className="text-xs text-gray-500 hover:text-white">Reset</button>
                        </div>

                        <div className="p-4 grid grid-cols-2 gap-4">
                            <div>
                                <span className="text-xs text-gray-500 block mb-1">Est. Return</span>
                                <div className="text-lg font-bold text-white">{(result.metrics.expected_return * 100).toFixed(1)}%</div>
                                <span className="text-[10px] text-emerald-400 font-mono">
                                    {result.improvement.return_delta > 0 ? "+" : ""}{(result.improvement.return_delta * 100).toFixed(2)}%
                                </span>
                            </div>
                            <div>
                                <span className="text-xs text-gray-500 block mb-1">Volatility</span>
                                <div className="text-lg font-bold text-white">{(result.metrics.volatility * 100).toFixed(1)}%</div>
                                <span className="text-[10px] text-emerald-400 font-mono">
                                    {result.improvement.volatility_delta > 0 ? "+" : ""}{(result.improvement.volatility_delta * 100).toFixed(2)}%
                                </span>
                            </div>
                        </div>

                        {/* Top Changes */}
                        <div className="p-4 border-t border-white/5 bg-black/20">
                            <h4 className="text-xs font-bold text-gray-400 mb-2">Recommended Weights</h4>
                            <div className="space-y-2 max-h-[150px] overflow-y-auto pr-1 custom-scrollbar">
                                {Object.entries(result.weights).map(([symbol, weight]: [string, any]) => (
                                    <div key={symbol} className="flex justify-between text-sm">
                                        <span className="text-gray-300">{symbol}</span>
                                        <div className="flex items-center gap-2">
                                            <span className="font-mono text-purple-300">{(weight * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="p-3 bg-yellow-500/10 border-t border-yellow-500/20 text-[10px] text-yellow-200/70 text-center">
                            Note: Optimization based on historical data. Does not guarantee future performance.
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
