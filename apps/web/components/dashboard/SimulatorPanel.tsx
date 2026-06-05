"use client";

import React, { useState, useEffect, memo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, RefreshCw, TrendingUp, AlertCircle } from 'lucide-react';
import api from '@/lib/api';
import { useSession } from 'next-auth/react';

// 🚀 Optimized Slider Component
const AllocationSlider = memo(({ assetName, symbol, quantity, originalQuantity, onCommit }: {
    assetName: string,
    symbol: string,
    quantity: number,
    originalQuantity: number,
    onCommit: (val: number) => void
}) => {
    const [localValue, setLocalValue] = useState(quantity);

    // Sync local state when external quantity changes (e.g. after simulation or reset)
    useEffect(() => {
        setLocalValue(quantity);
    }, [quantity]);

    // Use originalQuantity for a stable max to prevent the "jumping scale" feeling
    const sliderMax = Math.max(originalQuantity * 3, 100);

    return (
        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
            <div className="flex justify-between mb-2 text-[11px] uppercase tracking-wider text-gray-500 font-bold">
                <span className="text-white">{assetName}</span>
                <span className="font-mono text-cyan-400">{localValue} units</span>
            </div>
            <input
                type="range"
                min="0"
                max={sliderMax}
                step="1"
                value={localValue}
                onChange={(e) => setLocalValue(parseInt(e.target.value))}
                onMouseUp={() => onCommit(localValue)}
                onTouchEnd={() => onCommit(localValue)}
                className="w-full h-1.5 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />
            <div className="flex justify-between mt-1 text-[9px] text-gray-600 font-mono">
                <span>0</span>
                <span>{sliderMax}</span>
            </div>
        </div>
    );
});

AllocationSlider.displayName = "AllocationSlider";

function MetricBox({ label, original, simulated, format, inverse = false }: any) {
    if (original === undefined) return null;

    let isBetter = false;
    let diff = 0;

    if (simulated !== undefined && simulated !== null) {
        diff = simulated - original;
        if (inverse) {
            isBetter = diff < 0;
        } else {
            isBetter = diff > 0;
        }
    }

    return (
        <div className="bg-white/5 p-4 rounded-xl border border-white/5">
            <span className="text-[10px] text-gray-500 font-bold uppercase tracking-tight block mb-1">{label}</span>
            <div className="flex items-baseline gap-2">
                <span className="text-lg font-bold text-white">{format(original)}</span>
                {simulated !== null && simulated !== undefined && Math.abs(diff) > 0.0001 && (
                    <span className={`text-xs font-bold flex items-center ${isBetter ? "text-emerald-400" : "text-rose-400"}`}>
                        → {format(simulated)}
                    </span>
                )}
            </div>
        </div>
    );
}

interface SimulatorProps {
    isOpen: boolean;
    onClose: () => void;
    holdings: any[];
    setHoldings: React.Dispatch<React.SetStateAction<any[]>>;
    currentMetrics: any;
    onSimulate?: (results: any) => void;
}

import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, Cell, Legend } from 'recharts';

