"""
spec_enrichment_service.py
Orchestrates all spec enrichment passes on a PhoneSpec after base normalisation.
Each enricher is isolated in its own try/except block — a failure in one enricher
never breaks the pipeline or the API response.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("uvicorn.error")


class SpecEnrichmentService:
    """
    Runs enrichment passes in order:
    1. Display (brightness label, HDR, protection, PWM)
    2. Software support (OS years, security years, policy label, Android version)
    3. AI features (suite name, feature list)
    4. Connectivity (WiFi, Bluetooth, USB, eSIM)
    5. Build (cooling, materials)
    6. Storage type (UFS)

    Usage:
        enriched = SpecEnrichmentService.enrich(brand, model, raw_specs, normalized)
        # enriched is a copy of normalized with additional fields filled in
    """

    @classmethod
    def enrich(
        cls,
        brand: str,
        model: str,
        raw_specs: Dict[str, Any],
        normalized: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Applies all enrichment passes to the normalized spec dict.

        Args:
            brand:      Phone brand (e.g. "Samsung")
            model:      Phone model (e.g. "Galaxy S24 Ultra")
            raw_specs:  Raw string values scraped from GSMArena (keys like raw_display_type)
            normalized: Already-normalized numeric/cleaned values from normalize_all_specs()

        Returns:
            A merged dict of normalized + enriched fields, safe to iterate and setattr onto PhoneSpec.
        """
        result = dict(normalized)

        # 1. Display enrichment
        try:
            from app.services.specs.display_enrichment import (
                enrich_display_from_raw,
                interpret_brightness,
                interpret_hdr,
                interpret_display_protection,
            )
            raw_display = raw_specs.get("raw_display_type", "") or ""
            raw_brightness = raw_specs.get("raw_brightness", "") or ""
            raw_protection = raw_specs.get("raw_protection", "") or ""

            display_data = enrich_display_from_raw(
                raw_display_type=raw_display,
                raw_brightness=raw_brightness,
                raw_protection=raw_protection,
            )
            result.update(display_data)

            # Human-readable brightness label (if peak_brightness_nits now set)
            peak_nits = result.get("peak_brightness_nits")
            if peak_nits and not result.get("brightness_label"):
                brightness_interp = interpret_brightness(peak_nits)
                result.update(brightness_interp)

            # Human-readable HDR label
            hdr = result.get("hdr_support")
            if hdr:
                result["hdr_label"] = interpret_hdr(hdr)

            # Human-readable display protection label
            protection = result.get("display_protection")
            if protection:
                result["display_protection_label"] = interpret_display_protection(protection)

        except Exception as exc:
            logger.warning("SpecEnrichmentService: Display enrichment failed: %s", exc)

        # 2. Software support enrichment
        try:
            from app.services.specs.software_support_service import get_software_support
            sw = get_software_support(brand, model)
            # Only overwrite if not already populated from GSMArena
            if not result.get("os_updates_years"):
                result["os_updates_years"] = sw.get("os_updates_years")
            if not result.get("security_updates_years"):
                result["security_updates_years"] = sw.get("security_updates_years")
            if not result.get("update_policy_label"):
                result["update_policy_label"] = sw.get("update_policy_label")
            # Android version from raw_software field if not set
            if not result.get("android_version"):
                result["android_version"] = cls._extract_android_version(
                    raw_specs.get("raw_software", "")
                )
        except Exception as exc:
            logger.warning("SpecEnrichmentService: Software support enrichment failed: %s", exc)

        # 3. AI features enrichment
        try:
            from app.services.specs.manufacturer_data_parser import get_ai_features
            ai_data = get_ai_features(brand, model)
            if not result.get("ai_suite_name"):
                result["ai_suite_name"] = ai_data.get("ai_suite_name")
            if not result.get("ai_features"):
                result["ai_features"] = ai_data.get("ai_features")
        except Exception as exc:
            logger.warning("SpecEnrichmentService: AI features enrichment failed: %s", exc)

        # 4. Connectivity enrichment
        try:
            from app.services.specs.normalization_service import (
                normalize_wifi_version,
                normalize_bluetooth_version,
                normalize_usb_type,
                normalize_ufs_type,
                normalize_esim,
            )
            raw_conn = raw_specs.get("raw_connectivity", "") or ""
            raw_storage_raw = raw_specs.get("raw_storage", "") or ""

            if not result.get("wifi_version"):
                result["wifi_version"] = normalize_wifi_version(raw_conn)
            if not result.get("bluetooth_version"):
                result["bluetooth_version"] = normalize_bluetooth_version(raw_conn)
            if not result.get("usb_type"):
                result["usb_type"] = normalize_usb_type(raw_conn)
            if result.get("esim") is None:
                result["esim"] = normalize_esim(raw_conn)
            if not result.get("ufs_type"):
                result["ufs_type"] = normalize_ufs_type(raw_storage_raw)

            # Manufacturer connectivity defaults fallback
            from app.services.specs.manufacturer_data_parser import get_connectivity_info
            conn_defaults = get_connectivity_info(brand, model)
            for k, v in conn_defaults.items():
                if not result.get(k):
                    result[k] = v

        except Exception as exc:
            logger.warning("SpecEnrichmentService: Connectivity enrichment failed: %s", exc)

        # 5. Build enrichment (cooling, materials)
        try:
            from app.services.specs.manufacturer_data_parser import get_build_info
            build_data = get_build_info(brand, model)
            if not result.get("cooling_system"):
                result["cooling_system"] = build_data.get("cooling_system")
            if not result.get("build_materials"):
                result["build_materials"] = build_data.get("build_materials")
        except Exception as exc:
            logger.warning("SpecEnrichmentService: Build enrichment failed: %s", exc)

        # 6. Reverse charging enrichment
        try:
            raw_charging = raw_specs.get("raw_wireless_charging", "") or raw_specs.get("raw_charging_watts", "") or ""
            if result.get("reverse_charging") is None:
                result["reverse_charging"] = cls._detect_reverse_charging(raw_charging)
        except Exception as exc:
            logger.warning("SpecEnrichmentService: Reverse charging detection failed: %s", exc)

        return result

    @staticmethod
    def _extract_android_version(raw_software: Optional[str]) -> Optional[str]:
        """Extract Android version string from raw GSMArena software field."""
        import re
        if not raw_software:
            return None
        match = re.search(r"Android\s+(\d+(?:\.\d+)?)", raw_software, re.IGNORECASE)
        if match:
            return f"Android {match.group(1)}"
        return None

    @staticmethod
    def _detect_reverse_charging(raw_charging: Optional[str]) -> bool:
        """Detect reverse wireless charging from raw charging text."""
        if not raw_charging:
            return False
        keywords = ["reverse wireless", "reverse charging", "powershare", "reverse wired"]
        return any(kw in raw_charging.lower() for kw in keywords)
