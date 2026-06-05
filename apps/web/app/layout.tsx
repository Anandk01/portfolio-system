import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import AuthContext from '../components/AuthContext'

const inter = Inter({
    subsets: ['latin'],
    display: 'swap',
    variable: '--font-inter',
})

export const metadata: Metadata = {
    title: 'Profolio AI — AI-Powered Portfolio Intelligence',
    description: 'Upload your brokerage statements, resolve Indian asset symbols automatically, and get deep AI-powered insights with sentiment analysis and predictive modeling.',
    keywords: ['portfolio', 'AI', 'fintech', 'Indian stocks', 'mutual funds', 'ETFs', 'sentiment analysis'],
    openGraph: {
        title: 'Profolio AI — AI-Powered Portfolio Intelligence',
        description: 'Smart portfolio analysis for modern Indian investors.',
        type: 'website',
    },
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className={`${inter.variable} dark`}>
            <body className="font-sans antialiased">
                <AuthContext>
                    {children}
                </AuthContext>
            </body>
        </html>
    )
}
