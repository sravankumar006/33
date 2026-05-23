import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Phone(Base):
    __tablename__ = 'phones'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    brand = Column(String(120), nullable=False, index=True)
    model = Column(String(180), nullable=False, index=True)
    slug = Column(String(210), nullable=False, unique=True, index=True)
    launch_price = Column(Integer, nullable=True)
    current_avg_price = Column(Integer, nullable=True)
    image_url = Column(Text, nullable=True)
    source = Column(String(100), nullable=True)
    source_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), nullable=False, index=True)

    spec = relationship(
        'PhoneSpec',
        back_populates='phone',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    insight = relationship(
        'PhoneInsight',
        back_populates='phone',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    price_listings = relationship(
        'PriceListing',
        back_populates='phone',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    variants = relationship(
        'PhoneVariant',
        back_populates='phone',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )
    interpretation = relationship(
        'PhoneInterpretation',
        back_populates='phone',
        uselist=False,
        cascade='all, delete-orphan',
        passive_deletes=True,
    )


class PhoneSpec(Base):
    __tablename__ = 'phone_specs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    phone_id = Column(UUID(as_uuid=True), ForeignKey('phones.id', ondelete='CASCADE'), unique=True, nullable=False)
    battery_mah = Column(Integer, nullable=True)
    charging_watts = Column(Integer, nullable=True)
    processor = Column(String(180), nullable=True)
    ram_gb = Column(Integer, nullable=True)
    storage_gb = Column(Integer, nullable=True)
    display_size = Column(Float, nullable=True)
    display_type = Column(String(120), nullable=True)
    refresh_rate_hz = Column(Integer, nullable=True)
    peak_brightness_nits = Column(Integer, nullable=True)
    camera_main_mp = Column(Integer, nullable=True)
    os_updates_years = Column(Integer, nullable=True)
    security_updates_years = Column(Integer, nullable=True)

    # Performance
    chipset = Column(String(180), nullable=True)
    cpu = Column(String(250), nullable=True)
    gpu = Column(String(180), nullable=True)
    ram = Column(Integer, nullable=True)
    storage = Column(Integer, nullable=True)

    # Battery
    wireless_charging = Column(Boolean, nullable=True)
    reverse_charging = Column(Boolean, nullable=True)

    # Display
    display_resolution = Column(String(120), nullable=True)
    refresh_rate = Column(Integer, nullable=True)
    hdr_support = Column(String(120), nullable=True)        # e.g. "HDR10+", "Dolby Vision"
    display_protection = Column(String(120), nullable=True)  # e.g. "Gorilla Glass Victus 2"
    pwm_dimming = Column(Boolean, nullable=True)
    real_world_brightness_nits = Column(Integer, nullable=True)
    brightness_label = Column(String(180), nullable=True)   # human-readable e.g. "Excellent outdoor visibility"

    # Camera
    main_camera = Column(String(250), nullable=True)
    ultrawide_camera = Column(String(250), nullable=True)
    telephoto_camera = Column(String(250), nullable=True)
    selfie_camera = Column(String(250), nullable=True)

    # Build
    weight = Column(Integer, nullable=True)
    ip_rating = Column(String(80), nullable=True)
    cooling_system = Column(String(180), nullable=True)     # e.g. "Vapor Chamber", "Graphene"
    build_materials = Column(String(250), nullable=True)    # e.g. "Titanium frame, Gorilla Glass back"

    # Connectivity
    wifi_version = Column(String(60), nullable=True)        # e.g. "Wi-Fi 7"
    bluetooth_version = Column(String(60), nullable=True)   # e.g. "5.4"
    usb_type = Column(String(80), nullable=True)            # e.g. "USB 3.2 Gen 2 Type-C"
    nfc = Column(Boolean, nullable=True)
    esim = Column(Boolean, nullable=True)

    # Software
    android_version = Column(String(60), nullable=True)     # e.g. "Android 15"
    update_policy_label = Column(String(250), nullable=True) # human label e.g. "Among best in Android"

    # Storage type
    ufs_type = Column(String(40), nullable=True)            # e.g. "UFS 4.0"

    # AI Features
    ai_features = Column(JSON, nullable=True)               # list of feature strings
    ai_suite_name = Column(String(120), nullable=True)      # e.g. "Galaxy AI", "Google Gemini"

    # Raw extracted strings
    raw_chipset = Column(Text, nullable=True)
    raw_cpu = Column(Text, nullable=True)
    raw_gpu = Column(Text, nullable=True)
    raw_ram = Column(Text, nullable=True)
    raw_storage = Column(Text, nullable=True)
    raw_battery_mah = Column(Text, nullable=True)
    raw_charging_watts = Column(Text, nullable=True)
    raw_wireless_charging = Column(Text, nullable=True)
    raw_display_size = Column(Text, nullable=True)
    raw_display_resolution = Column(Text, nullable=True)
    raw_refresh_rate = Column(Text, nullable=True)
    raw_display_type = Column(Text, nullable=True)
    raw_main_camera = Column(Text, nullable=True)
    raw_ultrawide_camera = Column(Text, nullable=True)
    raw_telephoto_camera = Column(Text, nullable=True)
    raw_selfie_camera = Column(Text, nullable=True)
    raw_weight = Column(Text, nullable=True)
    raw_ip_rating = Column(Text, nullable=True)
    raw_connectivity = Column(Text, nullable=True)
    raw_software = Column(Text, nullable=True)
    raw_colors = Column(Text, nullable=True)

    phone = relationship('Phone', back_populates='spec')


class PhoneInsight(Base):
    __tablename__ = 'phone_insights'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    phone_id = Column(UUID(as_uuid=True), ForeignKey('phones.id', ondelete='CASCADE'), unique=True, nullable=False)
    battery_summary = Column(Text, nullable=False)
    performance_summary = Column(Text, nullable=False)
    display_summary = Column(Text, nullable=False)
    camera_summary = Column(Text, nullable=False)
    software_summary = Column(Text, nullable=False)
    honest_verdict = Column(Text, nullable=False)

    phone = relationship('Phone', back_populates='insight')


class PriceListing(Base):
    __tablename__ = 'price_listings'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    phone_id = Column(UUID(as_uuid=True), ForeignKey('phones.id', ondelete='CASCADE'), nullable=False)
    platform = Column(String(100), nullable=False)
    seller_name = Column(String(200), nullable=False)
    seller_rating = Column(Float, nullable=True)
    seller_reviews_count = Column(Integer, nullable=True)
    listed_price = Column(Integer, nullable=False)
    original_mrp = Column(Integer, nullable=True)           # Platform-stated MRP (often inflated)
    coupon_discount = Column(Integer, default=0, nullable=False)
    bank_discount = Column(Integer, default=0, nullable=False)
    exchange_bonus = Column(Integer, default=0, nullable=False)
    cashback_amount = Column(Integer, default=0, nullable=False)
    delivery_charge = Column(Integer, default=0, nullable=False)
    final_price = Column(Integer, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    delivery_eta_days = Column(Integer, nullable=True)
    product_url = Column(Text, nullable=False)
    emi_available = Column(Boolean, default=False, nullable=False)
    emi_months = Column(Integer, nullable=True)             # e.g. 12 months
    # Discount authenticity
    fake_discount_flag = Column(Boolean, default=False, nullable=False)
    discount_authenticity_score = Column(Integer, default=100, nullable=False)  # 0-100
    price_intelligence_note = Column(Text, nullable=True)   # plain-English pricing insight
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    phone = relationship('Phone', back_populates='price_listings')


class PhoneInterpretation(Base):
    __tablename__ = 'phone_interpretations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    phone_id = Column(UUID(as_uuid=True), ForeignKey('phones.id', ondelete='CASCADE'), unique=True, nullable=False)
    battery_summary = Column(Text, nullable=True)
    normal_usage = Column(String(100), nullable=True)
    heavy_usage = Column(String(100), nullable=True)
    charging_summary = Column(Text, nullable=True)
    performance_summary = Column(Text, nullable=True)
    display_summary = Column(Text, nullable=True)
    camera_summary = Column(Text, nullable=True)
    pros = Column(JSON, nullable=True)
    cons = Column(JSON, nullable=True)
    verdict = Column(Text, nullable=True)
    expected_experience = Column(Text, nullable=True)

    phone = relationship('Phone', back_populates='interpretation')


class PhoneVariant(Base):
    __tablename__ = 'phone_variants'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    phone_id = Column(UUID(as_uuid=True), ForeignKey('phones.id', ondelete='CASCADE'), nullable=False, index=True)
    ram_gb = Column(Integer, nullable=False)
    storage_gb = Column(Integer, nullable=False)
    color = Column(String(100), nullable=True)
    sku_code = Column(String(100), nullable=True)
    slug = Column(String(250), nullable=False, unique=True, index=True)

    phone = relationship('Phone', back_populates='variants')
    prices = relationship(
        'VariantPrice',
        back_populates='variant',
        cascade='all, delete-orphan',
        passive_deletes=True,
    )


class VariantPrice(Base):
    __tablename__ = 'variant_prices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('phone_variants.id', ondelete='CASCADE'), nullable=False, index=True)
    platform = Column(String(100), nullable=False)
    seller_name = Column(String(200), nullable=False)
    seller_rating = Column(Float, nullable=True)
    seller_reviews_count = Column(Integer, nullable=True)
    listed_price = Column(Integer, nullable=False)
    original_mrp = Column(Integer, nullable=True)
    coupon_discount = Column(Integer, default=0, nullable=False)
    bank_discount = Column(Integer, default=0, nullable=False)
    exchange_bonus = Column(Integer, default=0, nullable=False)
    cashback_amount = Column(Integer, default=0, nullable=False)
    delivery_charge = Column(Integer, default=0, nullable=False)
    final_price = Column(Integer, nullable=False)
    in_stock = Column(Boolean, default=True, nullable=False)
    delivery_eta_days = Column(Integer, nullable=True)
    product_url = Column(Text, nullable=False)
    emi_available = Column(Boolean, default=False, nullable=False)
    emi_months = Column(Integer, nullable=True)
    fake_discount_flag = Column(Boolean, default=False, nullable=False)
    discount_authenticity_score = Column(Integer, default=100, nullable=False)
    price_intelligence_note = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

    variant = relationship('PhoneVariant', back_populates='prices')

