"use client";

import { useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { motion } from 'framer-motion';

const COLORS = ['#22d3ee', '#3b82f6', '#8b5cf6', '#a855f7', '#ec4899', '#f43f5e', '#64748b'];

export default function SectorAllocation({ holdings }: { holdings: any[] }) {
    const data = useMemo(() => {
        if (!holdings || holdings.length === 0) return [];

        const categories: Record<string, number> = {
            "Equity": 0,
            "Mutual Funds (Demat)": 0,
            "Mutual Funds (SOA)": 0,
            "Others": 0
        };

        holdings.forEach(h => {
            const type = h.asset_type || "UNKNOWN";
            const account = h.account_type || "UNKNOWN";

            let label = "Others";
            if (type === "STOCK") {
                label = "Equity";
            } else if ((type === "MF" && account === "DEMAT") || type === "ETF") {
                label = "Mutual Funds (Demat)";
            } else if (type === "MF" && account === "SOA") {
                label = "Mutual Funds (SOA)";
            } else if (type === "COMMODITY") {
                label = "Others"; // Or Commodities if we add it
            }

            if (categories[label] !== undefined) {
                categories[label] += h.current_value;
            } else {
                categories["Others"] += h.current_value;
            }
        });

        return Object.entries(categories)
            .filter(([_, value]) => value > 0) // Only show non-zero
            .map(([name, value]) => ({ name, value }))
            .sort((a, b) => b.value - a.value);
    }, [holdings]);

    if (data.length === 0) {
        return (
            <div className="flex h-full items-center justify-center text-gray-500 text-sm">
                No sector data available
            </div>
        );
    }

    const topSector = data[0];
    const topSectorShare = ((topSector.value / data.reduce((a, b) => a + b.value, 0)) * 100).toFixed(0);

    return (
        <div className="h-full flex flex-col">
            {/* Risk Warning - Top Relative */}
            {Number(topSectorShare) > 40 && (
                <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-2 bg-red-500/10 border border-red-500/20 rounded-lg p-2 flex items-center gap-2 flex-shrink-0"
                >
                    <div className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                    <span className="text-[10px] font-medium text-red-200">High concentration in {topSector.name}</span>
                </motion.div>
            )}

            <div className="flex-1 min-h-0 relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={55}
                            outerRadius={75}
                            paddingAngle={2}
                            dataKey="value"
                            stroke="none"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px' }}
                            itemStyle={{ color: '#e2e8f0' }}
                            formatter={(value: any) => [`₹${Number(value).toLocaleString()}`, 'Value']}
                        />
                        <Legend
                            layout="vertical"
                            verticalAlign="middle"
                            align="right"
                            iconType="circle"
                            iconSize={6}
                            wrapperStyle={{ fontSize: '10px', color: '#94a3b8' }}
                        />
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Label */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-6 pr-20">
                    <span className="text-xl font-bold text-white">{topSectorShare}%</span>
                    <span className="text-[9px] text-gray-400 uppercase tracking-wider">{topSector.name.substring(0, 8)}</span>
                </div>
            </div>
        </div>
    );
}
