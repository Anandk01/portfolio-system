"use client";

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertTriangle, Newspaper, Zap } from 'lucide-react';

interface FeedItem {
    id: string;
    type: "price" | "sentiment" | "risk" | "insight";
    title: string;
    description: string;
    asset_symbol?: string;
    impact_level: "HIGH" | "MEDIUM" | "LOW";
    timestamp: string;
    url?: string;
    sentiment_score?: number;
}

export default function IntelligenceFeed({ items }: { items: FeedItem[] }) {
    if (!items || items.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500 gap-3">
                <Zap className="w-8 h-8 opacity-20" />
                <p className="text-sm">No signals detected yet.</p>
            </div>
        );
    }

    const getIcon = (item: FeedItem) => {
        if (item.type === 'risk') return <AlertTriangle className="w-4 h-4 text-amber-500" />;
        if (item.type === 'sentiment') {
            return (item.sentiment_score || 0) > 0
                ? <TrendingUp className="w-4 h-4 text-emerald-500" />
                : <TrendingDown className="w-4 h-4 text-red-500" />;
        }
        if (item.type === 'price') return <Zap className="w-4 h-4 text-cyan-500" />;
        return <Newspaper className="w-4 h-4 text-blue-500" />;
    };

    const getBorderColor = (level: string) => {
        if (level === 'HIGH') return 'border-l-red-500';
        if (level === 'MEDIUM') return 'border-l-amber-500';
        return 'border-l-blue-500';
    };

    return (
        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-4">
            {items.map((item, i) => (
                <motion.div
                    key={item.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`bg-white/[0.02] border border-white/5 rounded-r-xl border-l-[3px] ${getBorderColor(item.impact_level)} p-4 hover:bg-white/[0.04] transition-colors group`}
                >
                    <div className="flex items-start justify-between gap-3">
                        <div className="flex gap-3">
                            <div className="mt-1 p-1.5 bg-white/5 rounded-lg shrink-0 group-hover:scale-110 transition-transform">
                                {getIcon(item)}
                            </div>
                            <div>
                                <h4 className="text-sm font-semibold text-gray-200 leading-tight mb-1">
                                    {item.title}
                                </h4>
                                <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                                    {item.description}
                                </p>
                            </div>
                        </div>
                        {item.asset_symbol && (
                            <span className="text-[10px] font-mono bg-white/5 px-2 py-1 rounded text-gray-400 whitespace-nowrap">
                                {item.asset_symbol}
                            </span>
                        )}
                    </div>

                    {item.url && (
                        <div className="mt-2 pl-[42px]">
                            <a href={item.url} target="_blank" rel="noreferrer" className="text-[10px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1">
                                Read Source <span aria-hidden="true">&rarr;</span>
                            </a>
                        </div>
                    )}
                </motion.div>
            ))}
        </div>
    );
}
