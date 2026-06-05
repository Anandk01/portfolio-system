"use client";

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Info } from 'lucide-react';
import api from '@/lib/api';
import { useSession } from 'next-auth/react';

export default function RiskHeatmap({ holdings }: { holdings: any[] }) {
    const { data: session } = useSession();
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            if (!(session as any)?.accessToken || !holdings || holdings.length === 0) return;

            try {
                setLoading(true);
                // We need to pass holdings to get the analysis
                const response = await api.post('/api/analytics/risk/correlation', holdings, {
                    headers: { Authorization: `Bearer ${(session as any).accessToken}` }
                });
                setData(response.data);
            } catch (e) {
                console.error("Risk Fetch Error", e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [holdings, session]);

    if (loading) return <div className="h-[300px] flex items-center justify-center animate-pulse text-gray-600">Calculating Risk Matrix...</div>;
    if (!data || !data.correlation || !data.correlation.symbols) return <div className="h-[300px] flex items-center justify-center text-gray-500">Not enough data for correlation analysis.</div>;

    const { symbols, matrix, average_correlation, diversification_score } = data.correlation;
    const size = symbols.length;

    // Helper to get color based on correlation
    const getColor = (val: number) => {
        if (val === 1) return "bg-gray-800 text-gray-600"; // Diagonal
        if (val > 0.7) return "bg-rose-500/80 text-white font-bold"; // High Risk
        if (val > 0.5) return "bg-orange-500/60 text-white";
        if (val > 0.3) return "bg-yellow-500/40 text-white";
        return "bg-emerald-500/40 text-emerald-100"; // Low Risk (Good)
    };

    return (
        <div className="w-full">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="font-bold text-lg flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5 text-rose-400" />
                        Correlation Matrix
                    </h3>
                    <p className="text-xs text-gray-500">
                        Avg Correlation: <span className={average_correlation > 0.6 ? "text-rose-400" : "text-emerald-400"}>{average_correlation}</span>
                    </p>
                </div>
                <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-gray-500 block">Diversification Score</span>
                    <span className={`text-xl font-black ${diversification_score < 0.3 ? "text-rose-500" : "text-emerald-400"}`}>
                        {(diversification_score * 100).toFixed(0)}/100
                    </span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <div
                    className="grid gap-1"
                    style={{
                        gridTemplateColumns: `40px repeat(${size}, minmax(40px, 1fr))`,
                    }}
                >
                    {/* Header Row */}
                    <div className="h-8"></div>
                    {symbols.map((s: string) => (
                        <div key={s} className="h-8 flex items-center justify-center text-[10px] font-bold text-gray-400 -rotate-45 origin-bottom-left translate-x-2">
                            {s.length > 4 ? s.substring(0, 4) : s}
                        </div>
                    ))}

                    {/* Rows */}
                    {symbols.map((rowSym: string, i: number) => (
                        <>
                            {/* Row Label */}
                            <div className="w-10 flex items-center justify-end pr-2 text-[10px] font-bold text-gray-400">
                                {rowSym.length > 4 ? rowSym.substring(0, 4) : rowSym}
                            </div>

                            {/* Cells */}
                            {matrix[i].map((val: number, j: number) => (
                                <div
                                    key={`${i}-${j}`}
                                    className={`aspect-square rounded-md flex items-center justify-center text-[10px] cursor-help transition hover:scale-110 hover:z-10 ${getColor(val)}`}
                                    title={`${symbols[i]} vs ${symbols[j]}: ${val}`}
                                >
                                    {val === 1 ? "" : val.toFixed(1).replace("0.", ".")}
                                </div>
                            ))}
                        </>
                    ))}
                </div>
            </div>

            <div className="mt-4 flex gap-4 text-[10px] text-gray-500 justify-center">
                <div className="flex items-center gap-1"><div className="w-3 h-3 bg-emerald-500/40 rounded"></div>Low (&lt;0.3)</div>
                <div className="flex items-center gap-1"><div className="w-3 h-3 bg-yellow-500/40 rounded"></div>Med</div>
                <div className="flex items-center gap-1"><div className="w-3 h-3 bg-rose-500/80 rounded"></div>High (&gt;0.7)</div>
            </div>
        </div>
    );
}
