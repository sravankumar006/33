import logging
import uuid
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from difflib import SequenceMatcher

from app.models.phone import Phone
from app.providers.gsmarena_provider import GSMArenaProvider
from app.services.discovery.normalization_service import NormalizationService
from app.services.discovery.slug_service import SlugService

logger = logging.getLogger("uvicorn.error")


def clean_string(s: str) -> str:
    """Normalize a string: lowercase, remove special characters, remove extra spaces."""
    if not s:
        return ""
    # Lowercase
    s = s.lower().strip()
    # Replace 'one plus' or 'one-plus' with 'oneplus'
    s = re.sub(r'\bone\s+plus\b', 'oneplus', s)
    s = re.sub(r'\bone-plus\b', 'oneplus', s)
    # Ignore special characters (keep alphanumeric and spaces)
    s = re.sub(r'[^a-z0-9\s]', '', s)
    
    # Remove duplicate brand names if repeated next to each other or in string
    words = s.split()
    clean_words = []
    known_brands = {"samsung", "apple", "oneplus", "xiaomi", "oppo", "vivo", "realme", "motorola", "google", "nothing"}
    seen_brands = set()
    for w in words:
        if w in known_brands:
            if w in seen_brands:
                continue
            seen_brands.add(w)
        clean_words.append(w)
    s = " ".join(clean_words)
    
    # Remove extra spaces
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def get_model_boost(brand: str, model: str) -> float:
    """
    Calculate a numeric boost for flagship, modern, and high-end models.
    Helps rank premium/flagship devices higher in general brand-only searches.
    """
    boost = 0.0
    model_lower = model.lower()
    brand_lower = brand.lower()
    
    # Penalize placeholder/ancient basic models (like the 2007 "Apple iPhone" or brand-name only placeholders)
    if model_lower in ["iphone", "phones", brand_lower] or model_lower == "":
        return -20.0
    
    # 1. Flagship keywords
    if "ultra" in model_lower:
        boost += 15.0
    if "pro max" in model_lower or "promax" in model_lower:
        boost += 14.0
    if "fold" in model_lower:
        boost += 13.0
    if "flip" in model_lower:
        boost += 11.0
    if "pro" in model_lower:
        boost += 10.0
    if "plus" in model_lower or "+" in model_lower:
        boost += 8.0
    if "edge" in model_lower:
        boost += 6.0
    if "fe" in model_lower:
        boost += 5.0
        
    # 2. Extract and reward higher model numbers (e.g. S25 > S10, iPhone 16 > iPhone 8)
    numbers = [int(n) for n in re.findall(r'\d+', model_lower)]
    if numbers:
        max_num = max(numbers)
        if max_num < 100:  # e.g., version numbers like 16, 25, 30
            boost += min(max_num * 0.5, 15.0)  # Up to +15.0 for newer versions
            
    # 3. Series boost
    # S-series, Note-series for Samsung
    if brand_lower == "samsung":
        if re.search(r'\bs\d+', model_lower):
            boost += 10.0
        elif "note" in model_lower:
            boost += 8.0
        elif re.search(r'\ba\d+', model_lower):
            # A-series: A55, A35 are mid-range, A02, A03 are low-end.
            a_nums = [int(n) for n in re.findall(r'a(\d+)', model_lower)]
            if a_nums:
                max_a = max(a_nums)
                if max_a >= 50:
                    boost += 6.0
                elif max_a >= 30:
                    boost += 4.0
                elif max_a < 10:
                    boost -= 5.0 # Penalize low-end A0x series
        elif "tab" in model_lower:
            boost -= 5.0 # Prefer phones over tablets
            
    # iPhone numbers
    if brand_lower == "apple" and "iphone" in model_lower:
        boost += 10.0
        
    return boost


def calculate_score(query: str, brand: str, model: str) -> float:
    """
    Calculate search match score from 0.0 to 100.0.
    Intelligently ranks by prioritizing:
    1. Exact matches (100.0)
    2. Prefix matches (90.0-99.0)
    3. Substring matches (75.0-89.0)
    4. Fuzzy similarity (up to 74.0)
    
    Applies a model boost for brand-only / general queries.
    """
    q_clean = clean_string(query)
    brand_clean = clean_string(brand)
    model_clean = clean_string(model)
    full_name = f"{brand_clean} {model_clean}".strip()
    
    if not q_clean or not full_name:
        return 0.0
        
    # 1. Exact match of full name
    if q_clean == full_name:
        return 100.0
        
    # Detect if query has digits
    has_digits = bool(re.search(r'\d+', q_clean))
    
    boost = get_model_boost(brand, model)
    boost_weight = 0.2 if not has_digits else 0.05
    
    # 2. Exact model match
    if q_clean == model_clean:
        return min(95.0 + boost_weight * boost, 99.0)
        
    # 3. Full name prefix matches
    if full_name.startswith(q_clean):
        if not has_digits:
            base = 90.0
        else:
            base = 90.0 + (9.0 * len(q_clean) / len(full_name))
        return min(base + boost_weight * boost, 99.0)
        
    # 4. Model prefix matches
    if model_clean.startswith(q_clean):
        if not has_digits:
            base = 85.0
        else:
            base = 85.0 + (4.0 * len(q_clean) / len(model_clean))
        return min(base + boost_weight * boost, 99.0)
        
    # 5. Full name substring matches
    if q_clean in full_name:
        if not has_digits:
            base = 75.0
        else:
            base = 75.0 + (9.0 * len(q_clean) / len(full_name))
        return min(base + boost_weight * boost, 99.0)
        
    # 6. Model substring matches
    if q_clean in model_clean:
        if not has_digits:
            base = 70.0
        else:
            base = 70.0 + (4.0 * len(q_clean) / len(model_clean))
        return min(base + boost_weight * boost, 99.0)
        
    # 7. Exact token matching
    q_tokens = q_clean.split()
    name_tokens = full_name.split()
    
    token_matches = 0
    for qt in q_tokens:
        if qt in name_tokens:
            token_matches += 1
            
    if token_matches == len(q_tokens) and len(q_tokens) > 0:
        base = 80.0 + (9.0 * len(q_tokens) / len(name_tokens))
        return min(base + boost_weight * boost, 99.0)
        
    # 8. Prefix token matching
    token_prefix_matches = 0
    for qt in q_tokens:
        if any(nt.startswith(qt) for nt in name_tokens):
            token_prefix_matches += 1
            
    if token_prefix_matches == len(q_tokens) and len(q_tokens) > 0:
        base = 70.0 + (9.0 * len(q_tokens) / len(name_tokens))
        return min(base + boost_weight * boost, 99.0)
        
    # 9. Fuzzy matching using SequenceMatcher ratio
    ratio = SequenceMatcher(None, q_clean, full_name).ratio()
    fuzzy_score = ratio * 100.0
    
    # Cap fuzzy matches below token/substring matches
    base = min(fuzzy_score, 69.0)
    return min(base + boost_weight * boost, 69.0)



