from typing import Dict, Any, Optional

def interpret_battery(battery_mah: Optional[int]) -> Dict[str, Any]:
    if not battery_mah:
        return {
            "battery_summary": "Battery details not specified. Performance will vary depending on display and processor efficiency.",
            "normal_usage": "TBD",
            "heavy_usage": "TBD"
        }
    
    if battery_mah < 3500:
        return {
            "battery_summary": f"Compact {battery_mah} mAh battery capacity. Will likely require charging mid-day under standard usage.",
            "normal_usage": "0.6 - 0.8 days",
            "heavy_usage": "3 - 4 hours"
        }
    elif battery_mah < 4300:
        return {
            "battery_summary": f"Moderate {battery_mah} mAh battery. Good for light daily tasks, but heavy usage will drain it before the day ends.",
            "normal_usage": "0.8 - 1.0 day",
            "heavy_usage": "4.5 - 5.5 hours"
        }
    elif battery_mah < 5000:
        return {
            "battery_summary": f"Good {battery_mah} mAh battery capacity. Solidly lasts a full day of standard mixed usage.",
            "normal_usage": "1.0 - 1.2 days",
            "heavy_usage": "6 - 7 hours"
        }
    elif battery_mah < 6000:
        return {
            "battery_summary": f"Excellent {battery_mah} mAh battery capacity. Easily lasts a full day or more of standard usage with decent reserve.",
            "normal_usage": "1.2 - 1.5 days",
            "heavy_usage": "7 - 9 hours"
        }
    else:
        return {
            "battery_summary": f"Massive {battery_mah} mAh battery. Built for extreme endurance, easily spanning up to two days on a single charge.",
            "normal_usage": "1.5 - 2.0 days",
            "heavy_usage": "9 - 11 hours"
        }
