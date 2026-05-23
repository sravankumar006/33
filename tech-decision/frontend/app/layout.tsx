import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import './globals.css';

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  title: {
    template: '%s | Tech Decision',
    default: 'Tech Decision - Smart Smartphone Comparisons & Deal Intelligence',
  },
  description: 'Compare smartphone specifications, analyze live prices, detect fake discounts, and get honest AI-generated verdicts to find the absolute best deals.',
  keywords: [
    'smartphone comparison',
    'mobile comparison',
    'phone deals',
    'fake discount detector',
    'price tracking',
    'honest phone reviews',
    'AI tech review',
    'mobile specs analysis',
  ],
  authors: [{ name: 'Tech Decision Team' }],
  creator: 'Tech Decision',
  publisher: 'Tech Decision',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'http://localhost:3000',
    title: 'Tech Decision - Smartphone Comparisons & Deal Intelligence',
    description: 'Compare smartphone specifications, analyze live prices, detect fake discounts, and get honest AI-generated verdicts to find the absolute best deals.',
    siteName: 'Tech Decision',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'Tech Decision - Deal Intelligence',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Tech Decision - Smartphone Comparisons & Deal Intelligence',
    description: 'Compare smartphone specifications, analyze live prices, detect fake discounts, and get honest AI-generated verdicts to find the absolute best deals.',
    images: ['/og-image.jpg'],
  },
  alternates: {
    canonical: '/',
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
