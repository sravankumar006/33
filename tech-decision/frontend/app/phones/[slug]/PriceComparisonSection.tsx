'use client';

import { ShoppingBag, Truck, ArrowUpRight, Tag, AlertCircle, Sparkles, AlertTriangle, CreditCard } from 'lucide-react';
import type { PriceComparisonResponse } from './types';

interface PriceComparisonSectionProps {
  data: PriceComparisonResponse;
}

export default function PriceComparisonSection({ data }: PriceComparisonSectionProps) {
  const { listings, best_platform, summary } = data;

  if (!listings || listings.length === 0) {
    return (
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8 text-center backdrop-blur-sm">
        <AlertCircle className="mx-auto mb-3 h-10 w-10 text-slate-500" />
        <h3 className="text-lg font-semibold text-slate-300">No Listings Available</h3>
        <p className="mt-1 text-sm text-slate-400">We couldn&apos;t find any live prices for this device right now. Please check back later.</p>
      </div>
    );
  }

  // Get color for platform
  const getPlatformStyle = (platform: string) => {
    const p = platform.toLowerCase();
    if (p.includes('amazon')) {
      return {
        bg: 'bg-amber-500/10 border-amber-500/20 hover:border-amber-500/40 text-amber-400',
        badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
        btn: 'bg-amber-500 hover:bg-amber-600 text-slate-950',
      };
    }
    if (p.includes('flipkart')) {
      return {
        bg: 'bg-blue-500/10 border-blue-500/20 hover:border-blue-500/40 text-blue-400',
        badge: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
        btn: 'bg-blue-500 hover:bg-blue-600 text-white',
      };
    }
    if (p.includes('croma')) {
      return {
        bg: 'bg-teal-500/10 border-teal-500/20 hover:border-teal-500/40 text-teal-400',
        badge: 'bg-teal-500/20 text-teal-300 border-teal-500/30',
        btn: 'bg-teal-500 hover:bg-teal-600 text-slate-950',
      };
    }
    if (p.includes('reliance')) {
      return {
        bg: 'bg-red-500/10 border-red-500/20 hover:border-red-500/40 text-red-400',
        badge: 'bg-red-500/20 text-red-300 border-red-500/30',
        btn: 'bg-red-500 hover:bg-red-600 text-white',
      };
    }
    return {
      bg: 'bg-slate-800/50 border-slate-700/50 hover:border-slate-600/80 text-slate-300',
      badge: 'bg-slate-800 text-slate-300 border-slate-700',
      btn: 'bg-slate-700 hover:bg-slate-600 text-white',
    };
  };

  // Get color for trust score
  const getTrustScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    if (score >= 80) return 'text-teal-400 bg-teal-500/10 border-teal-500/20';
    if (score >= 70) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
  };

  // Get color for authenticity score
  const getAuthenticityColor = (score: number) => {
    if (score >= 85) return { text: 'text-emerald-400', bar: 'bg-emerald-500', label: 'Authentic Deal' };
    if (score >= 60) return { text: 'text-amber-400', bar: 'bg-amber-500', label: 'Artificially Inflated' };
    return { text: 'text-rose-400', bar: 'bg-rose-500', label: 'Misleading Discount' };
  };

  return (
    <section className="mt-16 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-100 sm:text-3xl flex items-center gap-2">
            <ShoppingBag className="h-7 w-7 text-cyan-400" />
            Best Prices Right Now
          </h2>
          <p className="mt-2 text-slate-400 max-w-2xl">
            Live prices from major e-commerce platforms. Offers, discounts, and seller trust are factored in for recommendations.
          </p>
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-1.5 self-start md:self-end">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          Live Price Feed Active
        </div>
      </div>

      {/* Recommendation Summary Card */}
      {best_platform && (
        <div className="relative overflow-hidden rounded-2xl border border-cyan-500/30 bg-gradient-to-r from-slate-900 via-cyan-950/20 to-slate-900 p-6 backdrop-blur-md shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)]">
          <div className="absolute top-0 right-0 h-40 w-40 bg-cyan-500/5 blur-3xl rounded-full pointer-events-none" />
          <div className="flex flex-col sm:flex-row gap-5 items-start">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <Sparkles className="h-6 w-6" />
            </div>
            <div className="space-y-2">
              <span className="text-xs font-semibold tracking-wider uppercase text-cyan-400">Antigravity Smart Recommendation</span>
              <h3 className="text-lg font-bold text-slate-100">
                Buy from <span className="text-cyan-300 font-extrabold">{best_platform.platform}</span>
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">{summary}</p>
            </div>
          </div>
        </div>
      )}

      {/* Grid of Listings */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {listings.map((listing) => {
          const isBest = best_platform?.id === listing.id;
          const styles = getPlatformStyle(listing.platform);
          const trustColor = getTrustScoreColor(listing.trust_score);
          const auth = getAuthenticityColor(listing.discount_authenticity_score ?? 100);
          
          const couponDiscount = listing.coupon_discount ?? 0;
          const bankDiscount = listing.bank_discount ?? 0;
          const exchangeBonus = listing.exchange_bonus ?? 0;
          const cashbackAmount = listing.cashback_amount ?? 0;
          const deliveryCharge = listing.delivery_charge ?? 0;
          const savings = couponDiscount + bankDiscount + exchangeBonus;

          return (
            <div
              key={listing.id}
              className={`group relative flex flex-col justify-between rounded-2xl border bg-slate-900/60 p-6 transition-all duration-300 hover:-translate-y-1 ${
                isBest
                  ? 'border-cyan-500/60 bg-gradient-to-b from-slate-900 to-cyan-950/20 shadow-[0_0_20px_-5px_rgba(6,182,212,0.2)]'
                  : 'border-slate-800 hover:border-slate-700/80 hover:bg-slate-900/80'
              }`}
            >
              {/* Highlight Ribbon */}
              {isBest && (
                <div className="absolute -top-3 left-6 flex items-center gap-1 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-950 shadow-md animate-pulse">
                  <Sparkles className="h-3 w-3" /> Best Choice
                </div>
              )}

              <div className="space-y-4">
                {/* Platform & Stock */}
                <div className="flex items-center justify-between">
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-md border ${styles.badge}`}>
                    {listing.platform}
                  </span>
                  {!listing.in_stock && (
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-500/10 border border-rose-500/20 text-rose-400">
                      Out of Stock
                    </span>
                  )}
                </div>

                {/* Pricing Block */}
                <div className="space-y-2">
                  <div className="flex flex-col">
                    {/* Original MRP with strike-through & Inflation Alert */}
                    {listing.original_mrp && listing.original_mrp > listing.listed_price ? (
                      <span className={`text-[11px] text-slate-500 line-through flex items-center gap-1 ${
                        listing.fake_discount_flag ? 'decoration-rose-500/50 decoration-[1.5px]' : ''
                      }`}>
                        MRP: ₹{listing.original_mrp.toLocaleString('en-IN')}
                        {listing.fake_discount_flag && (
                          <span className="text-[9px] text-amber-400 font-medium px-1 bg-amber-500/10 border border-amber-500/20 rounded">
                            Inflated
                          </span>
                        )}
                      </span>
                    ) : null}
                    
                    <div className="flex items-baseline gap-2 mt-0.5">
                      <span className="text-3xl font-extrabold text-slate-100">
                        ₹{listing.final_price.toLocaleString('en-IN')}
                      </span>
                      {listing.listed_price > listing.final_price && (
                        <span className="text-xs text-slate-400 line-through">
                          ₹{listing.listed_price.toLocaleString('en-IN')}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Savings / Cashback badge */}
                  <div className="flex flex-wrap gap-1.5">
                    {savings > 0 && (
                      <div className="inline-flex items-center gap-1 text-[10px] font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/10">
                        <Tag className="h-3 w-3" />
                        Save ₹{savings.toLocaleString('en-IN')}
                      </div>
                    )}
                    {cashbackAmount > 0 && (
                      <div className="inline-flex items-center gap-1 text-[10px] font-medium text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/10">
                        <span>💳 +₹{cashbackAmount.toLocaleString('en-IN')} Cashback</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Deal Authenticity Score (Visual progress bar) */}
                <div className="space-y-1.5 border-t border-slate-800/80 pt-3">
                  <div className="flex justify-between text-[10px]">
                    <span className="text-slate-400 font-medium">Deal Authenticity</span>
                    <span className={`font-semibold ${auth.text}`}>{listing.discount_authenticity_score ?? 100}%</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden border border-white/5">
                    <div className={`h-full ${auth.bar}`} style={{ width: `${listing.discount_authenticity_score ?? 100}%` }} />
                  </div>
                  {listing.fake_discount_flag && (
                    <div className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-400 mt-1">
                      <AlertTriangle className="h-3 w-3 text-amber-400 animate-pulse" />
                      MRP inflated vs official launch
                    </div>
                  )}
                </div>

                {/* Details list */}
                <div className="space-y-2 border-t border-slate-800/80 pt-3 text-xs">
                  {/* Seller Info */}
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Seller</span>
                    <span className="font-medium text-slate-300 truncate max-w-[120px] text-right" title={listing.seller_name}>
                      {listing.seller_name}
                    </span>
                  </div>

                  {/* Trust Score */}
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Seller Trust</span>
                    <span className={`font-semibold px-1.5 py-0.5 rounded text-[10px] border ${trustColor}`}>
                      {listing.trust_score}% Trust
                    </span>
                  </div>

                  {/* Delivery ETA */}
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Delivery</span>
                    <span className="font-medium text-slate-300 flex items-center gap-1">
                      <Truck className="h-3 w-3 text-slate-400" />
                      {listing.delivery_eta_days !== null && listing.delivery_eta_days !== undefined
                        ? `${listing.delivery_eta_days} ${listing.delivery_eta_days === 1 ? 'day' : 'days'}`
                        : 'Contact Seller'}
                    </span>
                  </div>

                  {/* EMI Availability */}
                  {listing.emi_available && (
                    <div className="flex justify-between items-center text-slate-400">
                      <span>EMI Option</span>
                      <span className="font-medium text-slate-300 flex items-center gap-1 text-[10px] bg-slate-950/60 px-1.5 py-0.5 rounded border border-white/5">
                        <CreditCard className="h-3 w-3 text-cyan-400" />
                        From ₹{Math.round(listing.final_price / (listing.emi_months || 12)).toLocaleString('en-IN')}/mo
                      </span>
                    </div>
                  )}
                </div>

                {/* Full Offer Breakdown Detail */}
                <div className="space-y-1.5 rounded-lg bg-slate-950/40 p-2.5 text-[10px] text-slate-400 border border-slate-900">
                  <span className="font-medium text-slate-400 uppercase tracking-wider block mb-1">Pricing Breakdown</span>
                  <div className="flex justify-between">
                    <span>Listed Price</span>
                    <span className="text-slate-300">₹{listing.listed_price.toLocaleString('en-IN')}</span>
                  </div>
                  {couponDiscount > 0 && (
                    <div className="flex justify-between text-emerald-400">
                      <span>Coupon Discount</span>
                      <span>-₹{couponDiscount.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                  {bankDiscount > 0 && (
                    <div className="flex justify-between text-emerald-400">
                      <span>Bank Offer</span>
                      <span>-₹{bankDiscount.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                  {exchangeBonus > 0 && (
                    <div className="flex justify-between text-emerald-400">
                      <span>Exchange Bonus</span>
                      <span>-₹{exchangeBonus.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                  {cashbackAmount > 0 && (
                    <div className="flex justify-between text-cyan-400 font-medium">
                      <span>Cashback</span>
                      <span>-₹{cashbackAmount.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                  {deliveryCharge > 0 && (
                    <div className="flex justify-between text-rose-400">
                      <span>Delivery Fee</span>
                      <span>+₹{deliveryCharge.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                  <div className="flex justify-between border-t border-slate-800/80 pt-1 font-bold text-slate-200">
                    <span>Final Effective</span>
                    <span className="text-cyan-300">₹{listing.final_price.toLocaleString('en-IN')}</span>
                  </div>
                </div>

                {/* Price Intelligence Note */}
                {listing.price_intelligence_note && (
                  <p className="text-[10px] leading-relaxed text-slate-400 bg-slate-950/40 border border-slate-800/60 rounded-lg p-2 mt-2">
                    {listing.price_intelligence_note}
                  </p>
                )}
              </div>

              {/* Action Button */}
              <div className="mt-6 pt-2">
                <a
                  href={listing.product_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`w-full py-2 px-4 rounded-xl font-semibold text-xs flex items-center justify-center gap-1.5 transition-all shadow-sm ${styles.btn}`}
                >
                  Go to Store
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
