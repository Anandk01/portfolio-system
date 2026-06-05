"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const LOADING_MESSAGES = [
    "Analyzing your portfolio…",
    "Fetching market signals…",
    "Running AI models…",
    "Crunching the numbers…",
];

interface PageLoaderProps {
    isLoading: boolean;
    variant?: "fullscreen" | "bar";
}

export default function PageLoader({ isLoading, variant = "fullscreen" }: PageLoaderProps) {
    const [msgIndex, setMsgIndex] = useState(0);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        if (!isLoading) {
            setProgress(0);
            setMsgIndex(0);
            return;
        }
        const msgTimer = setInterval(() => {
            setMsgIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
        }, 2500);
        const progTimer = setInterval(() => {
            setProgress((prev) => Math.min(prev + Math.random() * 8 + 2, 95));
        }, 400);
        return () => {
            clearInterval(msgTimer);
            clearInterval(progTimer);
        };
    }, [isLoading]);

    /* ─ Bar variant: thin gradient line at top ─ */
    if (variant === "bar") {
        return (
            <AnimatePresence>
                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed top-0 left-0 w-full z-[100] h-[2px]"
                    >
                        <motion.div
                            initial={{ width: "0%" }}
                            animate={{ width: `${progress}%` }}
                            transition={{ ease: "easeOut", duration: 0.3 }}
                            className="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500"
                        />
                    </motion.div>
                )}
            </AnimatePresence>
        );
    }

    /* ─ Fullscreen variant ─ */
    return (
        <AnimatePresence>
            {isLoading && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0, transition: { duration: 0.4 } }}
                    className="fixed inset-0 z-[100] bg-[#020617] flex flex-col items-center justify-center"
                >
                    {/* Animated Logo */}
                    <motion.div
                        animate={{ scale: [1, 1.05, 1] }}
                        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        className="mb-8"
                    >
                        <svg width="56" height="56" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <linearGradient id="loaderGrad" x1="0" y1="0" x2="32" y2="32">
                                    <stop offset="0%" stopColor="#22d3ee" />
                                    <stop offset="100%" stopColor="#3b82f6" />
                                </linearGradient>
                            </defs>
                            <rect width="32" height="32" rx="8" fill="url(#loaderGrad)" />
                            <motion.path
                                d="M8 22L13 14L18 18L24 10"
                                stroke="white"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                            />
                            <circle cx="24" cy="10" r="2" fill="white" />
                        </svg>
                    </motion.div>

                    {/* Rotating text */}
                    <div className="h-6 overflow-hidden">
                        <AnimatePresence mode="wait">
                            <motion.p
                                key={msgIndex}
                                initial={{ opacity: 0, y: 12 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -12 }}
                                transition={{ duration: 0.3 }}
                                className="text-sm text-gray-400 font-medium"
                            >
                                {LOADING_MESSAGES[msgIndex]}
                            </motion.p>
                        </AnimatePresence>
                    </div>

                    {/* Progress bar */}
                    <div className="w-48 h-[2px] bg-white/5 rounded-full mt-6 overflow-hidden">
                        <motion.div
                            initial={{ width: "0%" }}
                            animate={{ width: `${progress}%` }}
                            className="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"
                        />
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
