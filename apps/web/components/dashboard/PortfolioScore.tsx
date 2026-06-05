"use client";

import { motion } from 'framer-motion';
import { Info, Activity } from 'lucide-react';

interface ScoreProps {
    data: {
        total_score: number;
        grade: string;
        breakdown: {
            diversification: number;
            risk: number;
            sentiment: number;
            quality: number;
        };
        summary: string;
    } | null;
    isSimulated?: boolean;
}

export default function PortfolioScore({ data, isSimulated }: ScoreProps) {
    if (!data) return <div className="animate-pulse bg-gray-800 rounded-lg h-40" />;

    const { total_score, grade, breakdown, summary } = data;

    // Color logic
    const getColor = (s: number) => {
        if (s >= 80) return "text-emerald-400";
        if (s >= 60) return "text-amber-400";
        return "text-red-400";
    };

    const ringColor = total_score >= 80 ? "#34d399" : total_score >= 60 ? "#fbbf24" : "#f87171";
    const circumference = 2 * Math.PI * 40;
    const strokeDashoffset = circumference - (total_score / 100) * circumference;

    return (
        <div className="flex items-center gap-6">
            {/* Radial Chart */}
            <div className="relative w-32 h-32 flex-shrink-0">
                <svg className="w-full h-full transform -rotate-90">
                    <circle cx="64" cy="64" r="40" stroke="#1e293b" strokeWidth="8" fill="transparent" />
                    <motion.circle
                        cx="64" cy="64" r="40"
                        stroke={ringColor}
                        strokeWidth="8"
                        fill="transparent"
                        strokeDasharray={circumference}
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        strokeLinecap="round"
                    />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className={`text-3xl font-bold ${getColor(total_score)}`}>{grade}</span>
                    <span className="text-xs text-gray-400">Grade</span>
                </div>
            </div>

            {/* Breakdown */}
            <div className="flex-1 space-y-3">
                <div className="flex justify-between items-baseline">
                    <h3 className="text-white font-semibold flex items-center gap-2">
                        {isSimulated ? (
                            <span className="flex items-center gap-1.5 py-0.5 px-2 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-[9px] text-cyan-400 font-black uppercase tracking-widest animate-pulse">
                                <Activity className="w-2.5 h-2.5" /> Simulated Scenario
                            </span>
                        ) : (
                            <>
                                AI Health Score
                                <div className="group relative">
                                    <Info className="w-3.5 h-3.5 text-gray-500 cursor-help" />
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 bg-slate-900 border border-slate-700 p-2 rounded text-xs text-gray-300 hidden group-hover:block z-50 shadow-xl">
                                        0-100 Score based on Diversification (30), Risk (30), Sentiment (20), Quality (20).
                                    </div>
                                </div>
                            </>
                        )}
                    </h3>
                    <span className="text-2xl font-bold text-white">{total_score}<span className="text-sm text-gray-500">/100</span></span>
                </div>

                <p className="text-xs text-gray-400 leading-relaxed border-l-2 border-gray-700 pl-2">
                    {summary}
                </p>

                <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-500 font-mono pt-1">
                    <div className="flex justify-between"><span>DIVERSIFICATION</span> <span className="text-gray-300">{breakdown.diversification}/30</span></div>
                    <div className="flex justify-between"><span>RISK EFFICIENCY</span> <span className="text-gray-300">{breakdown.risk}/30</span></div>
                    <div className="flex justify-between"><span>SENTIMENT</span> <span className="text-gray-300">{breakdown.sentiment}/20</span></div>
                    <div className="flex justify-between"><span>QUALITY</span> <span className="text-gray-300">{breakdown.quality}/20</span></div>
                </div>
            </div>
        </div>
    );
}
