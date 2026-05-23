import logging
import time
from typing import List, Dict, Any
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

from app.providers.base_provider import BaseProvider

logger = logging.getLogger("uvicorn.error")

class GSMArenaProvider(BaseProvider):
    BASE_URL = "https://www.gsmarena.com/"
    SEARCH_URL = "https://www.gsmarena.com/results.php3"

    def __init__(self, timeout: int = 10, max_retries: int = 3, backoff_factor: float = 0.5):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    def _make_request(self, url: str, params: Dict[str, Any] = None) -> requests.Response:
        """Make HTTP GET requests with retries and timeout handling."""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"GSMArenaProvider: Requesting URL={url} with params={params} (attempt {attempt + 1})")
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_exception = exc
                logger.warning(f"GSMArenaProvider: Request failed (attempt {attempt + 1}): {exc}")
                if attempt < self.max_retries - 1:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
        logger.error(f"GSMArenaProvider: Max retries exceeded for URL={url}. Error: {last_exception}")
        raise last_exception

    def search_phone(self, query: str) -> List[Dict[str, Any]]:
        """Search for phones on GSMArena."""
        try:
            params = {
                "sQuickSearch": "yes",
                "sName": query
            }
            response = self._make_request(self.SEARCH_URL, params=params)
            
            # Check if this page contains multiple maker cards (results or brand list page)
            if "class=\"makers\"" in response.text or "class='makers'" in response.text or "<div class=\"makers\"" in response.text:
                logger.info(f"GSMArenaProvider: Search response contains makers. Parsing search results: {response.url}")
                return self._parse_search_results(response.text)

            # Check if we were redirected to a phone details page directly
            # Details page usually has a specific format like "https://www.gsmarena.com/brand_model-id.php"
            # and contains the spec list.
            if "results.php3" not in response.url and response.url != self.SEARCH_URL:
                logger.info(f"GSMArenaProvider: Search redirected directly to phone page: {response.url}")
                return self._parse_details_page_as_search_result(response.text, response.url)

            return self._parse_search_results(response.text)
        except Exception as exc:
            logger.exception(f"GSMArenaProvider: Error during search for query '{query}': {exc}")
            return []

    def fetch_phone_details(self, slug: str) -> Dict[str, Any]:
        """Fetch details of a phone from its URL/slug."""
        try:
            # Assuming slug is like 'oneplus_13-13456'
            url = urljoin(self.BASE_URL, f"{slug}.php")
            response = self._make_request(url)
            return self._parse_details_page(response.text, url)
        except Exception as exc:
            logger.exception(f"GSMArenaProvider: Error fetching phone details for slug '{slug}': {exc}")
            return {}

    def _parse_search_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse search results from the GSMArena search results page."""
        results = []
        soup = BeautifulSoup(html, "html.parser")
        
        # GSMArena search results are contained in <div class="makers">
        makers_div = soup.find("div", class_="makers")
        if not makers_div:
            logger.info("GSMArenaProvider: No results div found in search output.")
            return []

        li_elements = makers_div.find_all("li")
        for li in li_elements:
            try:
                a_tag = li.find("a")
                if not a_tag:
                    continue

                href = a_tag.get("href")
                if not href:
                    continue
                source_url = urljoin(self.BASE_URL, href)

                # Extract image url if present
                img_tag = a_tag.find("img")
                image_url = img_tag.get("src", "") if img_tag else ""
                
                # Prefer strong/span text for the clean phone name
                strong_tag = a_tag.find("strong")
                title = ""
                if strong_tag:
                    title = strong_tag.get_text(separator=" ", strip=True)
                
                # Fallback to image title attribute if strong_tag is missing
                if not title and img_tag:
                    full_desc = img_tag.get("title", "")
                    if full_desc:
                        # Extract first sentence/part before first period/comma/clause
                        first_clause = full_desc.split(".")[0].split(",")[0].strip()
                        title = first_clause.replace("Android smartphone", "").replace("smartphone", "").strip()

                if not title:
                    continue

                # Parse brand and model out of the title
                # E.g. "OnePlus 13" or "Samsung Galaxy S25 Ultra"
                # The normalization service will refine this, but we'll split by space as a starting point.
                title_parts = title.strip().split(" ", 1)
                brand = title_parts[0]
                model = title_parts[1] if len(title_parts) > 1 else title_parts[0]

                results.append({
                    "brand": brand,
                    "model": model,
                    "image_url": image_url,
                    "source": "GSMArena",
                    "source_url": source_url
                })
            except Exception as exc:
                logger.error(f"GSMArenaProvider: Error parsing search result item: {exc}")
                continue

        logger.info(f"GSMArenaProvider: Successfully parsed {len(results)} search results.")
        return results

    def _parse_details_page_as_search_result(self, html: str, url: str) -> List[Dict[str, Any]]:
        """Parse a direct details page redirect as a single search result."""
        try:
            details = self._parse_details_page(html, url)
            if details:
                return [{
                    "brand": details.get("brand", ""),
                    "model": details.get("model", ""),
                    "image_url": details.get("image_url", ""),
                    "source": "GSMArena",
                    "source_url": url
                }]
        except Exception as exc:
            logger.error(f"GSMArenaProvider: Error parsing details redirect: {exc}")
        return []

    def _parse_details_page(self, html: str, url: str) -> Dict[str, Any]:
        """Parse core phone metadata from details page."""
        soup = BeautifulSoup(html, "html.parser")
        
        # Phone name title is typically in <h1 class="specs-phone-name-title">
        title_tag = soup.find("h1", class_="specs-phone-name-title")
        title = title_tag.text.strip() if title_tag else ""
        
        if not title:
            # Fallback to document title
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.text.split("-")[0].strip()

        # Parse main photo
        photo_div = soup.find("div", class_="specs-photo-main")
        image_url = ""
        if photo_div:
            img = photo_div.find("img")
            if img:
                image_url = img.get("src", "")

        if not title:
            return {}

        title_parts = title.strip().split(" ", 1)
        brand = title_parts[0]
        model = title_parts[1] if len(title_parts) > 1 else title_parts[0]

        return {
            "brand": brand,
            "model": model,
            "image_url": image_url,
            "source": "GSMArena",
            "source_url": url
        }