class DiscoveryService:
    def __init__(self):
        self.provider = GSMArenaProvider()

    def search_and_discover(self, query: str, db: Session) -> List[Phone]:
        """
        Discovers phones matching the query from external sources,
        normalizes identities, generates slugs, avoids duplicates,
        updates the database, scores them intelligently, and returns
        up to 7 ranked results with a `match_score` attribute assigned.
        """
        logger.info(f"DiscoveryService: Initiating discovery search for query='{query}'")
        
        q_clean = clean_string(query)
        
        # 1. Query external provider to fetch any new matches
        raw_results = []
        try:
            raw_results = self.provider.search_phone(query)
            logger.info(f"DiscoveryService: Provider found {len(raw_results)} results.")
        except Exception as exc:
            logger.error(f"DiscoveryService: Scraper error: {exc}", exc_info=True)
            
        # 2. Process and upsert scraper results to the local database
        processed_slugs = set()
        for item in raw_results:
            try:
                raw_brand = item.get("brand", "")
                raw_model = item.get("model", "")
                
                brand, model = NormalizationService.normalize(raw_brand, raw_model)
                slug = SlugService.generate(brand, model)
                
                if slug in processed_slugs:
                    continue
                processed_slugs.add(slug)

                # Check database for existing slug
                query_stmt = select(Phone).where(Phone.slug == slug)
                existing_phone = db.scalars(query_stmt).first()

                if existing_phone:
                    # Update fields
                    existing_phone.brand = brand
                    existing_phone.model = model
                    if item.get("image_url"):
                        existing_phone.image_url = item["image_url"]
                    existing_phone.source = item.get("source")
                    existing_phone.source_url = item.get("source_url")
                    db.add(existing_phone)
                else:
                    # Insert new record
                    new_phone = Phone(
                        id=uuid.uuid4(),
                        brand=brand,
                        model=model,
                        slug=slug,
                        image_url=item.get("image_url"),
                        source=item.get("source"),
                        source_url=item.get("source_url"),
                        launch_price=None,
                        current_avg_price=None
                    )
                    db.add(new_phone)
            except Exception as exc:
                logger.error(f"DiscoveryService: Error processing discovered item: {exc}", exc_info=True)

        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            logger.error(f"DiscoveryService: DB commit failed: {exc}", exc_info=True)

        # 3. Query the database for all candidates matching the query tokens
        # We query by building conditions for each token of the query
        words = q_clean.split()
        candidates: List[Phone] = []
        if words:
            conditions = []
            for w in words:
                conditions.append(
                    Phone.brand.ilike(f"%{w}%") | 
                    Phone.model.ilike(f"%{w}%") | 
                    Phone.slug.ilike(f"%{w}%")
                )
            stmt = select(Phone).where(and_(*conditions))
            candidates = list(db.scalars(stmt).all())
        else:
            # Fallback if query was only special characters, get everything
            stmt = select(Phone)
            candidates = list(db.scalars(stmt).all())

        # If we got no candidates from the tokenized query, fall back to matching any word
        if not candidates and words:
            conditions = []
            for w in words:
                conditions.append(
                    Phone.brand.ilike(f"%{w}%") | 
                    Phone.model.ilike(f"%{w}%") | 
                    Phone.slug.ilike(f"%{w}%")
                )
            from sqlalchemy import or_
            stmt = select(Phone).where(or_(*conditions))
            candidates = list(db.scalars(stmt).all())

        # 4. Calculate score for each candidate and sort them
        scored_candidates = []
        for phone in candidates:
            score = calculate_score(query, phone.brand, phone.model)
            # Filter out extremely low matches (e.g. score < 15) to keep suggestions clean
            if score >= 15.0:
                # Save raw score for sorting
                phone.raw_score = score
                # Dynamically set match_score on the SQLModel object as an integer
                phone.match_score = int(round(score))
                scored_candidates.append(phone)

        # Sort by raw_score descending, and lexicographically by brand+model as fallback
        scored_candidates.sort(key=lambda p: (-p.raw_score, p.brand.lower(), p.model.lower()))

        # Deduplicate candidates by slug just in case
        unique_candidates = []
        seen_slugs = set()
        for p in scored_candidates:
            if p.slug not in seen_slugs:
                seen_slugs.add(p.slug)
                unique_candidates.append(p)

        # Slice the top 7
        top_7 = unique_candidates[:7]
        
        logger.info(f"DiscoveryService: Returning {len(top_7)} ranked results for query='{query}'")
        return top_7
