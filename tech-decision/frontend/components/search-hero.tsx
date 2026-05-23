'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Search } from 'lucide-react';

interface PhoneSearchResult {
  brand: string;
  model: string;
  slug: string;
  image_url?: string | null;
  current_avg_price: number | null;
  match_score?: number;
}

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'http://localhost:8000';

const formatINR = (value: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value);

export default function SearchHero() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<PhoneSearchResult[]>([]);
  const [status, setStatus] = useState<'idle' | 'loading' | 'empty' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cacheRef = useRef<Record<string, PhoneSearchResult[]>>({});
  const listContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setActiveIndex(-1);
  }, [query, results]);

  useEffect(() => {
    if (activeIndex >= 0 && listContainerRef.current) {
      const activeEl = listContainerRef.current.children[activeIndex] as HTMLElement;
      if (activeEl) {
        activeEl.scrollIntoView({
          block: 'nearest',
        });
      }
    }
  }, [activeIndex]);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults([]);
      setStatus('idle');
      return;
    }

    const controller = new AbortController();

    const fetchResults = async () => {
      if (cacheRef.current[trimmed]) {
        const cachedData = cacheRef.current[trimmed];
        console.log("SearchHero: Cache hit for query =", trimmed);
        setResults(cachedData);
        setStatus(cachedData.length === 0 ? 'empty' : 'idle');
        setShowDropdown(true);
        return;
      }

      setStatus('loading');
      setErrorMessage('');

      const url = `${API_URL}/api/discovery/search?q=${encodeURIComponent(trimmed)}`;
      console.log("SearchHero: API_URL =", API_URL);
      console.log("SearchHero: fetching url =", url);

      try {
        const response = await fetch(
          url,
          {
            signal: controller.signal,
          },
        );

        if (!response.ok) {
          throw new Error(`Search request failed with status: ${response.status}`);
        }

        const data: PhoneSearchResult[] = await response.json();
        console.log("SearchHero: fetch success, results count =", data.length);
        
        cacheRef.current[trimmed] = data;
        
        setResults(data);
        setStatus(data.length === 0 ? 'empty' : 'idle');
        setShowDropdown(true);
      } catch (err) {
        if (controller.signal.aborted) {
          console.log("SearchHero: fetch aborted");
          return;
        }

        console.error("SearchHero: fetch error =", err);
        setResults([]);
        setStatus('error');
        setErrorMessage('Unable to fetch search results. Please try again.');
        setShowDropdown(true);
      }
    };

    timeoutRef.current = setTimeout(fetchResults, 300);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      controller.abort();
    };
  }, [query]);

  return (
    <section className="relative isolate overflow-hidden px-6 py-20 sm:px-10 lg:px-16">
      <div className="mx-auto max-w-7xl">
        <div className="rounded-[2rem] bg-slate-900/90 p-10 shadow-glass ring-1 ring-white/10 backdrop-blur-xl sm:p-14">
          <div className="mx-auto max-w-4xl text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-300">Tech deal intelligence</p>
            <h1 className="mt-6 text-4xl font-semibold tracking-tight text-white sm:text-6xl">
              Find the Best Tech Deal
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
              Compare prices, understand specs, and get brutally honest buying advice.
            </p>
          </div>

          <div className="mt-14 grid gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-end">
            <div className="relative rounded-4xl border border-white/10 bg-slate-950/90 p-8 shadow-xl ring-1 ring-white/5">
              <div className="mb-6 flex items-center gap-3 text-slate-400">
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-cyan-500/10 text-cyan-300">
                  <Search className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Search phones</p>
                  <p className="text-sm text-slate-500">Type at least 2 characters to find matching phones.</p>
                </div>
              </div>

              <label htmlFor="phone-search" className="sr-only">
                Search for a phone
              </label>
              <div className="relative">
                <input
                  id="phone-search"
                  type="search"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  onFocus={() => setShowDropdown(true)}
                  onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
                  onKeyDown={(e) => {
                    const displayedResults = results.slice(0, 15);
                    const length = displayedResults.length;
                    
                    if (e.key === 'ArrowDown') {
                      e.preventDefault();
                      if (length > 0) {
                        setActiveIndex((prev) => (prev + 1) % length);
                      }
                    } else if (e.key === 'ArrowUp') {
                      e.preventDefault();
                      if (length > 0) {
                        setActiveIndex((prev) => (prev - 1 + length) % length);
                      }
                    } else if (e.key === 'Enter') {
                      if (activeIndex >= 0 && displayedResults[activeIndex]) {
                        e.preventDefault();
                        const targetPhone = displayedResults[activeIndex];
                        console.log("Navigating via Enter key to slug:", targetPhone.slug);
                        router.push(`/phones/${targetPhone.slug}`);
                        setShowDropdown(false);
                      }
                    } else if (e.key === 'Escape') {
                      e.preventDefault();
                      setShowDropdown(false);
                    }
                  }}
                  placeholder="Search for a phone..."
                  className="w-full rounded-[2rem] border border-white/10 bg-slate-900 px-5 py-4 pr-14 text-sm text-white placeholder:text-slate-500 focus:border-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400/20"
                />
                <div className="pointer-events-none absolute inset-y-0 right-5 flex items-center text-slate-500">
                  <Search className="h-4 w-4" />
                </div>
              </div>

              <div className="mt-4 min-h-[2rem] text-sm text-slate-400">
                {query.trim().length > 0 && query.trim().length < 2 && (
                  <span>Enter at least 2 characters to search.</span>
                )}
                {status === 'loading' && <span>Searching...</span>}
              </div>

              {showDropdown && (status !== 'idle' || results.length > 0) && (
                <div className="absolute left-0 right-0 top-[calc(100%+1rem)] z-20 rounded-3xl border border-white/10 bg-slate-950/95 p-4 shadow-xl backdrop-blur-xl">
                  {status === 'loading' && (
                    <div className="rounded-3xl bg-slate-900 p-6 text-center text-slate-300">
                      Searching...
                    </div>
                  )}
                  {status === 'empty' && (
                    <div className="rounded-3xl bg-slate-900 p-6 text-center text-slate-300">
                      No phones found.
                    </div>
                  )}
                  {status === 'error' && (
                    <div className="rounded-3xl bg-rose-950 p-6 text-center text-rose-300">
                      {errorMessage}
                    </div>
                  )}
                  {results.length > 0 && (
                    <div
                      ref={listContainerRef}
                      className="space-y-3 max-h-[380px] overflow-y-auto custom-scrollbar pr-1"
                    >
                      {results.slice(0, 15).map((phone, index) => {
                        const isActive = activeIndex === index;
                        const isHighMatch = phone.match_score !== undefined && phone.match_score >= 90;
                        return (
                          <Link
                            key={phone.slug}
                            href={`/phones/${phone.slug}`}
                            onMouseDown={(e) => {
                              // Prevent input blur before click registers
                              e.preventDefault();
                            }}
                            onClick={() => {
                              console.log("Navigating to slug:", phone.slug);
                            }}
                            className={`group flex items-center justify-between gap-4 rounded-3xl border p-4 transition duration-200 hover:-translate-y-0.5 ${
                              isActive
                                ? 'border-cyan-400 bg-slate-800 ring-2 ring-cyan-400/20'
                                : isHighMatch
                                  ? 'border-cyan-500/30 bg-slate-900/95 hover:border-cyan-400/40 hover:bg-slate-900'
                                  : 'border-white/10 bg-slate-900/95 hover:border-cyan-400/30 hover:bg-slate-900'
                            }`}
                          >
                            <div className="flex items-center gap-4">
                              <div className="h-16 w-16 overflow-hidden rounded-3xl bg-slate-800 ring-1 ring-white/10">
                                <img
                                  src={phone.image_url || 'https://via.placeholder.com/160?text=Phone'}
                                  alt={`${phone.brand} ${phone.model}`}
                                  className="h-full w-full object-cover"
                                />
                              </div>
                              <div>
                                <div className="flex flex-wrap items-center gap-2">
                                  <p className="font-semibold text-white">{phone.brand} {phone.model}</p>
                                  {isHighMatch && (
                                    <span className="inline-flex items-center rounded-md bg-cyan-400/10 px-2 py-0.5 text-[10px] font-semibold text-cyan-300 ring-1 ring-inset ring-cyan-400/20">
                                      Best Match
                                    </span>
                                  )}
                                </div>
                                <div className="flex items-center gap-3 mt-1">
                                  <p className="text-sm text-slate-400">
                                    {phone.current_avg_price ? formatINR(phone.current_avg_price) : 'Price pending'}
                                  </p>
                                  {phone.match_score !== undefined && (
                                    <span className="text-[10px] uppercase tracking-wider text-slate-500 font-medium">
                                      Match: {phone.match_score}%
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                            <ArrowRight className="h-5 w-5 text-cyan-300 transition group-hover:translate-x-1" />
                          </Link>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>

            <div className="rounded-[2rem] bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 p-8 shadow-2xl ring-1 ring-white/10 sm:p-10">
              <div className="rounded-3xl border border-white/5 bg-white/5 p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-300">Why Tech Decision</p>
                <ul className="mt-6 space-y-4 text-slate-300">
                  <li className="rounded-3xl border border-white/5 bg-slate-950/80 p-4">
                    <strong className="block text-white">Curated price insights</strong>
                    Compare market pricing for the products that matter.
                  </li>
                  <li className="rounded-3xl border border-white/5 bg-slate-950/80 p-4">
                    <strong className="block text-white">Spec-driven advice</strong>
                    Understand the tradeoffs behind every recommendation.
                  </li>
                  <li className="rounded-3xl border border-white/5 bg-slate-950/80 p-4">
                    <strong className="block text-white">Premium buying experience</strong>
                    Designed for buyers who want data and style.
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
