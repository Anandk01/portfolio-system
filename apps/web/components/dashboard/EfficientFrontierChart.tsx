"use client";

import { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer, Cell, ReferenceDot } from 'recharts';
import { Activity, TrendingUp, Info } from 'lucide-react';
import api from '@/lib/api';
import { useSession } from 'next-auth/react';

export default function EfficientFrontierChart({ holdings }: { holdings: any[] }) {
    const { data: session } = useSession();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!(session as any)?.accessToken || !holdings || holdings.length < 2) return;

            try {
                setLoading(true);
                const response = await api.post('/api/analytics/frontier', holdings, {
                    headers: { Authorization: `Bearer ${(session as any).accessToken}` }
                });
                setData(response.data);
            } catch (e) {
                console.error("Frontier Fetch Error", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [holdings, session]);

    if (loading) return <div className="h-[300px] flex items-center justify-center animate-pulse text-gray-600">Running Monte Carlo Simulation (n=1000)...</div>;
    if (!data || !data.cloud) return <div className="h-[300px] flex items-center justify-center text-gray-500">Insufficient data for Frontier.</div>;

    const { cloud, current, optimized } = data;

    return (
        <div className="w-full">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="font-bold text-lg flex items-center gap-2">
                        <Activity className="w-5 h-5 text-cyan-400" />
                        Efficient Frontier
                    </h3>
                    <p className="text-xs text-gray-500">Risk vs Return Landscape</p>
                </div>
            </div>

            <div className="h-[320px] w-full bg-black/20 rounded-xl border border-white/5 p-2">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                        <XAxis
                            type="number"
                            dataKey="volatility"
                            name="Volatility"
                            unit=""
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                            domain={['auto', 'auto']}
                        />
                        <YAxis
                            type="number"
                            dataKey="return"
                            name="Return"
                            unit=""
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                            domain={['auto', 'auto']}
                        />
                        <Tooltip
                            cursor={{ strokeDasharray: '3 3' }}
                            content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                    const d = payload[0].payload;
                                    return (
                                        <div className="bg-[#0f172a] border border-white/10 p-2 rounded-lg shadow-xl text-xs">
                                            <p className="font-bold text-white mb-1">{d.name || "Simulated Portfolio"}</p>
                                            <div className="space-y-1 text-gray-400">
                                                <div className="flex justify-between gap-4"><span>Return:</span> <span className="text-emerald-400">{(d.return * 100).toFixed(2)}%</span></div>
                                                <div className="flex justify-between gap-4"><span>Volatility:</span> <span className="text-rose-400">{(d.volatility * 100).toFixed(2)}%</span></div>
                                                {d.sharpe && <div className="flex justify-between gap-4"><span>Sharpe:</span> <span className="text-cyan-400">{d.sharpe}</span></div>}
                                            </div>
                                        </div>
                                    );
                                }
                                return null;
                            }}
                        />

                        {/* 1. The Cloud */}
                        <Scatter name="Feasible Set" data={cloud} fill="#475569" opacity={0.3} shape="circle" />

                        {/* 2. Current Portfolio (Cyan Star) */}
                        {current && (
                            <Scatter
                                name="Your Portfolio"
                                data={[{ ...current, name: "Your Current Allocation" }]}
                                fill="#22d3ee"
                                shape="star"
                                legendType="star"
                            >
                                <Cell fill="#22d3ee" />
                            </Scatter>
                        )}

                        {/* 3. Optimized Portfolio (Purple Star) */}
                        {optimized && (
                            <Scatter
                                name="Max Sharpe"
                                data={[{ ...optimized, name: "Maximum Sharpe Portfolio (Historical)" }]}
                                fill="#a855f7"
                                shape="star"
                                legendType="star"
                            >
                                <Cell fill="#a855f7" />
                            </Scatter>
                        )}
                    </ScatterChart>
                </ResponsiveContainer>
            </div>

            <div className="mt-4 flex gap-6 justify-center text-[10px] text-gray-500">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-cyan-400"></div> Your Portfolio
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-500"></div> Max Sharpe
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-gray-600"></div> Randomized (n=1000)
                </div>
            </div>
        </div>
    );
}
