from typing import Optional

def interpret_charging(charging_watts: Optional[int], wireless_charging: Optional[bool]) -> str:
    wireless_text = " Supports wireless charging for cable-free convenience." if wireless_charging else ""
    
    if not charging_watts:
        if wireless_charging:
            return "Charging wattage not specified." + wireless_text
        return "Charging specifications not detailed."
    
    if charging_watts < 18:
        summary = f"Slow {charging_watts}W charging. A full charge will likely take over 2 hours."
    elif charging_watts < 30:
        summary = f"Moderate {charging_watts}W charging speed. A full charge takes around 1.5 hours."
    elif charging_watts < 67:
        summary = f"Fast {charging_watts}W charging. Recharges up to 50% in around 30 minutes, full charge in under an hour."
    elif charging_watts < 120:
        summary = f"Very fast {charging_watts}W charging. Recharges to 50% in about 15 minutes, full charge in under 40 minutes."
    else:
        summary = f"Hyper-fast {charging_watts}W charging. Completely recharges the battery in 20-25 minutes."
        
    return summary + wireless_text
