import type { Metadata } from 'next';

import PhoneDetailClient from './PhoneDetailClient';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'http://localhost:8000';

interface PhonePageProps {
  params: Promise<{
    slug: string;
  }>;
}

async function getPhoneDetails(slug: string) {
  try {
    const response = await fetch(`${API_URL}/api/phones/${encodeURIComponent(slug)}`, {
      next: { revalidate: 3600 },
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching phone in generateMetadata:", error);
    return null;
  }
}

async function getPhonePrices(slug: string) {
  try {
    const response = await fetch(`${API_URL}/api/phones/${encodeURIComponent(slug)}/prices`, {
      next: { revalidate: 3600 },
    });

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error("Error fetching phone prices in JSON-LD:", error);
    return null;
  }
}

export async function generateMetadata({ params }: PhonePageProps): Promise<Metadata> {
  const { slug } = await params;
  const phone = await getPhoneDetails(slug);

  if (!phone) {
    return {
      title: 'Phone Details | Tech Decision',
      description: 'Find honest phone specifications and comparisons on Tech Decision.',
    };
  }

  const title = `${phone.brand} ${phone.model} - Verdict, Deals & Specs`;
  const description = `Specs, honest verdicts, and price comparisons for ${phone.brand} ${phone.model}. Launched at ₹${phone.launch_price?.toLocaleString('en-IN') || 'pending'}. Detect fake discounts.`;
  const imageUrl = phone.image_url || '/og-image.jpg';

  return {
    title,
    description,
    openGraph: {
      title: `${phone.brand} ${phone.model} Deal Analysis`,
      description,
      type: 'website',
      url: `/phones/${slug}`,
      images: [
        {
          url: imageUrl,
          alt: `${phone.brand} ${phone.model}`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${phone.brand} ${phone.model} | Tech Decision`,
      description,
      images: [imageUrl],
    },
    alternates: {
      canonical: `/phones/${slug}`,
    },
  };
}

export default async function PhoneDetailPage({ params }: PhonePageProps) {
  const { slug } = await params;
  const phone = await getPhoneDetails(slug);

  if (!phone) {
    console.log("PHONE FETCH FAILED", slug);
    return (
      <main className="min-h-screen bg-slate-950 px-6 py-20 text-slate-100 flex items-center justify-center">
        <div className="max-w-md w-full rounded-[2rem] border border-rose-500/20 bg-rose-950/40 p-8 text-center backdrop-blur-xl shadow-glass">
          <p className="text-xs uppercase tracking-[0.2em] text-rose-400 font-bold">Debug Mode</p>
          <h1 className="mt-4 text-2xl font-semibold text-white">Phone Fetch Failed</h1>
          <p className="mt-2 text-sm text-slate-400">Could not retrieve details for:</p>
          <div className="mt-2 inline-block rounded-xl bg-black/40 px-3 py-1.5 font-mono text-xs text-rose-300 border border-white/5">
            {slug}
          </div>
          <div className="mt-6 text-left text-xs text-slate-400 space-y-2 border-t border-white/5 pt-4">
            <p className="font-semibold text-slate-300">Possible Causes:</p>
            <ul className="list-disc pl-4 space-y-1">
              <li>Empty database in production</li>
              <li>Missing or incorrect <code className="text-cyan-300 font-mono">NEXT_PUBLIC_API_URL</code> environment variable</li>
              <li>Backend service is down or inaccessible from server component</li>
            </ul>
          </div>
        </div>
      </main>
    );
  }

  const prices = await getPhonePrices(slug);

  let jsonLd: Record<string, any> | null = null;

  if (phone) {
    jsonLd = {
      '@context': 'https://schema.org',
      '@type': 'Product',
      name: `${phone.brand} ${phone.model}`,
      image: phone.image_url || undefined,
      description: `Specifications, real-time prices, fake discount detector warning scores, and honest AI verdicts for the ${phone.brand} ${phone.model}.`,
      brand: {
        '@type': 'Brand',
        name: phone.brand,
      },
    };

    if (phone.spec) {
      jsonLd.additionalProperty = [
        {
          '@type': 'PropertyValue',
          name: 'Processor',
          value: phone.spec.processor || phone.spec.chipset || undefined,
        },
        {
          '@type': 'PropertyValue',
          name: 'RAM',
          value: phone.spec.ram_gb ? `${phone.spec.ram_gb} GB` : undefined,
        },
        {
          '@type': 'PropertyValue',
          name: 'Storage',
          value: phone.spec.storage_gb ? `${phone.spec.storage_gb} GB` : undefined,
        },
        {
          '@type': 'PropertyValue',
          name: 'Battery',
          value: phone.spec.battery_mah ? `${phone.spec.battery_mah} mAh` : undefined,
        },
      ].filter((p) => p.value !== undefined);
    }

    if (prices && prices.listings && prices.listings.length > 0) {
      const validPrices = prices.listings
        .filter((l: any) => l.final_price && l.final_price > 0)
        .map((l: any) => l.final_price);

      if (validPrices.length > 0) {
        const lowPrice = Math.min(...validPrices);
        const highPrice = Math.max(...validPrices);

        jsonLd.offers = {
          '@type': 'AggregateOffer',
          priceCurrency: 'INR',
          lowPrice: lowPrice,
          highPrice: highPrice,
          offerCount: prices.listings.length,
          offers: prices.listings.map((l: any) => ({
            '@type': 'Offer',
            price: l.final_price,
            priceCurrency: 'INR',
            url: l.product_url || undefined,
            itemCondition: 'https://schema.org/NewCondition',
            availability: l.in_stock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
            seller: {
              '@type': 'Organization',
              name: l.platform,
            },
          })),
        };
      }
    } else if (phone.current_avg_price || phone.launch_price) {
      const priceVal = phone.current_avg_price || phone.launch_price;
      jsonLd.offers = {
        '@type': 'Offer',
        price: priceVal,
        priceCurrency: 'INR',
        itemCondition: 'https://schema.org/NewCondition',
        availability: 'https://schema.org/InStock',
      };
    }
  }

  return (
    <>
      {jsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      )}
      <PhoneDetailClient slug={slug} />
    </>
  );
}
