import urllib.request
import json
import sys
from pathlib import Path

project_dir = Path("c:/Users/SAMSUNG/OneDrive/Desktop/My-Projects/33/tech-decision/backend")
sys.path.append(str(project_dir))

from app.db.session import SessionLocal
from app.models.phone import Phone
from sqlalchemy import select

def test_all_phones():
    db = SessionLocal()
    try:
        stmt = select(Phone)
        phones = list(db.scalars(stmt).all())
        print(f"Testing {len(phones)} phones...")
        failures = []
        for p in phones:
            url = f"http://localhost:8000/api/phones/{p.slug}"
            try:
                req = urllib.request.urlopen(url)
                res = req.read().decode('utf-8')
                data = json.loads(res)
                # Also test prices endpoint
                prices_url = f"http://localhost:8000/api/phones/{p.slug}/prices"
                prices_req = urllib.request.urlopen(prices_url)
                prices_res = prices_req.read().decode('utf-8')
                
                # Also test decision endpoint
                decision_url = f"http://localhost:8000/api/phones/{p.slug}/decision"
                decision_req = urllib.request.urlopen(decision_url)
                decision_res = decision_req.read().decode('utf-8')
            except Exception as e:
                print(f"FAILURE for {p.brand} {p.model} ({p.slug}): {e}")
                failures.append((p.slug, str(e)))
        
        print("\n--- Summary ---")
        print(f"Total checked: {len(phones)}")
        print(f"Total failures: {len(failures)}")
        for slug, err in failures:
            print(f"- {slug}: {err}")
    finally:
        db.close()

if __name__ == "__main__":
    test_all_phones()

