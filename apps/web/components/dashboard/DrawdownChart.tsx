"use client";

import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingDown, AlertTriangle } from 'lucide-react';
import api from '@/lib/api';
import { useSession } from 'next-auth/react';

export default function DrawdownChart({ holdings }: { holdings: any[] }) {
    const { data: session } = useSession();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!(session as any)?.accessToken || !holdings || holdings.length === 0) return;
            try {
                setLoading(true);
                // Reuse risk endpoint which returns drawdown data
                const response = await api.post('/api/analytics/risk/correlation', holdings, {
                    headers: { Authorization: `Bearer ${(session as any).accessToken}` }
                });
                setData(response.data.drawdown);
            } catch (e) {
                console.error("Drawdown Fetch Error", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [holdings, session]);

    if (loading) return <div className="h-[200px] flex items-center justify-center animate-pulse text-gray-600">Analyzing Historical Risk...</div>;
    if (!data || !data.drawdown_series) return <div className="h-[200px] flex items-center justify-center text-gray-500">No drawdown data available.</div>;

    return (
        <div className="w-full">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="font-bold text-lg flex items-center gap-2">
                        <TrendingDown className="w-5 h-5 text-orange-500" />
                        Drawdown Analysis
                    </h3>
                    <p className="text-xs text-gray-500">Historical "Underwater" Profile</p>
                </div>
                <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-gray-500 block">Max Drawdown</span>
                    <span className="text-xl font-black text-orange-500">
                        {(data.max_drawdown * 100).toFixed(2)}%
                    </span>
                </div>
            </div>

            <div className="h-[200px] w-full bg-gradient-to-b from-orange-500/5 to-transparent rounded-xl border border-orange-500/10 p-2">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data.drawdown_series} margin={{ top: 10, right: 0, bottom: 0, left: -20 }}>
                        <defs>
                            <linearGradient id="colorDd" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="date"
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { month: 'short', year: '2-digit' })}
                            minTickGap={40}
                        />
                        <YAxis
                            stroke="#475569"
                            tick={{ fill: '#475569', fontSize: 10 }}
                            tickFormatter={(val) => `${val}%`}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#f97316', borderRadius: '8px' }}
                            itemStyle={{ color: '#f97316', fontSize: '12px' }}
                            formatter={(value: any) => [`${Number(value).toFixed(2)}%`, 'Drawdown']}
                            labelStyle={{ color: '#94a3b8', marginBottom: '4px' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="drawdown"
                            stroke="#f97316"
                            fill="url(#colorDd)"
                            strokeWidth={2}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            <p className="mt-2 text-[10px] text-orange-400/60 flex items-center gap-1 justify-center">
                <AlertTriangle className="w-3 h-3" /> Historical worst-case decline from peak.
            </p>
        </div>
    );
}
