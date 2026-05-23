from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PhoneSpecBase(BaseModel):
    battery_mah: Optional[int] = None
    charging_watts: Optional[int] = None
    processor: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    display_size: Optional[float] = None
    display_type: Optional[str] = None
    refresh_rate_hz: Optional[int] = None
    peak_brightness_nits: Optional[int] = None
    camera_main_mp: Optional[int] = None
    os_updates_years: Optional[int] = None
    security_updates_years: Optional[int] = None

    # Performance
    chipset: Optional[str] = None
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    ram: Optional[int] = None
    storage: Optional[int] = None

    # Battery
    wireless_charging: Optional[bool] = None
    reverse_charging: Optional[bool] = None

    # Display
    display_resolution: Optional[str] = None
    refresh_rate: Optional[int] = None
    hdr_support: Optional[str] = None
    display_protection: Optional[str] = None
    pwm_dimming: Optional[bool] = None
    real_world_brightness_nits: Optional[int] = None
    brightness_label: Optional[str] = None
    hdr_label: Optional[str] = None
    display_protection_label: Optional[str] = None

    # Camera
    main_camera: Optional[str] = None
    ultrawide_camera: Optional[str] = None
    telephoto_camera: Optional[str] = None
    selfie_camera: Optional[str] = None

    # Build
    weight: Optional[int] = None
    ip_rating: Optional[str] = None
    cooling_system: Optional[str] = None
    build_materials: Optional[str] = None

    # Connectivity
    wifi_version: Optional[str] = None
    bluetooth_version: Optional[str] = None
    usb_type: Optional[str] = None
    nfc: Optional[bool] = None
    esim: Optional[bool] = None

    # Software
    android_version: Optional[str] = None
    update_policy_label: Optional[str] = None

    # Storage type
    ufs_type: Optional[str] = None

    # AI Features
    ai_features: Optional[list] = None
    ai_suite_name: Optional[str] = None

    # Raw extracted strings
    raw_chipset: Optional[str] = None
    raw_cpu: Optional[str] = None
    raw_gpu: Optional[str] = None
    raw_ram: Optional[str] = None
    raw_storage: Optional[str] = None
    raw_battery_mah: Optional[str] = None
    raw_charging_watts: Optional[str] = None
    raw_wireless_charging: Optional[str] = None
    raw_display_size: Optional[str] = None
    raw_display_resolution: Optional[str] = None
    raw_refresh_rate: Optional[str] = None
    raw_display_type: Optional[str] = None
    raw_main_camera: Optional[str] = None
    raw_ultrawide_camera: Optional[str] = None
    raw_telephoto_camera: Optional[str] = None
    raw_selfie_camera: Optional[str] = None
    raw_weight: Optional[str] = None
    raw_ip_rating: Optional[str] = None
    raw_connectivity: Optional[str] = None
    raw_software: Optional[str] = None
    raw_colors: Optional[str] = None


class PhoneSpecRead(PhoneSpecBase):
    id: UUID
    phone_id: UUID

    model_config = ConfigDict(from_attributes=True)


class PhoneSpecsResponse(BaseModel):
    brand: str
    model: str
    chipset: Optional[str] = None
    ram: Optional[int] = None
    storage: Optional[int] = None
    battery_mah: Optional[int] = None
    refresh_rate: Optional[int] = None


class PhoneInsightBase(BaseModel):
    battery_summary: str
    performance_summary: str
    display_summary: str
    camera_summary: str
    software_summary: str
    honest_verdict: str


class PhoneInsightRead(PhoneInsightBase):
    id: UUID
    phone_id: UUID

    model_config = ConfigDict(from_attributes=True)


class PhoneSearchResult(BaseModel):
    brand: str
    model: str
    slug: str
    image_url: Optional[str] = None
    current_avg_price: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PhoneDiscoverySearchResult(BaseModel):
    brand: str
    model: str
    slug: str
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    current_avg_price: Optional[int] = None
    match_score: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class PhoneBase(BaseModel):
    brand: str
    model: str
    slug: str
    launch_price: Optional[int] = None
    current_avg_price: Optional[int] = None
    image_url: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None


class PhoneVariantRead(BaseModel):
    id: UUID
    phone_id: UUID
    ram_gb: int
    storage_gb: int
    color: Optional[str] = None
    sku_code: Optional[str] = None
    slug: str

    model_config = ConfigDict(from_attributes=True)


class PhoneInterpretationRead(BaseModel):
    id: UUID
    phone_id: UUID
    battery_summary: Optional[str] = None
    normal_usage: Optional[str] = None
    heavy_usage: Optional[str] = None
    charging_summary: Optional[str] = None
    performance_summary: Optional[str] = None
    display_summary: Optional[str] = None
    camera_summary: Optional[str] = None
    pros: Optional[list[str]] = None
    cons: Optional[list[str]] = None
    verdict: Optional[str] = None
    expected_experience: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PhoneRead(PhoneBase):
    id: UUID
    created_at: datetime
    spec: Optional[PhoneSpecRead] = None
    insight: Optional[PhoneInsightRead] = None
    interpretation: Optional[PhoneInterpretationRead] = None
    price_intelligence: Optional[str] = None
    variants: list[PhoneVariantRead] = []

    model_config = ConfigDict(from_attributes=True)


class PriceListingRead(BaseModel):
    id: UUID
    phone_id: UUID
    platform: str
    seller_name: str
    seller_rating: Optional[float] = None
    seller_reviews_count: Optional[int] = None
    listed_price: int
    original_mrp: Optional[int] = None
    coupon_discount: int
    bank_discount: int
    exchange_bonus: int
    cashback_amount: int = 0
    delivery_charge: int
    final_price: int
    in_stock: bool
    delivery_eta_days: Optional[int] = None
    product_url: str
    emi_available: bool = False
    emi_months: Optional[int] = None
    fake_discount_flag: bool = False
    discount_authenticity_score: int = 100
    price_intelligence_note: Optional[str] = None
    updated_at: datetime
    trust_score: int

    model_config = ConfigDict(from_attributes=True)


class VariantPriceRead(BaseModel):
    id: UUID
    variant_id: UUID
    platform: str
    seller_name: str
    seller_rating: Optional[float] = None
    seller_reviews_count: Optional[int] = None
    listed_price: int
    original_mrp: Optional[int] = None
    coupon_discount: int
    bank_discount: int
    exchange_bonus: int
    cashback_amount: int = 0
    delivery_charge: int
    final_price: int
    in_stock: bool
    delivery_eta_days: Optional[int] = None
    product_url: str
    emi_available: bool = False
    emi_months: Optional[int] = None
    fake_discount_flag: bool = False
    discount_authenticity_score: int = 100
    price_intelligence_note: Optional[str] = None
    updated_at: datetime
    trust_score: int

    model_config = ConfigDict(from_attributes=True)


class PriceComparisonResponse(BaseModel):
    listings: list[VariantPriceRead]
    best_platform: Optional[VariantPriceRead] = None
    summary: str


class PhoneDecisionResponse(BaseModel):
    decision: str
    headline: str
    summary: str
    pros: list[str]
    cons: list[str]
    confidence_score: int



