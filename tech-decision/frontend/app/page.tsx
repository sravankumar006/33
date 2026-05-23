import type { Metadata } from 'next';
import SearchHero from '@/components/search-hero';

export const metadata: Metadata = {
  title: {
    absolute: 'Tech Decision - Smart Smartphone Comparisons & Deal Intelligence',
  },
  description: 'Find the best tech deal with modern comparisons and honest buying advice. Analyze real specs, track prices, detect fake discounts, and see AI insights.',
  alternates: {
    canonical: '/',
  },
};

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <SearchHero />
    </main>
  );
}
