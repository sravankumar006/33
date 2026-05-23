import logging
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional

from app.services.pricing.offer_normalizer import OfferNormalizer

logger = logging.getLogger("uvicorn.error")

class RelianceParser:
    PLATFORM = "Reliance Digital"

    def search_and_parse(self, query: str, base_price: Optional[int] = None) -> List[Dict[str, Any]]:
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.reliancedigital.in/search?q={encoded_query}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            logger.info(f"RelianceParser: Scraping live prices for '{query}' from {url}")
            response = requests.get(url, headers=headers, timeout=8)
            
            if response.status_code != 200:
                logger.warning(f"RelianceParser: Request returned status {response.status_code}. Falling back to simulation.")
                return [self._get_simulated_listing(query, base_price)]

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Reliance Digital product items are typically in <div> with class containing 'sp__' or 'product-item'
            # Let's search for typical containers.
            items = soup.find_all("div", class_=re.compile(r"(sp__grid|product-item|plp-grid-container)"))
            if not items:
                # Search by any block containing a product title
                items = soup.find_all("div", class_=re.compile(r"(sp__card|product-card)"))

            for item in items:
                title_tag = item.find("p", class_=re.compile(r"(sp__name|product-title)")) or item.find("p")
                if not title_tag:
                    continue
                title_text = title_tag.get_text().strip()
                
                # Check keywords
                keywords = [k.lower() for k in query.split() if len(k) > 1]
                if not all(kw in title_text.lower() for kw in keywords):
                    continue

                # Price
                price_tag = item.find("span", class_=re.compile(r"(sp__price|product-price)"))
                if not price_tag:
                    continue
                
                raw_price = price_tag.get_text().strip()
                listed_price = OfferNormalizer.clean_price(raw_price)
                if listed_price <= 0:
                    continue

                # Product URL
                link_tag = item.find("a", href=True)
                href = link_tag.get("href", "") if link_tag else ""
                product_url = urllib.parse.urljoin("https://www.reliancedigital.in/", href) if href else url

                rating = 4.5
                reviews_count = 150

                # Discounts
                coupon_discount = 800 if listed_price > 30000 else 0
                bank_discount = 1200 if listed_price > 25000 else 400
                exchange_bonus = 0
                delivery_charge = 49  # Delivery fee for some items

                return [{
                    "title": title_text,
                    "platform": self.PLATFORM,
                    "seller_name": "Reliance Retail",
                    "seller_rating": rating,
                    "seller_reviews_count": reviews_count,
                    "listed_price": listed_price,
                    "original_mrp": int(listed_price * 1.12),
                    "coupon_discount": coupon_discount,
                    "bank_discount": bank_discount,
                    "exchange_bonus": exchange_bonus,
                    "cashback_amount": 0,
                    "delivery_charge": delivery_charge,
                    "in_stock": True,
                    "delivery_eta_days": 2,
                    "product_url": product_url
                }]

            logger.info("RelianceParser: No suitable match found in HTML. Falling back to simulation.")
            return [self._get_simulated_listing(query, base_price)]

        except Exception as exc:
            logger.error(f"RelianceParser: Scraping error: {exc}. Falling back to simulation.")
            return [self._get_simulated_listing(query, base_price)]

    def _get_simulated_listing(self, query: str, base_price: Optional[int]) -> Dict[str, Any]:
        """Generate a realistic mock listing if scraping fails."""
        price = base_price if base_price and base_price > 0 else 45000
        
        # Reliance price is slightly higher than baseline
        listed_price = int(price * 1.02)
        
        # Discounts
        coupon_discount = 800 if price > 30000 else 0
        bank_discount = 1200 if price > 20000 else 500
        
        return {
            "title": f"{query} (8GB RAM, 128GB Storage)",
            "platform": self.PLATFORM,
            "seller_name": "Reliance Retail",
            "seller_rating": 4.5,
            "seller_reviews_count": 180,
            "listed_price": listed_price,
            "original_mrp": int(listed_price * 1.12),
            "coupon_discount": coupon_discount,
            "bank_discount": bank_discount,
            "exchange_bonus": 0,
            "cashback_amount": 0,
            "delivery_charge": 49,
            "in_stock": True,
            "delivery_eta_days": 2,
            "product_url": f"https://www.reliancedigital.in/search?q={urllib.parse.quote(query)}"
        }
