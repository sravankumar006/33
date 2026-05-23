'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  Sparkles, 
  Cpu, 
  Tv, 
  Zap, 
  Layers, 
  Wifi, 
  Smartphone, 
  AlertTriangle, 
  Camera,
  ShoppingBag
} from 'lucide-react';
import type { PhoneDetail, PriceComparisonResponse, PhoneVariant } from './types';
import PriceComparisonSection from './PriceComparisonSection';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'http://localhost:8000';

const formatINR = (value: number | null | undefined) => {
  if (value === null || value === undefined || value === 0) return 'Price pending';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);
};

interface PhoneDetailClientProps {
  slug: string;
}

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-3xl border border-white/10 bg-slate-900/80 p-6">
      <div className="h-5 w-3/4 rounded-full bg-slate-800"></div>
      <div className="mt-4 grid gap-3">
        <div className="h-4 w-full rounded-full bg-slate-800"></div>
        <div className="h-4 w-5/6 rounded-full bg-slate-800"></div>
      </div>
    </div>
  );
}

interface DecisionData {
  decision: 'BUY_NOW' | 'WAIT_FOR_PRICE_DROP' | 'BUY_COMPETITOR' | 'SKIP';
  headline: string;
  summary: string;
  pros: string[];
  cons: string[];
  confidence_score: number;
}