export default function SimulatorPanel({ isOpen, onClose, holdings, setHoldings, currentMetrics, onSimulate }: SimulatorProps) {
    const { data: session } = useSession();
    const [originalQuantities, setOriginalQuantities] = useState<Record<string, number>>({});
    const [originalPrices, setOriginalPrices] = useState<Record<string, number>>({});
    const [originalAllocation, setOriginalAllocation] = useState<any[]>([]);
    const [simulatedMetrics, setSimulatedMetrics] = useState<any>(null);
    const [simulatedAllocation, setSimulatedAllocation] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [dirty, setDirty] = useState(false);

    // Initialize original reference data once when holdings are first loaded
    useEffect(() => {
        if (holdings.length > 0 && Object.keys(originalQuantities).length === 0) {
            const qtyMap: Record<string, number> = {};
            const priceMap: Record<string, number> = {};
            const allocMap: Record<string, number> = {};

            holdings.forEach(h => {
                qtyMap[h.symbol] = h.quantity;
                priceMap[h.symbol] = h.quantity > 0 ? h.current_value / h.quantity : 0;

                let label = "Others";
                if (h.asset_type === "STOCK") label = "Equity";
                else if (h.asset_type === "ETF" || h.account_type === "DEMAT") label = "Mutual Funds (Demat)";
                else if (h.asset_type === "MF") label = "Mutual Funds (SOA)";

                allocMap[label] = (allocMap[label] || 0) + h.current_value;
            });

            setOriginalQuantities(qtyMap);
            setOriginalPrices(priceMap);
            setOriginalAllocation(Object.entries(allocMap).map(([name, value]) => ({ name, value })));
        }
    }, [holdings, originalQuantities]);

    const handleQuantityChange = useCallback((symbol: string, newQty: number) => {
        setHoldings(prev => prev.map(h => {
            if (h.symbol === symbol) {
                const price = originalPrices[symbol] || 0;
                return {
                    ...h,
                    quantity: newQty,
                    current_value: newQty * price
                };
            }
            return h;
        }));
        setDirty(true);
    }, [originalPrices, setHoldings]);

    const runSimulation = async () => {
        const token = (session as any)?.accessToken;
        if (!token) {
            setError("No active session. Please log in again.");
            return;
        }

        setLoading(true);
        setError(null);

        try {
            const validHoldings = holdings.filter(h => !isNaN(h.quantity) && h.quantity >= 0);
            const response = await api.post('/api/analytics/simulate', validHoldings, {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.data?.metrics) {
                setSimulatedMetrics(response.data.metrics);
                setSimulatedAllocation(response.data.allocation || []);
                setDirty(false);
                if (onSimulate) onSimulate({ ...response.data, holdings: validHoldings });
                // We no longer auto-close! Stay open for more edits.
            } else {
                throw new Error("Invalid response from server");
            }
        } catch (err: any) {
            console.error("Simulation failed:", err);
            setError(err.response?.data?.detail || err.message || "Simulation failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    // Prepare data for the comparison chart
    const comparisonData = originalAllocation.map(orig => {
        const sim = simulatedAllocation.find(a => a.name === orig.name);
        const totalOrig = originalAllocation.reduce((sum, a) => sum + a.value, 0);
        const totalSim = simulatedAllocation.reduce((sum, a) => sum + a.value, 0);

        return {
            name: orig.name,
            original: totalOrig > 0 ? (orig.value / totalOrig) * 100 : 0,
            simulated: totalSim > 0 ? ((sim?.value || 0) / totalSim) * 100 : 0
        };
    });

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop removed for "Drawer" feel - user can see dashboard charts */}
                    <motion.div
                        initial={{ x: "100%", opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: "100%" }}
                        transition={{ type: "spring", damping: 30, stiffness: 300 }}
                        className="fixed inset-y-0 right-0 w-full max-w-md bg-[#020617] border-l border-white/10 shadow-2xl z-[70] flex flex-col"
                    >
                        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                            <div>
                                <hgroup>
                                    <h2 className="text-xl font-black text-white flex items-center gap-2">
                                        <RefreshCw className={`w-5 h-5 text-cyan-400 ${loading ? 'animate-spin' : ''}`} />
                                        Portfolio Simulator
                                    </h2>
                                    <p className="text-[10px] font-mono text-gray-500 uppercase tracking-widest mt-1">What-If Intelligence Engine</p>
                                </hgroup>
                            </div>
                            <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-all">
                                <X size={20} />
                            </button>
                        </div>

                        <div className="flex-1 overflow-y-auto p-6 space-y-8">
                            {error && (
                                <motion.div
                                    initial={{ opacity: 0, y: -10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex gap-3 items-start"
                                >
                                    <AlertCircle className="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
                                    <p className="text-xs text-rose-200 leading-relaxed font-medium">{error}</p>
                                </motion.div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <MetricBox
                                    label="Sharpe Ratio"
                                    original={currentMetrics?.sharpe_ratio}
                                    simulated={simulatedMetrics?.sharpe_ratio}
                                    format={(v: number) => v.toFixed(2)}
                                />
                                <MetricBox
                                    label="Annual Volatility"
                                    original={currentMetrics?.annual_volatility}
                                    simulated={simulatedMetrics?.annual_volatility}
                                    format={(v: number) => `${(v * 100).toFixed(1)}%`}
                                    inverse={true}
                                />
                            </div>

                            {/* Weight Comparison Chart */}
                            {simulatedAllocation.length > 0 && (
                                <div className="bg-white/[0.03] border border-white/5 rounded-2xl p-4">
                                    <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-4">Weight Shift (%)</h3>
                                    <div className="h-[180px] w-full">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={comparisonData} layout="vertical" margin={{ left: -10, right: 20 }}>
                                                <XAxis type="number" hide />
                                                <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 10 }} width={80} />
                                                <RechartsTooltip
                                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', fontSize: '10px' }}
                                                    formatter={(v: any) => [`${parseFloat(v).toFixed(1)}%`]}
                                                />
                                                <Legend iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
                                                <Bar dataKey="original" name="Current" fill="#475569" radius={[0, 4, 4, 0]} barSize={8} />
                                                <Bar dataKey="simulated" name="Simulated" fill="#22d3ee" radius={[0, 4, 4, 0]} barSize={8} />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            )}

                            <div className="space-y-4">
                                <h3 className="text-[10px] font-black text-gray-500 uppercase tracking-[0.2em]">Adjust Holdings</h3>
                                <div className="space-y-4">
                                    {holdings.map((h) => (
                                        <AllocationSlider
                                            key={h.symbol}
                                            assetName={h.asset_name}
                                            symbol={h.symbol}
                                            quantity={h.quantity}
                                            originalQuantity={originalQuantities[h.symbol] || 0}
                                            onCommit={(newQty) => handleQuantityChange(h.symbol, newQty)}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="p-6 border-t border-white/5 bg-white/[0.01]">
                            <button
                                onClick={runSimulation}
                                disabled={loading || !dirty}
                                className={`w-full py-4 rounded-2xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-3 transition-all duration-300 shadow-xl ${dirty && !loading
                                    ? "bg-cyan-500 text-black hover:bg-cyan-400 shadow-cyan-500/20 active:scale-[0.98]"
                                    : "bg-white/5 text-gray-600 cursor-not-allowed border border-white/5"
                                    }`}
                            >
                                {loading ? <RefreshCw className="animate-spin w-4 h-4" /> : <TrendingUp className="w-4 h-4" />}
                                {loading ? "Computing Analytics..." : "Run Portfolio Simulation"}
                            </button>
                            <p className="text-[9px] text-gray-600 text-center mt-4 uppercase tracking-tighter">
                                Calculations leverage historical standard dev & mean returns
                            </p>
                        </div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
