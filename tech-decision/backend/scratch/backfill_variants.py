import os
import sys

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.phone import Phone, PhoneSpec, PhoneVariant
from app.services.variants.variant_extractor import generate_all_variants
from app.services.variants.variant_normalizer import generate_variant_slug
from app.services.pricing.pricing_service import PricingService

def backfill():
    db = SessionLocal()
    try:
        phones = db.query(Phone).all()
        print(f"Found {len(phones)} phones in database.")
        
        for phone in phones:
            print(f"\nProcessing {phone.brand} {phone.model} (ID: {phone.id})...")
            
            # Ensure spec is present
            spec = phone.spec
            if not spec:
                print(f"No spec found for {phone.brand} {phone.model}. Skipping.")
                continue
                
            # Populate raw_colors if empty (give it some default colors if None to generate nice variants)
            if not spec.raw_colors:
                spec.raw_colors = "Black, Silver, Blue"
                db.add(spec)
                db.commit()
                print("Setting default raw_colors to: 'Black, Silver, Blue'")
                
            if not spec.raw_ram:
                # Fallback to model spec ram/storage
                spec.raw_ram = f"{spec.storage_gb or 256}GB {spec.ram_gb or 12}GB RAM"
                db.add(spec)
                db.commit()
                print(f"Setting default raw_ram to: '{spec.raw_ram}'")
                
            # Create variants
            extracted = generate_all_variants(
                raw_ram_str=spec.raw_ram,
                raw_colors_str=spec.raw_colors,
                fallback_ram=spec.ram_gb,
                fallback_storage=spec.storage_gb
            )
            print(f"Extracted {len(extracted)} variant configurations.")
            
            # Create PhoneVariant entries
            existing_variants = {v.slug for v in phone.variants}
            variants_created = 0
            for ev_dict in extracted:
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
                    existing_variants.add(v_slug)
                    variants_created += 1
            
            db.commit()
            db.refresh(phone)
            print(f"Created {variants_created} new variants. Total variants: {len(phone.variants)}")
            
            # Run pricing fetch & save (which will scale and populate VariantPrice)
            print("Fetching and scaling prices...")
            PricingService.fetch_and_save_prices(phone, db)
            print(f"Done processing {phone.brand} {phone.model}.")
            
        print("\nBackfill successfully completed!")
    except Exception as exc:
        print(f"Error during backfill: {exc}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    backfill()