function DecisionSection({ slug, variantId }: { slug: string; variantId?: string }) {
  const [data, setData] = useState<DecisionData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const fetchDecision = async () => {
      setLoading(true);
      try {
        const url = variantId
          ? `${API_URL}/api/phones/${encodeURIComponent(slug)}/decision?variant_id=${encodeURIComponent(variantId)}`
          : `${API_URL}/api/phones/${encodeURIComponent(slug)}/decision`;
        console.log(`DecisionSection: Fetching decision for ${slug} from ${url}`);
        const res = await fetch(url);
        if (!res.ok) throw new Error(`Decision API status: ${res.status}`);
        const decisionData = await res.json();
        console.log("DecisionSection: Success", decisionData);
        if (active) {
          setData(decisionData);
        }
      } catch (err) {
        console.error("DecisionSection error:", err);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };
    fetchDecision();
    return () => {
      active = false;
    };
  }, [slug, variantId]);

  if (loading) {
    return (
      <div className="animate-pulse rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-glass">
        <div className="h-6 w-1/4 rounded-full bg-slate-800"></div>
        <div className="mt-6 h-32 rounded-3xl bg-slate-800"></div>
      </div>
    );
  }

  if (!data) return null;

  const getTheme = () => {
    switch (data.decision) {
      case 'BUY_NOW':
        return {
          bg: 'from-emerald-500/10 to-teal-500/5',
          border: 'border-emerald-500/20 hover:border-emerald-500/40',
          badgeBg: 'bg-emerald-500/10 border-emerald-400/20 text-emerald-300',
          recommendation: "Buy now — this is one of the best prices we've seen recently.",
          glow: 'shadow-emerald-500/5',
          circleColor: '#10b981'
        };
      case 'WAIT_FOR_PRICE_DROP':
        return {
          bg: 'from-amber-500/10 to-yellow-500/5',
          border: 'border-amber-500/20 hover:border-amber-500/40',
          badgeBg: 'bg-amber-500/10 border-amber-400/20 text-amber-300',
          recommendation: "Wait — this phone is currently overpriced compared to its usual pricing.",
          glow: 'shadow-amber-500/5',
          circleColor: '#f59e0b'
        };
      case 'BUY_COMPETITOR':
        return {
          bg: 'from-orange-500/10 to-amber-500/5',
          border: 'border-orange-500/20 hover:border-orange-500/40',
          badgeBg: 'bg-orange-500/10 border-orange-400/20 text-orange-300',
          recommendation: "Consider alternative models for better value.",
          glow: 'shadow-orange-500/5',
          circleColor: '#f97316'
        };
      case 'SKIP':
      default:
        return {
          bg: 'from-rose-500/10 to-red-500/5',
          border: 'border-rose-500/20 hover:border-rose-500/40',
          badgeBg: 'bg-rose-500/10 border-rose-400/20 text-rose-300',
          recommendation: "Skip this and consider another option.",
          glow: 'shadow-rose-500/5',
          circleColor: '#f43f5e'
        };
    }
  };

  const theme = getTheme();
  const radius = 32;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (data.confidence_score / 100) * circumference;

  return (
    <section className={`rounded-[2rem] border bg-gradient-to-br ${theme.bg} ${theme.border} p-6 sm:p-8 shadow-glass shadow-2xl backdrop-blur-xl transition duration-500 ${theme.glow}`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-white/10 pb-6">
        <div>
          <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wider ${theme.badgeBg}`}>
            {data.decision.replace(/_/g, ' ')}
          </span>
          <h2 className="mt-3 text-2xl font-bold text-white sm:text-3xl">
            {data.headline}
          </h2>
          <p className="mt-2 text-cyan-300 font-medium">
            {theme.recommendation}
          </p>
        </div>

        {/* Confidence Indicator */}
        <div className="flex items-center gap-4 bg-slate-950/40 rounded-2xl p-4 border border-white/5">
          <div className="relative h-16 w-16">
            <svg className="h-full w-full -rotate-90">
              <circle
                cx="32"
                cy="32"
                r={radius}
                className="stroke-white/10"
                strokeWidth="5"
                fill="transparent"
              />
              <circle
                cx="32"
                cy="32"
                r={radius}
                className="transition-all duration-1000 ease-out"
                strokeWidth="5"
                fill="transparent"
                stroke={theme.circleColor}
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-bold text-white">{data.confidence_score}%</span>
            </div>
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Confidence Score</p>
            <p className="text-xs text-slate-400">Based on specs, prices, and seller trust</p>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <p className="text-base leading-7 text-slate-300">
          {data.summary}
        </p>
      </div>

      <div className="mt-6 grid md:grid-cols-2 gap-6">
        {/* Pros */}
        <div className="rounded-2xl bg-emerald-500/5 border border-emerald-500/10 p-5">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-emerald-300 mb-4">Pros</h3>
          <ul className="space-y-3">
            {data.pros.map((pro, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                <svg className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span>{pro}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Cons */}
        <div className="rounded-2xl bg-rose-500/5 border border-rose-500/10 p-5">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-rose-300 mb-4">Cons</h3>
          <ul className="space-y-3">
            {data.cons.map((con, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                <svg className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>{con}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default function PhoneDetailClient({ slug }: PhoneDetailClientProps) {
  const [phone, setPhone] = useState<PhoneDetail | null>(null);
  const [status, setStatus] = useState<'loading' | 'success' | 'notfound' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [priceData, setPriceData] = useState<PriceComparisonResponse | null>(null);
  const [selectedVariant, setSelectedVariant] = useState<PhoneVariant | null>(null);
  const [pricesLoading, setPricesLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    const loadPhone = async () => {
      setStatus('loading');
      setErrorMessage('');

      try {
        const response = await fetch(`${API_URL}/api/phones/${encodeURIComponent(slug)}`, {
          signal: controller.signal,
        });

        if (response.status === 404) {
          setStatus('notfound');
          setPhone(null);
          return;
        }

        if (!response.ok) {
          throw new Error('Unable to load phone details');
        }

        const data: PhoneDetail = await response.json();
        setPhone(data);
        
        if (data.variants && data.variants.length > 0) {
          const sorted = [...data.variants].sort((a, b) => {
            if (a.storage_gb !== b.storage_gb) return a.storage_gb - b.storage_gb;
            return a.ram_gb - b.ram_gb;
          });
          setSelectedVariant(sorted[0]);
        } else {
          setSelectedVariant(null);
        }
        
        setStatus('success');
      } catch {
        if (controller.signal.aborted) {
          return;
        }

        setStatus('error');
        setErrorMessage('Something went wrong while loading the phone. Please try again later.');
      }
    };

    loadPhone();

    return () => controller.abort();
  }, [slug]);

  // Separate effect to fetch pricing dynamically when variant changes
  useEffect(() => {
    if (!phone) return;

    const controller = new AbortController();
    const fetchPrices = async () => {
      setPricesLoading(true);
      try {
        const url = selectedVariant
          ? `${API_URL}/api/phones/${encodeURIComponent(slug)}/prices?variant_id=${encodeURIComponent(selectedVariant.id)}`
          : `${API_URL}/api/phones/${encodeURIComponent(slug)}/prices`;

        console.log(`PhoneDetailClient: Fetching prices from ${url}`);
        const pricesResponse = await fetch(url, {
          signal: controller.signal,
        });
        if (pricesResponse.ok) {
          const pricesData: PriceComparisonResponse = await pricesResponse.json();
          setPriceData(pricesData);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          console.error("Failed to load prices:", err);
        }
      } finally {
        setPricesLoading(false);
      }
    };

    fetchPrices();

    return () => controller.abort();
  }, [slug, phone?.id, selectedVariant?.id]);

  const handleGenerateInsights = async () => {
    if (!phone) return;
    setIsGenerating(true);
    try {
      const response = await fetch(`${API_URL}/api/phones/${encodeURIComponent(slug)}/generate-insights`, {
        method: 'POST',
      });
      if (!response.ok) {
        let errMsg = 'Failed to generate insights';
        try {
          const data = await response.json();
          if (data && data.detail) {
            errMsg = data.detail;
          }
        } catch {
          // ignore parsing error
        }
        throw new Error(errMsg);
      }
      const newInsight = await response.json();
      setPhone({
        ...phone,
        insight: newInsight,
      });
    } catch (err: any) {
      alert(err.message || 'Failed to generate insights. Please check that backend server is active and OpenAI API Key is configured.');
    } finally {
      setIsGenerating(false);
    }
  };

  const getVariantLaunchPrice = () => {
    if (!phone) return null;
    const baseLaunchPrice = phone.launch_price || 69999;
    if (!phone.variants || phone.variants.length === 0 || !selectedVariant) {
      return baseLaunchPrice;
    }

    const baseVariant = [...phone.variants].reduce((acc, curr) => {
      if (curr.storage_gb !== acc.storage_gb) {
        return curr.storage_gb < acc.storage_gb ? curr : acc;
      }
      return curr.ram_gb < acc.ram_gb ? curr : acc;
    }, phone.variants[0]);

    const ramDiff = selectedVariant.ram_gb - baseVariant.ram_gb;
    const ramAdjustment = (ramDiff / 4.0) * 3000;

    let storageAdjustment = 0;
    if (baseVariant.storage_gb && selectedVariant.storage_gb) {
      const storageRatio = selectedVariant.storage_gb / baseVariant.storage_gb;
      const storageDoublings = storageRatio > 0 ? Math.log2(storageRatio) : 0;
      storageAdjustment = storageDoublings * 5000;
    }

    return Math.round(baseLaunchPrice + ramAdjustment + storageAdjustment);
  };

  const handleSelectRAM = (ram: number) => {
    if (!phone?.variants || !selectedVariant) return;
    const currentStorage = selectedVariant.storage_gb;
    const currentColor = selectedVariant.color;

    const candidates = phone.variants.filter(v => v.ram_gb === ram);
    if (candidates.length === 0) return;

    let best = candidates.find(v => v.storage_gb === currentStorage && v.color === currentColor);
    if (!best) {
      best = candidates.find(v => v.storage_gb === currentStorage);
    }
    if (!best) {
      best = candidates.find(v => v.color === currentColor);
    }
    if (!best) {
      best = candidates[0];
    }
    setSelectedVariant(best);
  };

  const handleSelectStorage = (storage: number) => {
    if (!phone?.variants || !selectedVariant) return;
    const currentRAM = selectedVariant.ram_gb;
    const currentColor = selectedVariant.color;

    const candidates = phone.variants.filter(v => v.storage_gb === storage);
    if (candidates.length === 0) return;

    let best = candidates.find(v => v.ram_gb === currentRAM && v.color === currentColor);
    if (!best) {
      best = candidates.find(v => v.ram_gb === currentRAM);
    }
    if (!best) {
      best = candidates.find(v => v.color === currentColor);
    }
    if (!best) {
      best = candidates[0];
    }
    setSelectedVariant(best);
  };

  const handleSelectColor = (color: string) => {
    if (!phone?.variants || !selectedVariant) return;
    const currentRAM = selectedVariant.ram_gb;
    const currentStorage = selectedVariant.storage_gb;

    const candidates = phone.variants.filter(v => v.color === color);
    if (candidates.length === 0) return;

    let best = candidates.find(v => v.ram_gb === currentRAM && v.storage_gb === currentStorage);
    if (!best) {
      best = candidates.find(v => v.storage_gb === currentStorage);
    }
    if (!best) {
      best = candidates.find(v => v.ram_gb === currentRAM);
    }
    if (!best) {
      best = candidates[0];
    }
    setSelectedVariant(best);
  };

  const uniqueRAMs = phone?.variants
    ? Array.from(new Set(phone.variants.map(v => v.ram_gb))).sort((a, b) => a - b)
    : [];
  const uniqueStorages = phone?.variants
    ? Array.from(new Set(phone.variants.map(v => v.storage_gb))).sort((a, b) => a - b)
    : [];
  const uniqueColors = phone?.variants
    ? Array.from(new Set(phone.variants.map(v => v.color).filter((c): c is string => !!c))).sort()
    : [];

  const currentLaunchPrice = getVariantLaunchPrice();
  const currentBestPrice = priceData?.best_platform?.final_price ?? priceData?.listings?.[0]?.final_price ?? phone?.current_avg_price ?? null;

  const discountPercent = phone && currentLaunchPrice && currentBestPrice
    ? Math.max(0, Math.round(((currentLaunchPrice - currentBestPrice) / currentLaunchPrice) * 100))
    : 0;

  const isGreatDeal = phone ? discountPercent >= 10 : false;

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100 sm:px-10 lg:px-16">
      <div className="mx-auto max-w-6xl">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-sm font-medium text-cyan-300 transition hover:text-cyan-200"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to search
        </Link>

        {status === 'loading' && (
          <div className="space-y-8">
            <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-glass">
                <div className="h-80 rounded-[1.75rem] bg-slate-800" />
                <div className="mt-6 space-y-4">
                  <div className="h-8 w-3/5 rounded-full bg-slate-800"></div>
                  <div className="h-6 w-2/5 rounded-full bg-slate-800"></div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="h-24 rounded-3xl bg-slate-800"></div>
                    <div className="h-24 rounded-3xl bg-slate-800"></div>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                {Array.from({ length: 6 }).map((_, index) => (
                  <SkeletonCard key={index} />
                ))}
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              {Array.from({ length: 4 }).map((_, index) => (
                <div key={index} className="animate-pulse rounded-3xl border border-white/10 bg-slate-900/80 p-6" />
              ))}
            </div>

            <div className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 shadow-glass">
              <div className="h-8 w-2/5 rounded-full bg-slate-800" />
              <div className="mt-6 space-y-4">
                <div className="h-5 w-full rounded-full bg-slate-800" />
                <div className="h-5 w-5/6 rounded-full bg-slate-800" />
                <div className="h-5 w-4/6 rounded-full bg-slate-800" />
              </div>
            </div>
          </div>
        )}

        {status === 'notfound' && (
          <div className="rounded-[2rem] border border-white/10 bg-slate-900/90 p-16 text-center shadow-glass">
            <p className="text-sm uppercase tracking-[0.28em] text-cyan-300">Phone not found</p>
            <h1 className="mt-6 text-3xl font-semibold text-white">We couldn&apos;t find that device.</h1>
            <p className="mt-4 text-slate-400">Please try searching for another phone or check the URL.</p>
          </div>
        )}

        {status === 'error' && (
          <div className="rounded-[2rem] border border-rose-500/20 bg-rose-950/80 p-16 text-center shadow-glass">
            <p className="text-sm uppercase tracking-[0.28em] text-rose-300">Error</p>
            <h1 className="mt-6 text-3xl font-semibold text-white">Unable to load phone details.</h1>
            <p className="mt-4 text-rose-300">{errorMessage}</p>
          </div>
        )}

        {status === 'success' && phone && (
          <div className="space-y-10">
            <section className="rounded-[2rem] border border-white/10 bg-slate-900/90 p-8 shadow-glass lg:p-10">
              <div className="grid gap-8 lg:grid-cols-[0.9fr_0.9fr] lg:items-center">
                <div className="overflow-hidden rounded-[2rem] border border-white/10 bg-slate-950/90 shadow-2xl">
                  <img
                    src={phone.image_url || 'https://via.placeholder.com/900x900?text=Phone'}
                    alt={`${phone.brand} ${phone.model}`}
                    className="h-full w-full object-cover"
                  />
                </div>
                <div className="space-y-6">
                  <div>
                    <p className="text-sm uppercase tracking-[0.28em] text-cyan-300">{phone.brand}</p>
                    <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
                      {phone.brand} {phone.model}
                    </h1>
                    {selectedVariant && (
                      <p className="mt-2.5 text-xs text-slate-400 font-medium bg-slate-950/60 px-3 py-1.5 rounded-lg border border-white/5 inline-block">
                        Selected: <span className="text-cyan-300 font-semibold">{selectedVariant.ram_gb}GB RAM + {selectedVariant.storage_gb}GB Storage</span>
                        {selectedVariant.color && <> &bull; <span className="text-slate-300">{selectedVariant.color}</span></>}
                      </p>
                    )}
                  </div>

                  {/* Variant Selection Chips */}
                  {phone.variants && phone.variants.length > 0 && selectedVariant && (
                    <div className="space-y-4 rounded-3xl border border-white/10 bg-slate-950/40 p-5 backdrop-blur-md">
                      <div className="space-y-3.5">
                        {/* RAM options */}
                        {uniqueRAMs.length > 1 && (
                          <div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2">RAM</span>
                            <div className="flex flex-wrap gap-2">
                              {uniqueRAMs.map(ram => {
                                const active = selectedVariant.ram_gb === ram;
                                return (
                                  <button
                                    key={ram}
                                    onClick={() => handleSelectRAM(ram)}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wide border transition-all duration-200 ${
                                      active
                                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.15)] font-bold'
                                        : 'bg-slate-900/50 border-white/5 text-slate-400 hover:border-white/20 hover:text-white'
                                    }`}
                                  >
                                    {ram} GB
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Storage options */}
                        {uniqueStorages.length > 1 && (
                          <div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2">Storage</span>
                            <div className="flex flex-wrap gap-2">
                              {uniqueStorages.map(storage => {
                                const active = selectedVariant.storage_gb === storage;
                                return (
                                  <button
                                    key={storage}
                                    onClick={() => handleSelectStorage(storage)}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wide border transition-all duration-200 ${
                                      active
                                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.15)] font-bold'
                                        : 'bg-slate-900/50 border-white/5 text-slate-400 hover:border-white/20 hover:text-white'
                                    }`}
                                  >
                                    {storage} GB
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Color options */}
                        {uniqueColors.length > 1 && (
                          <div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-2">Color</span>
                            <div className="flex flex-wrap gap-2">
                              {uniqueColors.map(color => {
                                const active = selectedVariant.color === color;
                                return (
                                  <button
                                    key={color}
                                    onClick={() => handleSelectColor(color)}
                                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wide border transition-all duration-200 ${
                                      active
                                        ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.15)] font-bold'
                                        : 'bg-slate-900/50 border-white/5 text-slate-400 hover:border-white/20 hover:text-white'
                                    }`}
                                  >
                                    {color}
                                  </button>
                                );
                              })}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Pricing Hero Section */}
                  <div className="grid gap-4 sm:grid-cols-2">
                    <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-6 flex flex-col justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-400">Launch Price</p>
                        <p className="mt-2 text-3xl font-bold text-slate-300">{formatINR(currentLaunchPrice)}</p>
                      </div>
                    </div>
                    <div className="rounded-3xl border border-cyan-500/20 bg-gradient-to-br from-slate-950/80 to-cyan-950/20 p-6 flex flex-col justify-between relative overflow-hidden group">
                      <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-cyan-500/5 blur-xl rounded-full" />
                      <div>
                        <p className="text-sm font-medium text-slate-400">Best Effective Price</p>
                        <p className="mt-2 text-3xl font-extrabold text-cyan-300">
                          {pricesLoading ? (
                            <span className="text-sm font-normal text-slate-400 animate-pulse">Loading prices...</span>
                          ) : (
                            formatINR(currentBestPrice)
                          )}
                        </p>
                      </div>
                      {priceData?.best_platform && (
                        <p className="text-xs text-slate-400 mt-2">
                          Available on <span className="font-semibold text-slate-200">{priceData.best_platform.platform}</span>
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-3 mt-4">
                    <div className="rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-2 flex items-center gap-2">
                      <span className="text-xs text-slate-400">Discount:</span>
                      <span className="text-sm font-bold text-white">{discountPercent}%</span>
                    </div>

                    {isGreatDeal && (
                      <div className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-4 py-1.5 text-xs font-semibold text-emerald-300">
                        <Sparkles className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
                        Great Deal
                      </div>
                    )}

                    {priceData?.listings && priceData.listings.length > 0 && (
                      <div className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-1.5 text-xs font-semibold text-cyan-300">
                        <ShoppingBag className="h-3.5 w-3.5 text-cyan-400" />
                        Best Offer: {(priceData.listings.filter(l => l.in_stock)[0] || priceData.listings[0]).platform} at {formatINR((priceData.listings.filter(l => l.in_stock)[0] || priceData.listings[0]).final_price)}
                      </div>
                    )}

                    {priceData?.listings?.some(l => l.fake_discount_flag) && (
                      <div className="inline-flex items-center gap-1.5 rounded-full border border-rose-500/25 bg-rose-500/10 px-4 py-1.5 text-xs font-bold text-rose-300 animate-pulse">
                        <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                        Inflation Alert
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </section>

            <DecisionSection slug={slug} />

            {/* Structured & Categorized Specs Section */}
            {phone.spec ? (
              <section className="space-y-6">
                <div className="border-b border-white/10 pb-4">
                  <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                    <span className="h-6 w-1 rounded-full bg-cyan-400" />
                    Device Specifications
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">Categorized and normalized hardware specifications</p>
                </div>
                
                <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                  {(() => {
                    const spec = phone.spec;
                    
                    const renderSpecRow = (label: string, value: string | number | null | undefined) => {
                      if (value === null || value === undefined || value === '') return null;
                      return (
                        <div className="flex justify-between items-start py-2.5 border-b border-white/5 last:border-0 text-sm">
                          <span className="text-slate-400 font-medium mr-2">{label}</span>
                          <span className="text-slate-200 font-semibold text-right break-words max-w-[60%]">{value}</span>
                        </div>
                      );
                    };

                    return (
                      <>
                        {/* 1. Core & Performance */}
                        <div className="rounded-3xl border border-indigo-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-indigo-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                                <Cpu className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-indigo-300">Core & Performance</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Processor", spec.chipset || spec.processor)}
                              {renderSpecRow("RAM Capacity", selectedVariant ? `${selectedVariant.ram_gb} GB` : (spec.ram_gb || spec.ram ? `${spec.ram_gb || spec.ram} GB` : null))}
                              {renderSpecRow("Storage Capacity", selectedVariant ? `${selectedVariant.storage_gb} GB` : (spec.storage_gb || spec.storage ? `${spec.storage_gb || spec.storage} GB` : null))}
                              {renderSpecRow("Storage Tech", spec.ufs_type)}
                              {renderSpecRow("CPU Architecture", spec.cpu)}
                              {renderSpecRow("GPU Processor", spec.gpu)}
                            </div>
                          </div>
                        </div>

                        {/* 2. Display & Visuals */}
                        <div className="rounded-3xl border border-purple-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-purple-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
                                <Tv className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-purple-300">Display & Visuals</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Screen Size & Type", spec.display_size && spec.display_type ? `${spec.display_size}” ${spec.display_type}` : null)}
                              {renderSpecRow("Resolution", spec.display_resolution)}
                              {renderSpecRow("Refresh Rate", spec.refresh_rate_hz || spec.refresh_rate ? `${spec.refresh_rate_hz || spec.refresh_rate} Hz` : null)}
                              
                              {spec.brightness_label ? (
                                <div className="flex justify-between items-start py-2.5 border-b border-white/5 text-sm">
                                  <span className="text-slate-400 font-medium mr-2">Brightness</span>
                                  <div className="text-right">
                                    <span className="text-slate-200 font-semibold block">{spec.brightness_label}</span>
                                    {spec.peak_brightness_nits && (
                                      <span className="text-[11px] text-slate-400 block mt-0.5">
                                        {spec.peak_brightness_nits} nits peak
                                      </span>
                                    )}
                                    {spec.real_world_brightness_nits && (
                                      <span className="text-[11px] text-slate-500 block">
                                        Real-world: {spec.real_world_brightness_nits} nits
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ) : (
                                spec.peak_brightness_nits ? renderSpecRow("Brightness", `${spec.peak_brightness_nits} nits peak`) : null
                              )}
                              
                              {renderSpecRow("Display Glass", spec.display_protection_label || spec.display_protection)}
                              {renderSpecRow("HDR Standard", spec.hdr_label || spec.hdr_support)}
                              {spec.pwm_dimming !== undefined && spec.pwm_dimming !== null && renderSpecRow(
                                "PWM Dimming",
                                spec.pwm_dimming ? "Supported (Reduced Eye Strain)" : "Standard"
                              )}
                            </div>
                          </div>
                        </div>

                        {/* 3. Camera & Optics */}
                        <div className="rounded-3xl border border-rose-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-rose-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
                                <Camera className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-rose-300">Camera & Optics</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Main Camera MP", spec.camera_main_mp ? `${spec.camera_main_mp} MP` : null)}
                              {renderSpecRow("Primary Setup", spec.main_camera)}
                              {renderSpecRow("Ultrawide Lens", spec.ultrawide_camera)}
                              {renderSpecRow("Telephoto Lens", spec.telephoto_camera)}
                              {renderSpecRow("Front Camera", spec.selfie_camera)}
                            </div>
                          </div>
                        </div>

                        {/* 4. Battery & Power */}
                        <div className="rounded-3xl border border-amber-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-amber-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                                <Zap className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-amber-300">Battery & Power</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Battery Capacity", spec.battery_mah ? `${spec.battery_mah} mAh` : null)}
                              {renderSpecRow("Charging Speed", spec.charging_watts ? `${spec.charging_watts}W Wired` : null)}
                              {spec.wireless_charging !== undefined && spec.wireless_charging !== null && renderSpecRow(
                                "Wireless Charging",
                                spec.wireless_charging ? "Supported" : "Not supported"
                              )}
                              {spec.reverse_charging !== undefined && spec.reverse_charging !== null && renderSpecRow(
                                "Reverse Charging",
                                spec.reverse_charging ? "Supported" : "Not supported"
                              )}
                            </div>
                          </div>
                          {phone.interpretation?.battery_summary && (
                            <div className="mt-4 border-t border-white/5 pt-3">
                              <p className="text-[11px] leading-5 text-slate-400 font-medium">
                                {phone.interpretation.battery_summary} 
                                {phone.interpretation.normal_usage && ` (Est: ${phone.interpretation.normal_usage} normal`}
                                {phone.interpretation.heavy_usage && `, ${phone.interpretation.heavy_usage} heavy usage)`}
                              </p>
                            </div>
                          )}
                        </div>

                        {/* 5. Build & Materials */}
                        <div className="rounded-3xl border border-cyan-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-cyan-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                                <Layers className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-cyan-300">Build & Materials</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Materials", spec.build_materials)}
                              {renderSpecRow("Cooling System", spec.cooling_system)}
                              {renderSpecRow("IP Rating", spec.ip_rating)}
                              {renderSpecRow("Weight", spec.weight ? `${spec.weight} grams` : null)}
                            </div>
                          </div>
                        </div>

                        {/* 6. Connectivity & Ports */}
                        <div className="rounded-3xl border border-sky-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-sky-500/30 transition-all duration-300">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400">
                                <Wifi className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-sky-300">Connectivity & Ports</h3>
                            </div>
                            <div className="space-y-1">
                              {renderSpecRow("Wi-Fi Version", spec.wifi_version)}
                              {renderSpecRow("Bluetooth Version", spec.bluetooth_version)}
                              {renderSpecRow("USB Interface", spec.usb_type)}
                              {spec.esim !== undefined && spec.esim !== null && renderSpecRow(
                                "eSIM Support",
                                spec.esim ? "Supported" : "Not supported"
                              )}
                              {spec.nfc !== undefined && spec.nfc !== null && renderSpecRow(
                                "NFC",
                                spec.nfc ? "Supported" : "Not supported"
                              )}
                            </div>
                          </div>
                        </div>

                        {/* 7. Software & AI Intelligence (spans full width on desktop) */}
                        <div className="rounded-3xl border border-emerald-500/10 bg-slate-950/60 p-6 flex flex-col justify-between hover:border-emerald-500/30 transition-all duration-300 sm:col-span-2 lg:col-span-3">
                          <div>
                            <div className="flex items-center gap-3 mb-5">
                              <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                                <Smartphone className="h-5 w-5" />
                              </div>
                              <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-300">Software & AI Intelligence</h3>
                            </div>
                            <div className="grid gap-6 md:grid-cols-2">
                              <div className="space-y-1">
                                {renderSpecRow("Operating System", spec.android_version || "Android")}
                                {spec.ai_suite_name && renderSpecRow("AI Platform Suite", spec.ai_suite_name)}
                                
                                {/* OS & Security updates details */}
                                {(spec.os_updates_years || spec.security_updates_years) && (
                                  <div className="mt-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10 p-4 text-xs space-y-2">
                                    <div className="flex flex-wrap gap-2">
                                      {spec.os_updates_years && (
                                        <span className="font-semibold bg-emerald-500/20 text-emerald-200 px-2 py-1 rounded">
                                          {spec.os_updates_years} Years OS Support
                                        </span>
                                      )}
                                      {spec.security_updates_years && (
                                        <span className="font-semibold bg-cyan-500/20 text-cyan-200 px-2 py-1 rounded">
                                          {spec.security_updates_years} Years Security Support
                                        </span>
                                      )}
                                    </div>
                                    {spec.update_policy_label && (
                                      <p className="text-slate-300 font-medium italic">“{spec.update_policy_label}”</p>
                                    )}
                                  </div>
                                )}
                              </div>
                              
                              {/* AI Features wrap list */}
                              <div>
                                {spec.ai_features && spec.ai_features.length > 0 ? (
                                  <div className="h-full flex flex-col justify-start">
                                    <p className="text-xs text-slate-400 mb-2.5 font-semibold uppercase tracking-wider">AI Intelligence Features</p>
                                    <div className="flex flex-wrap gap-2">
                                      {spec.ai_features.map((feature, idx) => (
                                        <span key={idx} className="text-xs font-semibold bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-3 py-1 rounded-full flex items-center gap-1.5">
                                          <Sparkles className="h-3 w-3 text-emerald-400" />
                                          {feature}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                ) : (
                                  <div className="h-full flex items-center justify-center border border-dashed border-white/5 rounded-2xl p-4">
                                    <p className="text-xs text-slate-500">No specific AI suite or software suite configured.</p>
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </section>
            ) : (
              <section className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 text-center shadow-glass">
                <p className="text-slate-400 text-lg">Specifications are not available yet.</p>
              </section>
            )}

            {/* Real-World Experience Section (Rule-Based) */}
            {phone.interpretation && (
              <section className="space-y-6">
                <div className="border-b border-white/10 pb-4">
                  <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                    <span className="h-6 w-1 rounded-full bg-cyan-400" />
                    Real-World Experience
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">Rule-based assessment based on hardware specs</p>
                </div>

                <div className="grid gap-6 md:grid-cols-2">
                  <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-6 shadow-sm">
                    <p className="text-sm uppercase tracking-[0.18em] text-cyan-300">Expected Experience</p>
                    <p className="mt-4 text-base leading-7 text-slate-300">
                      {phone.interpretation.expected_experience}
                    </p>
                  </div>
                  <div className="rounded-3xl border border-white/10 bg-slate-950/80 p-6 shadow-sm">
                    <p className="text-sm uppercase tracking-[0.18em] text-cyan-300">Verdict</p>
                    <p className="mt-4 text-base leading-7 text-slate-300">
                      {phone.interpretation.verdict}
                    </p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Pros */}
                  {phone.interpretation.pros && phone.interpretation.pros.length > 0 && (
                    <div className="rounded-3xl bg-emerald-500/5 border border-emerald-500/10 p-6">
                      <h3 className="text-sm font-semibold uppercase tracking-wider text-emerald-300 mb-4 flex items-center gap-2">
                        <svg className="h-5 w-5 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Hardware Strengths
                      </h3>
                      <ul className="space-y-3">
                        {phone.interpretation.pros.map((pro, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                            <span className="text-emerald-400 font-bold shrink-0">•</span>
                            <span>{pro}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Cons */}
                  {phone.interpretation.cons && phone.interpretation.cons.length > 0 && (
                    <div className="rounded-3xl bg-rose-500/5 border border-rose-500/10 p-6">
                      <h3 className="text-sm font-semibold uppercase tracking-wider text-rose-300 mb-4 flex items-center gap-2">
                        <svg className="h-5 w-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Hardware Limitations
                      </h3>
                      <ul className="space-y-3">
                        {phone.interpretation.cons.map((con, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-slate-300">
                            <span className="text-rose-400 font-bold shrink-0">•</span>
                            <span>{con}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </section>
            )}

            {phone.insight ? (
              <>
                <section className="grid gap-4 md:grid-cols-2">
                  {[
                    { title: 'Battery', text: phone.insight.battery_summary },
                    { title: 'Performance', text: phone.insight.performance_summary },
                    { title: 'Display', text: phone.insight.display_summary },
                    { title: 'Camera', text: phone.insight.camera_summary },
                    { title: 'Software', text: phone.insight.software_summary },
                  ].map((item) => (
                    <div key={item.title} className="rounded-3xl border border-white/10 bg-slate-950/80 p-6 shadow-sm">
                      <p className="text-sm uppercase tracking-[0.18em] text-cyan-300">{item.title}</p>
                      <p className="mt-4 text-base leading-7 text-slate-300">{item.text}</p>
                    </div>
                  ))}
                </section>

                <section className="rounded-[2rem] border border-cyan-400/10 bg-cyan-500/10 p-8 shadow-glass">
                  <div className="flex items-center gap-3 text-cyan-300">
                    <Sparkles className="h-5 w-5" />
                    <p className="text-sm uppercase tracking-[0.28em]">Brutally honest verdict</p>
                  </div>
                  <p className="mt-6 text-xl leading-9 text-slate-100">{phone.insight.honest_verdict}</p>
                </section>
              </>
            ) : (
              <section className="rounded-[2rem] border border-white/10 bg-slate-900/80 p-8 text-center shadow-glass">
                <p className="text-slate-400 text-lg">Insights are not available yet.</p>
                <button
                  onClick={handleGenerateInsights}
                  disabled={isGenerating}
                  className="mt-6 inline-flex items-center gap-2 rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/20 hover:bg-cyan-400 disabled:opacity-50 transition"
                >
                  <Sparkles className="h-4 w-4" />
                  {isGenerating ? 'Generating Insights...' : 'Generate Insights Now'}
                </button>
              </section>
            )}

            {/* Price Comparison Section */}
            {priceData && <PriceComparisonSection data={priceData} />}
          </div>
        )}
      </div>
    </main>
  );
}
