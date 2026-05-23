import sys
from pathlib import Path

# Add backend project directory to sys.path
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))

from app.db.session import SessionLocal
from app.models.phone import Phone
from app.services.interpreter.device_summary_service import DeviceSummaryService
from sqlalchemy import select
from sqlalchemy.orm import joinedload

def run_test():
    db = SessionLocal()
    try:
        # Test 1: Flagship Phone (e.g. OnePlus 12)
        slug_flagship = "oneplus-12"
        query_flagship = (
            select(Phone)
            .options(joinedload(Phone.spec), joinedload(Phone.interpretation))
            .where(Phone.slug == slug_flagship)
        )
        flagship = db.scalars(query_flagship).first()
        if not flagship:
            print(f"ERROR: Flagship phone with slug '{slug_flagship}' not found in DB.")
            return

        print(f"Generating interpretations for flagship: {flagship.brand} {flagship.model}")
        interp_flagship = DeviceSummaryService.generate_and_save(db, flagship)
        
        # Verify fields
        print(f"  Battery Summary: {interp_flagship.battery_summary}")
        print(f"  Normal Usage Est: {interp_flagship.normal_usage}")
        print(f"  Heavy Usage Est: {interp_flagship.heavy_usage}")
        print(f"  Charging Summary: {interp_flagship.charging_summary}")
        print(f"  Performance Summary: {interp_flagship.performance_summary}")
        print(f"  Display Summary: {interp_flagship.display_summary}")
        print(f"  Camera Summary: {interp_flagship.camera_summary}")
        print(f"  Pros: {interp_flagship.pros}")
        print(f"  Cons: {interp_flagship.cons}")
        print(f"  Verdict: {interp_flagship.verdict}")
        print(f"  Expected Experience: {interp_flagship.expected_experience}")
        print("Flagship generation and save successful!\n")

        # Test 2: Budget Phone (e.g. Samsung Galaxy A13)
        slug_budget = "samsung-galaxy-a13"
        query_budget = (
            select(Phone)
            .options(joinedload(Phone.spec), joinedload(Phone.interpretation))
            .where(Phone.slug == slug_budget)
        )
        budget = db.scalars(query_budget).first()
        if not budget:
            print(f"ERROR: Budget phone with slug '{slug_budget}' not found in DB.")
            return

        print(f"Generating interpretations for budget: {budget.brand} {budget.model}")
        interp_budget = DeviceSummaryService.generate_and_save(db, budget)
        
        # Verify fields
        print(f"  Battery Summary: {interp_budget.battery_summary}")
        print(f"  Normal Usage Est: {interp_budget.normal_usage}")
        print(f"  Heavy Usage Est: {interp_budget.heavy_usage}")
        print(f"  Charging Summary: {interp_budget.charging_summary}")
        print(f"  Performance Summary: {interp_budget.performance_summary}")
        print(f"  Display Summary: {interp_budget.display_summary}")
        print(f"  Camera Summary: {interp_budget.camera_summary}")
        print(f"  Pros: {interp_budget.pros}")
        print(f"  Cons: {interp_budget.cons}")
        print(f"  Verdict: {interp_budget.verdict}")
        print(f"  Expected Experience: {interp_budget.expected_experience}")
        print("Budget generation and save successful!\n")

    except Exception as e:
        print(f"Exception during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
