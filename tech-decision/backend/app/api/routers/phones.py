import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.core.config import settings
from app.models.phone import Phone, PhoneInsight, PriceListing, PhoneInterpretation, PhoneVariant, VariantPrice
from app.schemas.phone import PhoneInsightRead, PhoneRead, PhoneSearchResult, PriceComparisonResponse, PhoneDecisionResponse, PhoneSpecsResponse, PhoneInterpretationRead, PhoneVariantRead, VariantPriceRead
from app.services.insight_generator import InsightGenerator, InsightGeneratorError
from app.services.best_platform_selector import BestPlatformSelector
from app.services.seller_trust import SellerTrust
from app.services.decision_engine import DecisionEngine
from app.services.pricing.pricing_service import PricingService

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix='/api/phones', tags=['Phones'])


@router.get('/search', response_model=List[PhoneSearchResult])
def search_phones(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    query = select(Phone).where(Phone.slug.ilike(f'%{q}%') | Phone.brand.ilike(f'%{q}%') | Phone.model.ilike(f'%{q}%'))
    phones = db.scalars(query).all()
    return phones


@router.get('', response_model=List[PhoneSearchResult])
def get_all_phones(db: Session = Depends(get_db)):
    query = select(Phone)
    phones = db.scalars(query).all()
    return phones


@router.get('/{slug}', response_model=PhoneRead)
def get_phone_by_slug(slug: str, db: Session = Depends(get_db)):
    try:
        query = (
            select(Phone)
            .options(
                joinedload(Phone.spec),
                joinedload(Phone.insight),
                joinedload(Phone.interpretation),
                joinedload(Phone.price_listings),
                joinedload(Phone.variants)
            )
            .where(Phone.slug == slug)
        )
        phone = db.scalars(query).first()
        if not phone:
            raise HTTPException(status_code=404, detail='Phone not found')
        
        # If specs do not exist in database, fetch them dynamically
        if not phone.spec:
            logger.info("get_phone_by_slug: Specs not found in DB for %s. Fetching dynamically.", slug)
            from app.services.specs.specification_service import SpecificationService
            spec_service = SpecificationService()
            spec_service.get_or_fetch_specs(slug, db)
            db.expire_all()
            phone = db.scalars(query).first()
        elif phone.spec:
            # If specs exist but missing new fields, run enrichment dynamically
            enrichable_fields = ["brightness_label", "update_policy_label", "wifi_version", "build_materials"]
            is_missing_enrichment = any(getattr(phone.spec, field) is None for field in enrichable_fields)
            if is_missing_enrichment:
                logger.info("get_phone_by_slug: Spec missing enriched fields for %s. Running enrichment.", slug)
                from app.services.specs.spec_enrichment_service import SpecEnrichmentService
                from app.services.specs.normalization_service import normalize_all_specs
                
                # Construct raw_specs dict from the stored raw fields
                raw_specs = {
                    "raw_chipset": phone.spec.raw_chipset,
                    "raw_cpu": phone.spec.raw_cpu,
                    "raw_gpu": phone.spec.raw_gpu,
                    "raw_ram": phone.spec.raw_ram,
                    "raw_storage": phone.spec.raw_storage,
                    "raw_battery_mah": phone.spec.raw_battery_mah,
                    "raw_charging_watts": phone.spec.raw_charging_watts,
                    "raw_wireless_charging": phone.spec.raw_wireless_charging,
                    "raw_display_size": phone.spec.raw_display_size,
                    "raw_display_resolution": phone.spec.raw_display_resolution,
                    "raw_refresh_rate": phone.spec.raw_refresh_rate,
                    "raw_display_type": phone.spec.raw_display_type,
                    "raw_main_camera": phone.spec.raw_main_camera,
                    "raw_ultrawide_camera": phone.spec.raw_ultrawide_camera,
                    "raw_telephoto_camera": phone.spec.raw_telephoto_camera,
                    "raw_selfie_camera": phone.spec.raw_selfie_camera,
                    "raw_weight": phone.spec.raw_weight,
                    "raw_ip_rating": phone.spec.raw_ip_rating,
                    "raw_connectivity": phone.spec.raw_connectivity,
                    "raw_software": phone.spec.raw_software,
                }
                # Normalize and enrich
                normalized = normalize_all_specs(raw_specs)
                enriched = SpecEnrichmentService.enrich(phone.brand, phone.model, raw_specs, normalized)
                
                # Save back to database
                for k, v in enriched.items():
                    if hasattr(phone.spec, k) and getattr(phone.spec, k) is None:
                        setattr(phone.spec, k, v)
                try:
                    db.commit()
                    db.refresh(phone.spec)
                except Exception as db_exc:
                    logger.warning("Failed to commit dynamic spec enrichment: %s", db_exc)
                    db.rollback()

        # If interpretation is not generated/cached, generate and save it
        if phone and not phone.interpretation:
            logger.info("get_phone_by_slug: Interpretation not found in DB for %s. Generating.", slug)
            from app.services.interpreter.device_summary_service import DeviceSummaryService
            try:
                DeviceSummaryService.generate_and_save(db, phone)
            except Exception as exc:
                logger.error("Failed to generate interpretations for %s: %s", slug, exc)
            db.expire_all()
            phone = db.scalars(query).first()

        # Populate dynamic price_intelligence field on response model
        if phone:
            from app.services.pricing.fake_discount_detector import FakeDiscountDetector
            # Format listings for FakeDiscountDetector
            listings_list = []
            for lst in phone.price_listings:
                listings_list.append({
                    "platform": lst.platform,
                    "final_price": lst.final_price,
                    "trust_score": SellerTrust.calculate_score(lst.platform, lst.seller_rating, lst.seller_reviews_count),
                    "in_stock": lst.in_stock,
                })
            if listings_list:
                phone.price_intelligence = FakeDiscountDetector.generate_cross_platform_insight(
                    listings_list, launch_price=phone.launch_price
                )
            else:
                phone.price_intelligence = "No price listings currently available."

        return phone
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Endpoint exception in get_phone_by_slug for slug %s: %s", slug, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post('/{slug}/generate-insights', response_model=PhoneInsightRead)
def generate_phone_insights(slug: str, db: Session = Depends(get_db)):
    try:
        query = (
            select(Phone)
            .options(joinedload(Phone.spec), joinedload(Phone.insight))
            .where(Phone.slug == slug)
        )
        phone = db.scalars(query).first()
        if not phone:
            raise HTTPException(status_code=404, detail='Phone not found')
        if not phone.spec:
            raise HTTPException(status_code=404, detail='Phone specifications not found')

        phone_data = {
            'battery_mah': phone.spec.battery_mah,
            'charging_watts': phone.spec.charging_watts,
            'processor': phone.spec.processor,
            'ram_gb': phone.spec.ram_gb,
            'storage_gb': phone.spec.storage_gb,
            'display_size': phone.spec.display_size,
            'display_type': phone.spec.display_type,
            'refresh_rate_hz': phone.spec.refresh_rate_hz,
            'peak_brightness_nits': phone.spec.peak_brightness_nits,
            'camera_main_mp': phone.spec.camera_main_mp,
            'os_updates_years': phone.spec.os_updates_years,
            'security_updates_years': phone.spec.security_updates_years,
            'launch_price': phone.launch_price,
            'current_avg_price': phone.current_avg_price,
        }

        api_key = settings.openai_api_key or os.getenv('OPENAI_API_KEY', '')
        logger.info("Generating insights for %s. API key present: %s", slug, bool(api_key))

        try:
            insights = InsightGenerator.from_environment().generate(phone_data)
        except InsightGeneratorError as exc:
            logger.error("OpenAI request failure for phone %s: %s", slug, exc, exc_info=True)
            raise HTTPException(status_code=502, detail="AI insights are currently unavailable.") from exc
        except Exception as exc:
            logger.error("Unexpected OpenAI generation failure for phone %s: %s", slug, exc, exc_info=True)
            raise HTTPException(status_code=502, detail="AI insights are currently unavailable.") from exc

        if phone.insight:
            phone.insight.battery_summary = insights['battery_summary']
            phone.insight.performance_summary = insights['performance_summary']
            phone.insight.display_summary = insights['display_summary']
            phone.insight.camera_summary = insights['camera_summary']
            phone.insight.software_summary = insights['software_summary']
            phone.insight.honest_verdict = insights['honest_verdict']
        else:
            phone.insight = PhoneInsight(
                phone_id=phone.id,
                battery_summary=insights['battery_summary'],
                performance_summary=insights['performance_summary'],
                display_summary=insights['display_summary'],
                camera_summary=insights['camera_summary'],
                software_summary=insights['software_summary'],
                honest_verdict=insights['honest_verdict'],
            )

        db.add(phone)
        db.commit()
        db.refresh(phone)
        return phone.insight
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Endpoint exception in generate_phone_insights for slug %s: %s", slug, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get('/{slug}/prices', response_model=PriceComparisonResponse)
def get_phone_prices(slug: str, variant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = select(Phone).options(joinedload(Phone.variants)).where(Phone.slug == slug)
    phone = db.scalars(query).first()
    if not phone:
        raise HTTPException(status_code=404, detail='Phone not found')

    # Find the selected variant
    selected_variant = None
    if phone.variants:
        if variant_id:
            variant_id_str = str(variant_id)
            for v in phone.variants:
                if str(v.id) == variant_id_str or v.slug == variant_id_str:
                    selected_variant = v
                    break
        if not selected_variant:
            # Default to baseline (lowest storage/RAM variant)
            selected_variant = min(phone.variants, key=lambda v: (v.storage_gb, v.ram_gb))

    if selected_variant:
        listings_query = select(VariantPrice).where(VariantPrice.variant_id == selected_variant.id)
    else:
        listings_query = select(PriceListing).where(PriceListing.phone_id == phone.id)
        
    db_listings = db.scalars(listings_query).all()

    # Cache policies: if no listings are in DB or they are > 1 hour old, re-fetch
    is_stale = False
    if not db_listings:
        is_stale = True
    else:
        newest_update = max(l.updated_at for l in db_listings)
        if newest_update.tzinfo is None:
            # Naive datetime
            age = datetime.utcnow() - newest_update
        else:
            # Timezone aware
            age = datetime.now(timezone.utc) - newest_update
        
        if age.total_seconds() > 3600:
            is_stale = True

    if is_stale:
        logger.info(f"Price listings for {slug} are stale or missing. Triggering price aggregation.")
        PricingService.fetch_and_save_prices(phone, db)
        db.expire_all()
        # Fetch updated listings
        if selected_variant:
            db_listings = db.scalars(select(VariantPrice).where(VariantPrice.variant_id == selected_variant.id)).all()
        else:
            db_listings = db.scalars(select(PriceListing).where(PriceListing.phone_id == phone.id)).all()

    listings_data = []
    for listing in db_listings:
        trust_score = SellerTrust.calculate_score(
            listing.platform,
            listing.seller_rating,
            listing.seller_reviews_count
        )

        listing_dict = {
            "id": listing.id,
            "variant_id": getattr(listing, 'variant_id', None) or (selected_variant.id if selected_variant else None),
            "platform": listing.platform,
            "seller_name": listing.seller_name,
            "seller_rating": listing.seller_rating,
            "seller_reviews_count": listing.seller_reviews_count,
            "listed_price": listing.listed_price,
            "original_mrp": listing.original_mrp,
            "coupon_discount": listing.coupon_discount,
            "bank_discount": listing.bank_discount,
            "exchange_bonus": listing.exchange_bonus,
            "cashback_amount": listing.cashback_amount,
            "delivery_charge": listing.delivery_charge,
            "final_price": listing.final_price,
            "in_stock": listing.in_stock,
            "delivery_eta_days": listing.delivery_eta_days,
            "product_url": listing.product_url,
            "emi_available": listing.emi_available,
            "emi_months": listing.emi_months,
            "fake_discount_flag": listing.fake_discount_flag,
            "discount_authenticity_score": listing.discount_authenticity_score,
            "price_intelligence_note": listing.price_intelligence_note,
            "updated_at": listing.updated_at,
            "trust_score": trust_score
        }
        listings_data.append(listing_dict)

    if not listings_data:
        return PriceComparisonResponse(
            listings=[],
            best_platform=None,
            summary="No price listings available for this variant."
        )

    # Sort listings by final price ascending, out-of-stock listings at the end
    listings_data.sort(key=lambda x: (not x["in_stock"], x["final_price"]))

    best_listing, explanation = BestPlatformSelector.select_best(listings_data)
    
    # Generate cross-platform pricing insight summary
    from app.services.pricing.fake_discount_detector import FakeDiscountDetector
    
    # Estimate variant launch price
    launch_price = phone.launch_price if phone.launch_price else 69999
    if selected_variant:
        import math
        base_variant = min(phone.variants, key=lambda v: (v.storage_gb, v.ram_gb)) if phone.variants else None
        if base_variant:
            ram_diff = selected_variant.ram_gb - base_variant.ram_gb
            ram_adjustment = (ram_diff / 4.0) * 3000
            
            if base_variant.storage_gb and selected_variant.storage_gb:
                storage_ratio = selected_variant.storage_gb / base_variant.storage_gb
                storage_doublings = math.log2(storage_ratio) if storage_ratio > 0 else 0
                storage_adjustment = storage_doublings * 5000
            else:
                storage_adjustment = 0
            launch_price = int(launch_price + ram_adjustment + storage_adjustment)
            
    cross_platform_summary = FakeDiscountDetector.generate_cross_platform_insight(
        listings_data, launch_price=launch_price
    )
    # Append the best platform explanation if we have a summary
    summary = f"{cross_platform_summary} {explanation}" if cross_platform_summary else explanation

    return PriceComparisonResponse(
        listings=listings_data,
        best_platform=best_listing,
        summary=summary
    )


@router.get('/{slug}/decision', response_model=PhoneDecisionResponse)
def get_phone_decision(slug: str, variant_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    try:
        query = (
            select(Phone)
            .options(
                joinedload(Phone.spec),
                joinedload(Phone.insight),
                joinedload(Phone.variants),
                joinedload(Phone.price_listings)
            )
            .where(Phone.slug == slug)
        )
        phone = db.scalars(query).first()
        if not phone:
            raise HTTPException(status_code=404, detail='Phone not found')
        
        analysis = DecisionEngine.analyze(phone, variant_id=variant_id)
        return analysis
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Endpoint exception in get_phone_decision for slug %s: %s", slug, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get('/{slug}/specifications', response_model=PhoneSpecsResponse)
def get_phone_specifications(slug: str, db: Session = Depends(get_db)):
    try:
        query = (
            select(Phone)
            .options(joinedload(Phone.spec))
            .where(Phone.slug == slug)
        )
        phone = db.scalars(query).first()
        if not phone:
            raise HTTPException(status_code=404, detail='Phone not found')

        spec = phone.spec
        if not spec:
            from app.services.specs.specification_service import SpecificationService
            spec_service = SpecificationService()
            spec = spec_service.get_or_fetch_specs(slug, db)
            
        if not spec:
            raise HTTPException(status_code=404, detail='Specifications could not be retrieved')
            
        return PhoneSpecsResponse(
            brand=phone.brand,
            model=phone.model,
            chipset=spec.chipset,
            ram=spec.ram,
            storage=spec.storage,
            battery_mah=spec.battery_mah,
            refresh_rate=spec.refresh_rate
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Endpoint exception in get_phone_specifications for slug %s: %s", slug, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get('/{slug}/interpretations', response_model=PhoneInterpretationRead)
def get_phone_interpretations(slug: str, db: Session = Depends(get_db)):
    try:
        query = (
            select(Phone)
            .options(joinedload(Phone.spec), joinedload(Phone.interpretation))
            .where(Phone.slug == slug)
        )
        phone = db.scalars(query).first()
        if not phone:
            raise HTTPException(status_code=404, detail='Phone not found')
            
        if not phone.interpretation:
            from app.services.interpreter.device_summary_service import DeviceSummaryService
            DeviceSummaryService.generate_and_save(db, phone)
            db.refresh(phone)
            
        return phone.interpretation
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Endpoint exception in get_phone_interpretations for slug %s: %s", slug, exc)
        raise HTTPException(status_code=500, detail="Internal server error") from exc
