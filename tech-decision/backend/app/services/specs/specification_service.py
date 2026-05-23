import logging
import time
import requests
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.phone import Phone, PhoneSpec
from app.parsers.gsmarena_spec_parser import parse_gsmarena_specs
from app.services.specs.normalization_service import normalize_all_specs
from app.services.specs.spec_enrichment_service import SpecEnrichmentService

logger = logging.getLogger("uvicorn.error")

class SpecificationService:
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

    def _fetch_html(self, url: str) -> str:
        """Fetch the HTML content of a URL with retries, timeout and header configuration."""
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                logger.info(f"SpecificationService: Fetching HTML from {url} (attempt {attempt + 1})")
                res = requests.get(url, headers=self.headers, timeout=self.timeout)
                res.raise_for_status()
                return res.text
            except requests.RequestException as exc:
                last_exception = exc
                logger.warning(f"SpecificationService: Request failed (attempt {attempt + 1}): {exc}")
                if attempt < self.max_retries - 1:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
        logger.error(f"SpecificationService: Failed to fetch HTML from {url}. Error: {last_exception}")
        raise last_exception

    def get_or_fetch_specs(self, slug: str, db: Session) -> PhoneSpec | None:
        """
        Retrieves phone specs from the DB if they exist.
        Otherwise, scrapes GSMArena, normalizes, stores, and returns them.
        """
        # 1. Look up phone by slug
        stmt = select(Phone).where(Phone.slug == slug)
        phone = db.scalars(stmt).first()
        if not phone:
            logger.error(f"SpecificationService: Phone not found in DB for slug='{slug}'")
            return None

        # 2. Check if specs already exist in DB
        if phone.spec:
            logger.info(f"SpecificationService: Found existing specs in DB for phone='{phone.brand} {phone.model}'")
            return phone.spec

        # 3. Determine source URL
        source_url = phone.source_url
        if not source_url:
            source_url = f"https://www.gsmarena.com/{slug}.php"
            logger.info(f"SpecificationService: No source_url found in DB. Constructing fallback URL: {source_url}")

        # 4. Fetch HTML from GSMArena
        try:
            html = self._fetch_html(source_url)
        except Exception as exc:
            logger.error(f"SpecificationService: Failed to fetch phone page for slug='{slug}': {exc}")
            return None

        # 5. Parse specification tables
        try:
            raw_specs = parse_gsmarena_specs(html)
        except Exception as exc:
            logger.error(f"SpecificationService: Failed to parse specifications for slug='{slug}': {exc}")
            return None

        # 6. Normalize fields
        try:
            normalized_specs = normalize_all_specs(raw_specs)
        except Exception as exc:
            logger.error(f"SpecificationService: Failed to normalize specifications for slug='{slug}': {exc}")
            return None

        # 6b. Enrichment pass — adds display labels, software policy, AI features,
        #     connectivity versions, build materials, reverse charging detection.
        #     This is fully isolated; failures log warnings but don't abort the save.
        try:
            normalized_specs = SpecEnrichmentService.enrich(
                brand=phone.brand,
                model=phone.model,
                raw_specs=raw_specs,
                normalized=normalized_specs,
            )
            logger.info(f"SpecificationService: Enrichment completed for {phone.brand} {phone.model}")
        except Exception as exc:
            logger.warning(f"SpecificationService: Enrichment failed for slug='{slug}': {exc}")

        # 7. Save structured specs to DB
        try:
            # Check if there is already a PhoneSpec linked to the phone
            spec_stmt = select(PhoneSpec).where(PhoneSpec.phone_id == phone.id)
            phone_spec = db.scalars(spec_stmt).first()

            if not phone_spec:
                phone_spec = PhoneSpec(phone_id=phone.id)
                db.add(phone_spec)

            # Update the specifications fields (both raw and normalized)
            for key, val in normalized_specs.items():
                if hasattr(phone_spec, key):
                    setattr(phone_spec, key, val)

            # Parse page title and photo to update Phone's image_url if missing
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            photo_div = soup.find("div", class_="specs-photo-main")
            if photo_div:
                img = photo_div.find("img")
                if img and img.get("src"):
                    # Only update if current image_url is empty/placeholder
                    if not phone.image_url or "placeholder" in phone.image_url:
                        phone.image_url = img.get("src")
                        db.add(phone)

            # Extract and create variants
            self._create_variants(phone, phone_spec, db)

            db.commit()
            logger.info(f"SpecificationService: Successfully parsed, normalized, and saved specifications for {phone.brand} {phone.model}")
            return phone_spec
        except Exception as exc:
            db.rollback()
            try:
                # If another concurrent request already committed the specifications, update it
                spec_stmt = select(PhoneSpec).where(PhoneSpec.phone_id == phone.id)
                phone_spec = db.scalars(spec_stmt).first()
                if phone_spec:
                    for key, val in normalized_specs.items():
                        if hasattr(phone_spec, key):
                            setattr(phone_spec, key, val)
                    self._create_variants(phone, phone_spec, db)
                    db.commit()
                    return phone_spec
            except Exception as retry_exc:
                db.rollback()
            logger.error(f"SpecificationService: Failed to save specifications to database: {exc}", exc_info=True)
            return None

    def _create_variants(self, phone: Phone, phone_spec: PhoneSpec, db: Session) -> None:
        """Extract and persist all PhoneVariant combinations for the phone."""
        try:
            from app.services.variants.variant_extractor import generate_all_variants
            from app.services.variants.variant_normalizer import generate_variant_slug
            from app.models.phone import PhoneVariant

            extracted_variants = generate_all_variants(
                raw_ram_str=phone_spec.raw_ram,
                raw_colors_str=phone_spec.raw_colors,
                fallback_ram=phone_spec.ram_gb,
                fallback_storage=phone_spec.storage_gb
            )
            
            existing_variants = {v.slug: v for v in phone.variants}
            for ev_dict in extracted_variants:
                ram = ev_dict["ram_gb"]
                storage = ev_dict["storage_gb"]
                color = ev_dict["color"]
                v_slug = generate_variant_slug(phone.slug, ram, storage, color)
                
                if v_slug not in existing_variants:
                    new_var = PhoneVariant(
                        phone_id=phone.id,
                        ram_gb=ram,
                        storage_gb=storage,
                        color=color,
                        slug=v_slug
                    )
                    db.add(new_var)
            logger.info(f"SpecificationService: Extracted and created variants for {phone.brand} {phone.model}")
        except Exception as exc:
            logger.error(f"SpecificationService: Error creating variants: {exc}", exc_info=True)
