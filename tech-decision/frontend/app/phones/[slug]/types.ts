export interface PhoneSpec {
  battery_mah: number;
  charging_watts: number;
  processor: string;
  ram_gb: number;
  storage_gb: number;
  display_size: number;
  display_type: string;
  refresh_rate_hz: number;
  peak_brightness_nits: number;
  camera_main_mp: number;
  os_updates_years: number;
  security_updates_years: number;

  // Performance/Core
  chipset?: string | null;
  cpu?: string | null;
  gpu?: string | null;
  ram?: number | null;
  storage?: number | null;

  // Battery
  wireless_charging?: boolean | null;
  reverse_charging?: boolean | null;

  // Display
  display_resolution?: string | null;
  refresh_rate?: number | null;
  hdr_support?: string | null;
  display_protection?: string | null;
  pwm_dimming?: boolean | null;
  real_world_brightness_nits?: number | null;
  brightness_label?: string | null;
  hdr_label?: string | null;
  display_protection_label?: string | null;

  // Camera
  main_camera?: string | null;
  ultrawide_camera?: string | null;
  telephoto_camera?: string | null;
  selfie_camera?: string | null;

  // Build
  weight?: number | null;
  ip_rating?: string | null;
  cooling_system?: string | null;
  build_materials?: string | null;

  // Connectivity
  wifi_version?: string | null;
  bluetooth_version?: string | null;
  usb_type?: string | null;
  nfc?: boolean | null;
  esim?: boolean | null;

  // Software
  android_version?: string | null;
  update_policy_label?: string | null;

  // Storage
  ufs_type?: string | null;

  // AI Features
  ai_features?: string[] | null;
  ai_suite_name?: string | null;
}

export interface PhoneInsight {
  battery_summary: string;
  performance_summary: string;
  display_summary: string;
  camera_summary: string;
  software_summary: string;
  honest_verdict: string;
}

export interface PhoneInterpretation {
  id: string;
  phone_id: string;
  battery_summary?: string | null;
  normal_usage?: string | null;
  heavy_usage?: string | null;
  charging_summary?: string | null;
  performance_summary?: string | null;
  display_summary?: string | null;
  camera_summary?: string | null;
  pros?: string[] | null;
  cons?: string[] | null;
  verdict?: string | null;
  expected_experience?: string | null;
}

export interface PhoneVariant {
  id: string;
  phone_id: string;
  ram_gb: number;
  storage_gb: number;
  color?: string | null;
  sku_code?: string | null;
  slug: string;
}

export interface PhoneDetail {
  id: string;
  brand: string;
  model: string;
  slug: string;
  launch_price: number | null;
  current_avg_price: number | null;
  image_url?: string | null;
  created_at: string;
  spec?: PhoneSpec | null;
  insight: PhoneInsight | null;
  interpretation?: PhoneInterpretation | null;
  price_intelligence?: string | null;
  variants?: PhoneVariant[] | null;
}

export interface PriceListing {
  id: string;
  phone_id?: string | null;
  variant_id?: string | null;
  platform: string;
  seller_name: string;
  seller_rating?: number | null;
  seller_reviews_count?: number | null;
  listed_price: number;
  original_mrp?: number | null;
  coupon_discount: number;
  bank_discount: number;
  exchange_bonus: number;
  cashback_amount?: number;
  delivery_charge: number;
  final_price: number;
  in_stock: boolean;
  delivery_eta_days?: number | null;
  product_url: string;
  emi_available?: boolean;
  emi_months?: number | null;
  fake_discount_flag?: boolean;
  discount_authenticity_score?: number;
  price_intelligence_note?: string | null;
  updated_at: string;
  trust_score: number;
}

export interface PriceComparisonResponse {
  listings: PriceListing[];
  best_platform: PriceListing | null;
  summary: string;
}


