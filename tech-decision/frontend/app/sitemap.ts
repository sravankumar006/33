import type { MetadataRoute } from 'next';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'http://localhost:8000';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000';

  const routes = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily' as const,
      priority: 1.0,
    },
  ];

  try {
    const res = await fetch(`${API_URL}/api/phones`, {
      next: { revalidate: 3600 },
    });

    if (res.ok) {
      const phones = await res.json();
      const phoneRoutes = phones.map((phone: any) => ({
        url: `${baseUrl}/phones/${phone.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.8,
      }));
      return [...routes, ...phoneRoutes];
    }
  } catch (error) {
    console.error("Failed to generate sitemap routes:", error);
  }

  return routes;
}
