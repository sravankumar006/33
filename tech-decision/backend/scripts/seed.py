import uuid

from app.db.session import SessionLocal
from app.models.phone import Phone, PhoneInsight, PhoneSpec, PriceListing
from app.services.final_price_calculator import FinalPriceCalculator


def seed_phone():
    db = SessionLocal()
    try:
        slug = 'oneplus-13'
        phone = db.query(Phone).filter(Phone.slug == slug).one_or_none()
        
        if not phone:
            phone = Phone(
                id=uuid.uuid4(),
                brand='OnePlus',
                model='OnePlus 13',
                slug=slug,
                launch_price=69999,
                current_avg_price=64999,
                image_url='https://via.placeholder.com/600x600?text=OnePlus+13',
            )

            phone.spec = PhoneSpec(
                id=uuid.uuid4(),
                battery_mah=6000,
                charging_watts=100,
                processor='Snapdragon 8 Elite',
                ram_gb=12,
                storage_gb=256,
                display_size=6.82,
                display_type='LTPO AMOLED',
                refresh_rate_hz=120,
                peak_brightness_nits=4500,
                camera_main_mp=50,
                os_updates_years=4,
                security_updates_years=6,
            )

            phone.insight = PhoneInsight(
                id=uuid.uuid4(),
                battery_summary='Easily lasts 1.5 to 2 days with normal use. Heavy users can comfortably get a full day.',
                performance_summary='One of the fastest Android phones available. Excellent for gaming and multitasking.',
                display_summary='Flagship-grade display with excellent brightness and ultra-smooth scrolling.',
                camera_summary='Excellent camera system with strong daylight and night performance, though not the absolute best.',
                software_summary='Clean and fast software experience with solid long-term update support.',
                honest_verdict='A true flagship powerhouse with outstanding performance and battery life. Buy it if you prioritize speed and endurance over having the very best camera.',
            )
            db.add(phone)
            db.flush()
            print('Created sample phone: OnePlus 13')
        else:
            print('Phone OnePlus 13 already exists, updating listings.')

        # Delete existing listings to ensure clean seed
        db.query(PriceListing).filter(PriceListing.phone_id == phone.id).delete()

        # Define 4 sample platforms
        listings_data = [
            {
                "platform": "Amazon",
                "seller_name": "Appario Retail Private Ltd",
                "seller_rating": 4.5,
                "seller_reviews_count": 12500,
                "listed_price": 64999,
                "coupon_discount": 1000,
                "bank_discount": 2000,
                "exchange_bonus": 0,
                "delivery_charge": 0,
                "in_stock": True,
                "delivery_eta_days": 2,
                "product_url": "https://www.amazon.in/dp/B0D1234567"
            },
            {
                "platform": "Flipkart",
                "seller_name": "SuperComNet",
                "seller_rating": 4.2,
                "seller_reviews_count": 8400,
                "listed_price": 63999,
                "coupon_discount": 500,
                "bank_discount": 1500,
                "exchange_bonus": 1000,
                "delivery_charge": 50,
                "in_stock": True,
                "delivery_eta_days": 4,
                "product_url": "https://www.flipkart.com/oneplus-13-256gb"
            },
            {
                "platform": "Croma",
                "seller_name": "Croma Retail",
                "seller_rating": 4.6,
                "seller_reviews_count": 3200,
                "listed_price": 64999,
                "coupon_discount": 0,
                "bank_discount": 3000,
                "exchange_bonus": 0,
                "delivery_charge": 0,
                "in_stock": True,
                "delivery_eta_days": 1,
                "product_url": "https://www.croma.com/oneplus-13-256gb"
            },
            {
                "platform": "Reliance Digital",
                "seller_name": "Reliance Retail",
                "seller_rating": 3.9,
                "seller_reviews_count": 450,
                "listed_price": 62999,
                "coupon_discount": 0,
                "bank_discount": 0,
                "exchange_bonus": 0,
                "delivery_charge": 150,
                "in_stock": True,
                "delivery_eta_days": 3,
                "product_url": "https://www.reliancedigital.in/oneplus-13-256gb"
            }
        ]

        for item in listings_data:
            final_price = FinalPriceCalculator.calculate(
                item["listed_price"],
                item["coupon_discount"],
                item["bank_discount"],
                item["exchange_bonus"],
                item["delivery_charge"]
            )
            
            listing = PriceListing(
                id=uuid.uuid4(),
                phone_id=phone.id,
                platform=item["platform"],
                seller_name=item["seller_name"],
                seller_rating=item["seller_rating"],
                seller_reviews_count=item["seller_reviews_count"],
                listed_price=item["listed_price"],
                coupon_discount=item["coupon_discount"],
                bank_discount=item["bank_discount"],
                exchange_bonus=item["exchange_bonus"],
                delivery_charge=item["delivery_charge"],
                final_price=final_price,
                in_stock=item["in_stock"],
                delivery_eta_days=item["delivery_eta_days"],
                product_url=item["product_url"]
            )
            db.add(listing)

        db.commit()
        print('Successfully seeded 4 live price listings for OnePlus 13')
    finally:
        db.close()


if __name__ == '__main__':
    seed_phone()
