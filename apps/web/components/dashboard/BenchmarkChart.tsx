"use client";

import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Activity, TrendingUp } from 'lucide-react';
import api from "@/lib/api";
import { useSession } from "next-auth/react";

const RANGES = [
    { label: "1M", value: "1mo" },
    { label: "6M", value: "6mo" },
    { label: "1Y", value: "1y" },
    { label: "2Y", value: "2y" },
];

export default function BenchmarkChart({ holdings }: { holdings?: any[] }) {
    const { data: session } = useSession();
    const [data, setData] = useState<any[]>([]);
    const [range, setRange] = useState("1y");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!(session as any)?.accessToken) return;
            try {
                setLoading(true);
                // Switch to POST to support sending holdings for simulation
                const response = await api.post(`/api/analytics/benchmark?period=${range}`,
                    holdings ? { holdings } : {},
                    { headers: { Authorization: `Bearer ${(session as any).accessToken}` } }
                );
                setData(response.data);
            } catch (error) {
                console.error("Benchmark Error:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [session, range, holdings]);

    if (loading) return <div className="h-[300px] flex items-center justify-center animate-pulse text-gray-600">Loading Benchmark Data...</div>;
    if (!data || data.length === 0) return <div className="h-[300px] flex items-center justify-center text-gray-500 italic">Not enough historical data for comparison.</div>;

    // Calculate final returns for legendary status
    const lastPoint = data[data.length - 1];
    const pfReturn = lastPoint?.Portfolio || 0;
    const niftyReturn = lastPoint?.["NIFTY 50"] || 0;
    const goldReturn = lastPoint?.["GOLD"] || 0;

    return (
        <div className="w-full">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h3 className="font-bold text-lg flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-cyan-400" />
                        Performance vs Benchmarks
                        {holdings && (
                            <span className="ml-2 py-0.5 px-2 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-[9px] text-cyan-400 font-black uppercase tracking-widest animate-pulse">
                                Simulated Scenario
                            </span>
                        )}
                    </h3>
                    <p className="text-xs text-gray-500">Cumulative returns normalized to 0%</p>
                </div>

                <div className="flex bg-white/5 rounded-lg p-1 gap-1">
                    {RANGES.map((r) => (
                        <button
                            key={r.value}
                            onClick={() => setRange(r.value)}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${range === r.value ? "bg-cyan-500 text-black shadow-lg" : "text-gray-400 hover:text-white"
                                }`}
                        >
                            {r.label}
                        </button>
                    ))}
                </div>
            </div>

            <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }} key={range}>
                        <defs>
                            <linearGradient id="colorPf" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorNifty" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#94a3b8" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#94a3b8" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="date"
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { month: 'short', year: '2-digit' })}
                            minTickGap={range === "1mo" ? 15 : range === "6mo" ? 25 : 30}
                            interval="preserveStartEnd"
                        />
                        <YAxis
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => `${val}%`}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                            itemStyle={{ fontSize: '12px' }}
                            formatter={(value: number | undefined) => value !== undefined ? [`${value.toFixed(2)}%`, ''] : ['N/A', '']}
                            labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                        />
                        <Legend verticalAlign="top" height={36} iconType="circle" />

                        <Area
                            type="monotone"
                            dataKey="NIFTY 50"
                            stroke="#94a3b8"
                            strokeDasharray="4 4"
                            strokeWidth={2}
                            fill="url(#colorNifty)"
                            name={`NIFTY 50 (${niftyReturn.toFixed(1)}%)`}
                        />
                        <Area
                            type="monotone"
                            dataKey="GOLD"
                            stroke="#fbbf24"
                            strokeWidth={2}
                            fill="transparent"
                            name={`Gold (${goldReturn.toFixed(1)}%)`}
                        />
                        <Area
                            type="monotone"
                            dataKey="Portfolio"
                            stroke="#22d3ee"
                            strokeWidth={3}
                            fill="url(#colorPf)"
                            name={`Your Portfolio (${pfReturn.toFixed(1)}%)`}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
