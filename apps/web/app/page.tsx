"use client";

import Link from 'next/link';
import { useEffect, useState, useRef } from 'react';
import { motion, useInView } from 'framer-motion';

/* ─── Fade-up wrapper ─── */
function FadeUp({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
    const ref = useRef(null);
    const inView = useInView(ref, { once: true, margin: "-60px" });
    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, y: 28 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
            className={className}
        >
            {children}
        </motion.div>
    );
}

/* ─── SVG Logo Mark ─── */
function LogoMark({ size = 32 }: { size?: number }) {
    return (
        <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="32" y2="32">
                    <stop offset="0%" stopColor="#22d3ee" />
                    <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
            </defs>
            <rect width="32" height="32" rx="8" fill="url(#logoGrad)" />
            <path d="M8 22L13 14L18 18L24 10" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="24" cy="10" r="2" fill="white" />
        </svg>
    );
}

/* ═══════════════════════════════════════════════════
   LANDING PAGE
   ═══════════════════════════════════════════════════ */
export default function LandingPage() {
    const [scrolled, setScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener("scroll", handleScroll, { passive: true });
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <div className="relative min-h-screen bg-[#020617] overflow-hidden font-sans selection:bg-cyan-500/30 text-white">
            {/* ── Background Shapes ── */}
            <div className="pointer-events-none fixed inset-0 z-0">
                <div className="absolute top-[-10%] left-[-5%] w-[500px] h-[500px] bg-cyan-500/8 rounded-full blur-[120px] animate-float-slow" />
                <div className="absolute top-[20%] right-[-8%] w-[400px] h-[400px] bg-purple-500/8 rounded-full blur-[100px] animate-float" />
                <div className="absolute bottom-[10%] left-[15%] w-[350px] h-[350px] bg-blue-500/6 rounded-full blur-[100px] animate-float-slow" style={{ animationDelay: "2s" }} />
            </div>

            {/* ═══════════════ NAVBAR ═══════════════ */}
            <nav className={`fixed top-0 w-full z-50 transition-all duration-500 ${scrolled ? "glass-nav shadow-lg shadow-black/20" : "bg-transparent"}`}>
                <div className="max-w-7xl mx-auto px-6 h-[72px] flex items-center justify-between">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2.5 group">
                        <LogoMark />
                        <span className="text-lg font-bold tracking-tight">
                            Profolio <span className="text-cyan-400">AI</span>
                        </span>
                    </Link>

                    {/* Center Nav (Desktop) */}
                    <div className="hidden md:flex items-center gap-8">
                        {["Features", "How It Works", "Technology", "Security"].map((item) => (
                            <a
                                key={item}
                                href={`#${item.toLowerCase().replace(/\s+/g, "-")}`}
                                className="text-sm font-medium text-gray-400 hover:text-white transition-colors duration-300 relative group"
                            >
                                {item}
                                <span className="absolute -bottom-1 left-0 w-0 h-[2px] bg-cyan-400 group-hover:w-full transition-all duration-300" />
                            </a>
                        ))}
                    </div>

                    {/* Right Actions */}
                    <div className="flex items-center gap-3">
                        <Link href="/login" className="hidden sm:inline-flex text-sm font-medium text-gray-400 hover:text-white transition-colors px-4 py-2">
                            Sign In
                        </Link>
                        <Link
                            href="/register"
                            className="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-semibold rounded-full hover:shadow-lg hover:shadow-cyan-500/25 transition-all duration-300 active:scale-95"
                        >
                            Get Started
                        </Link>

                        {/* Mobile Menu Toggle */}
                        <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden ml-2 p-2 text-gray-400 hover:text-white">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                {mobileOpen
                                    ? <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
                                    : <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
                                }
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                {mobileOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="md:hidden glass-nav border-t border-white/5 px-6 py-4 space-y-3"
                    >
                        {["Features", "How It Works", "Technology", "Security"].map((item) => (
                            <a
                                key={item}
                                href={`#${item.toLowerCase().replace(/\s+/g, "-")}`}
                                onClick={() => setMobileOpen(false)}
                                className="block text-sm font-medium text-gray-400 hover:text-white py-2"
                            >
                                {item}
                            </a>
                        ))}
                        <Link href="/login" onClick={() => setMobileOpen(false)} className="block text-sm font-medium text-gray-400 hover:text-white py-2">
                            Sign In
                        </Link>
                    </motion.div>
                )}
            </nav>

            {/* ═══════════════ HERO ═══════════════ */}
            <section className="relative pt-36 pb-24 px-6">
                {/* Radial glow */}
                <div className="hero-glow" />

                <div className="relative max-w-5xl mx-auto text-center">
                    {/* Badge */}
                    <FadeUp>
                        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-8">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500" />
                            </span>
                            <span className="text-xs font-semibold text-cyan-400 tracking-wide uppercase">
                                AI Portfolio Engine v2.0
                            </span>
                        </div>
                    </FadeUp>

                    {/* Headline */}
                    <FadeUp delay={0.1}>
                        <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-extrabold tracking-tight leading-[1.05] mb-6">
                            Manage your assets
                            <br />
                            <span className="text-gradient-animated">with intelligence.</span>
                        </h1>
                    </FadeUp>

                    {/* Subtext */}
                    <FadeUp delay={0.2}>
                        <p className="max-w-2xl mx-auto text-lg sm:text-xl text-gray-400 mb-10 leading-relaxed font-normal">
                            Upload your portfolio statements, resolve Indian asset symbols automatically,
                            and get deep AI-powered insights with sentiment analysis and predictive modeling.
                        </p>
                    </FadeUp>

                    {/* CTA Buttons */}
                    <FadeUp delay={0.3}>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                            <Link
                                href="/tour"
                                className="w-full sm:w-auto px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-base font-semibold rounded-2xl hover:shadow-xl hover:shadow-cyan-500/20 transition-all duration-300 active:scale-95 flex items-center justify-center gap-2"
                            >
                                Take a Tour
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                            </Link>
                            <a
                                href="#how-it-works"
                                className="w-full sm:w-auto px-8 py-4 glass text-white text-base font-medium rounded-2xl hover:bg-white/5 transition-all duration-300 active:scale-95"
                            >
                                See How It Works
                            </a>
                        </div>
                    </FadeUp>

                    {/* Trust Indicators */}
                    <FadeUp delay={0.4}>
                        <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
                            <span className="flex items-center gap-1.5">
                                <span className="text-base">🇮🇳</span> Built for Indian Investors
                            </span>
                            <span className="hidden sm:inline text-gray-700">·</span>
                            <span className="flex items-center gap-1.5">
                                <svg className="w-4 h-4 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                                AI + Sentiment Powered
                            </span>
                            <span className="hidden sm:inline text-gray-700">·</span>
                            <span className="flex items-center gap-1.5">
                                <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                                Secure &amp; Private
                            </span>
                        </div>
                    </FadeUp>
                </div>
            </section>

            {/* ═══════════════ FEATURES ═══════════════ */}
            <section id="features" className="relative py-24 px-6">
                <div className="max-w-6xl mx-auto">
                    <FadeUp>
                        <div className="text-center mb-16">
                            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest mb-3 block">Core Capabilities</span>
                            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">Everything you need to manage your portfolio</h2>
                            <p className="text-gray-400 max-w-xl mx-auto">Three powerful modules working together to give you complete portfolio intelligence.</p>
                        </div>
                    </FadeUp>

                    <div className="grid md:grid-cols-3 gap-6">
                        {[
                            {
                                icon: (
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                ),
                                gradient: "from-cyan-500 to-blue-600",
                                title: "PDF Parser",
                                desc: "Automated extraction from NSDL, CDSL, CAMS, and broker statements. OCR-powered with intelligent table detection.",
                            },
                            {
                                icon: (
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                                ),
                                gradient: "from-violet-500 to-purple-600",
                                title: "Asset Resolver",
                                desc: "Maps Indian ISINs, raw names, and fund codes to live market symbols. ISIN registry + heuristic resolution.",
                            },
                            {
                                icon: (
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
                                ),
                                gradient: "from-amber-500 to-orange-600",
                                title: "AI Insights",
                                desc: "FinBERT sentiment analysis, LSTM price predictions, and reinforcement learning-based portfolio optimization.",
                            },
                        ].map((feature, i) => (
                            <FadeUp key={i} delay={i * 0.15}>
                                <div className="glass-card p-8 rounded-2xl h-full">
                                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center text-white mb-5`}>
                                        {feature.icon}
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed mb-4">{feature.desc}</p>
                                    <span className="inline-flex items-center gap-1 text-sm font-medium text-cyan-400 hover:text-cyan-300 cursor-pointer transition-colors group">
                                        Learn more
                                        <svg className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
                                    </span>
                                </div>
                            </FadeUp>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ HOW IT WORKS ═══════════════ */}
            <section id="how-it-works" className="relative py-24 px-6">
                <div className="max-w-5xl mx-auto">
                    <FadeUp>
                        <div className="text-center mb-16">
                            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest mb-3 block">Simple Process</span>
                            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">How It Works</h2>
                            <p className="text-gray-400 max-w-xl mx-auto">Three simple steps from raw PDF to intelligent portfolio insights.</p>
                        </div>
                    </FadeUp>

                    <div className="grid md:grid-cols-3 gap-8 relative">
                        {/* Connecting line (desktop) */}
                        <div className="hidden md:block absolute top-16 left-[calc(16.67%+40px)] right-[calc(16.67%+40px)] h-[2px]">
                            <div className="w-full h-full bg-gradient-to-r from-cyan-500/30 via-purple-500/30 to-amber-500/30 rounded-full" />
                        </div>

                        {[
                            {
                                step: "01",
                                color: "from-cyan-500 to-blue-600",
                                title: "Upload Statement",
                                desc: "Drop your CAS, NSDL, or broker PDF. We support all major Indian formats.",
                                icon: (
                                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                                ),
                            },
                            {
                                step: "02",
                                color: "from-violet-500 to-purple-600",
                                title: "Extract & Resolve",
                                desc: "Our engine parses tables, resolves ISINs, fetches live prices, and normalizes holdings.",
                                icon: (
                                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
                                ),
                            },
                            {
                                step: "03",
                                color: "from-amber-500 to-orange-600",
                                title: "AI Generates Insights",
                                desc: "Get portfolio metrics, risk analysis, AI recommendations, and actionable rebalancing strategies.",
                                icon: (
                                    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
                                ),
                            },
                        ].map((s, i) => (
                            <FadeUp key={i} delay={i * 0.15}>
                                <div className="relative text-center">
                                    <div className={`w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${s.color} flex items-center justify-center text-white shadow-lg relative z-10`}>
                                        {s.icon}
                                    </div>
                                    <span className="text-xs font-bold text-gray-600 uppercase tracking-widest mb-2 block">Step {s.step}</span>
                                    <h3 className="text-lg font-semibold text-white mb-2">{s.title}</h3>
                                    <p className="text-gray-400 text-sm leading-relaxed">{s.desc}</p>
                                </div>
                            </FadeUp>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ TECHNOLOGY ═══════════════ */}
            <section id="technology" className="relative py-24 px-6">
                <div className="absolute inset-0 bg-gradient-to-b from-transparent via-cyan-500/[0.02] to-transparent pointer-events-none" />
                <div className="max-w-6xl mx-auto relative">
                    <FadeUp>
                        <div className="text-center mb-16">
                            <span className="text-xs font-semibold text-cyan-400 uppercase tracking-widest mb-3 block">Under the Hood</span>
                            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">Powered by Real AI</h2>
                            <p className="text-gray-400 max-w-xl mx-auto">Not just charts and graphs — real machine learning models trained for Indian markets.</p>
                        </div>
                    </FadeUp>

                    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
                        {[
                            {
                                icon: "🧠",
                                title: "LSTM Neural Networks",
                                desc: "2-layer deep learning model for next-day price prediction on historical data.",
                            },
                            {
                                icon: "📊",
                                title: "FinBERT Sentiment",
                                desc: "Financial domain-specific BERT model for analyzing market sentiment signals.",
                            },
                            {
                                icon: "📈",
                                title: "Real-Time NAV",
                                desc: "Live mutual fund NAV from AMFI + stock prices from Yahoo Finance APIs.",
                            },
                            {
                                icon: "🎯",
                                title: "Portfolio Analytics",
                                desc: "Sharpe ratio, VaR (95%), HHI diversification scoring, and volatility analysis.",
                            },
                        ].map((tech, i) => (
                            <FadeUp key={i} delay={i * 0.1}>
                                <div className="glass-card p-6 rounded-2xl text-center h-full">
                                    <div className="text-3xl mb-4">{tech.icon}</div>
                                    <h3 className="text-base font-semibold text-white mb-2">{tech.title}</h3>
                                    <p className="text-gray-400 text-xs leading-relaxed">{tech.desc}</p>
                                </div>
                            </FadeUp>
                        ))}
                    </div>
                </div>
            </section>

            {/* ═══════════════ SECURITY ═══════════════ */}
            <section id="security" className="relative py-24 px-6">
                <div className="max-w-4xl mx-auto">
                    <FadeUp>
                        <div className="glass-card rounded-3xl p-10 sm:p-14 text-center">
                            <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                                <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                            </div>
                            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">Your Data Stays Yours</h2>
                            <p className="text-gray-400 max-w-lg mx-auto mb-10">
                                We take your financial privacy seriously. Your portfolio data is never shared, sold, or used for anything other than your personal analysis.
                            </p>

                            <div className="grid sm:grid-cols-3 gap-6 text-left">
                                {[
                                    {
                                        icon: (
                                            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                                        ),
                                        title: "Encrypted Storage",
                                        desc: "All data is stored securely with industry-standard encryption.",
                                    },
                                    {
                                        icon: (
                                            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" /></svg>
                                        ),
                                        title: "No Third-Party Sharing",
                                        desc: "Your financial data is never sold or shared with external parties.",
                                    },
                                    {
                                        icon: (
                                            <svg className="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2" /></svg>
                                        ),
                                        title: "Self-Hosted Ready",
                                        desc: "Run the entire system on your own infrastructure for full control.",
                                    },
                                ].map((item, i) => (
                                    <div key={i} className="flex gap-3">
                                        <div className="mt-0.5 shrink-0">{item.icon}</div>
                                        <div>
                                            <h4 className="text-sm font-semibold text-white mb-1">{item.title}</h4>
                                            <p className="text-xs text-gray-400 leading-relaxed">{item.desc}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </FadeUp>
                </div>
            </section>

            {/* ═══════════════ CTA BANNER ═══════════════ */}
            <section className="relative py-24 px-6">
                <div className="max-w-4xl mx-auto">
                    <FadeUp>
                        <div className="relative rounded-3xl overflow-hidden">
                            {/* Gradient bg */}
                            <div className="absolute inset-0 bg-gradient-to-br from-cyan-600/20 via-blue-600/20 to-purple-600/20" />
                            <div className="absolute inset-0 bg-[#020617]/60" />

                            <div className="relative p-10 sm:p-16 text-center">
                                <h2 className="text-3xl sm:text-4xl font-bold tracking-tight mb-4">
                                    Ready to take control of your portfolio?
                                </h2>
                                <p className="text-gray-400 max-w-md mx-auto mb-8">
                                    Join investors who use AI to make smarter decisions. Upload your first statement in under 60 seconds.
                                </p>
                                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                                    <Link
                                        href="/register"
                                        className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-2xl hover:shadow-xl hover:shadow-cyan-500/20 transition-all duration-300 active:scale-95"
                                    >
                                        Get Started Free →
                                    </Link>
                                    <Link
                                        href="/login"
                                        className="px-8 py-4 glass text-white font-medium rounded-2xl hover:bg-white/5 transition-all duration-300 active:scale-95"
                                    >
                                        Sign In
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </FadeUp>
                </div>
            </section>

            {/* ═══════════════ FOOTER ═══════════════ */}
            <footer className="relative border-t border-white/5">
                <div className="max-w-7xl mx-auto px-6 py-16">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-10 mb-12">
                        {/* Brand */}
                        <div className="col-span-2 md:col-span-1">
                            <div className="flex items-center gap-2 mb-4">
                                <LogoMark size={28} />
                                <span className="text-base font-bold">Profolio <span className="text-cyan-400">AI</span></span>
                            </div>
                            <p className="text-sm text-gray-500 leading-relaxed">
                                AI-powered portfolio intelligence for modern Indian investors.
                            </p>
                        </div>

                        {/* Product */}
                        <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Product</h4>
                            <ul className="space-y-2.5">
                                {["Features", "Pricing", "Roadmap", "Changelog"].map((item) => (
                                    <li key={item}><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">{item}</a></li>
                                ))}
                            </ul>
                        </div>

                        {/* Resources */}
                        <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Resources</h4>
                            <ul className="space-y-2.5">
                                {["Documentation", "Blog", "Examples", "API Reference"].map((item) => (
                                    <li key={item}><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">{item}</a></li>
                                ))}
                            </ul>
                        </div>

                        {/* Company */}
                        <div>
                            <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Company</h4>
                            <ul className="space-y-2.5">
                                {["About", "Contact", "Privacy Policy", "Terms of Service"].map((item) => (
                                    <li key={item}><a href="#" className="text-sm text-gray-500 hover:text-white transition-colors">{item}</a></li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    {/* Bottom bar */}
                    <div className="pt-8 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <p className="text-xs text-gray-600">
                            © 2026 Profolio AI. All rights reserved.
                        </p>
                        <p className="text-xs text-gray-600">
                            Built with PyTorch, FinBERT &amp; Next.js
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
