from sqlalchemy.orm import Session
from app.models.phone import Phone, PhoneInterpretation
from app.services.interpreter.battery_interpreter import interpret_battery
from app.services.interpreter.charging_interpreter import interpret_charging
from app.services.interpreter.performance_interpreter import interpret_performance
from app.services.interpreter.display_interpreter import interpret_display
from app.services.interpreter.camera_interpreter import interpret_camera

class DeviceSummaryService:
    @staticmethod
    def generate_and_save(db: Session, phone: Phone) -> PhoneInterpretation:
        spec = phone.spec
        
        # If there are no specs, create fallback interpretation
        if not spec:
            battery_data = interpret_battery(None)
            charging_summary = interpret_charging(None, None)
            perf_data = interpret_performance(None, None)
            display_summary = interpret_display(None, None, None, None)
            camera_summary = interpret_camera(None, None, None, None)
            pros = ["Basic smartphone functions"]
            cons = ["Specifications not fully loaded"]
            verdict = "Technical specifications are not available for this phone yet. Expected experience is standard for its category."
            expected_experience = "Expected experience is standard. Please check back later when specifications are fully fetched."
        else:
            # 1. Run individual interpreters
            battery_data = interpret_battery(spec.battery_mah)
            charging_summary = interpret_charging(spec.charging_watts, spec.wireless_charging)
            
            ram_val = spec.ram_gb if spec.ram_gb is not None else spec.ram
            perf_data = interpret_performance(spec.chipset, ram_val)
            
            rr_val = spec.refresh_rate_hz if spec.refresh_rate_hz is not None else spec.refresh_rate
            display_summary = interpret_display(spec.display_size, spec.display_type, rr_val, spec.display_resolution)
            
            camera_summary = interpret_camera(spec.main_camera, spec.ultrawide_camera, spec.telephoto_camera, spec.selfie_camera)
            
            # 2. Compile Pros and Cons
            pros = []
            cons = []
            
            # Battery size
            if spec.battery_mah:
                if spec.battery_mah >= 5000:
                    pros.append(f"Long-lasting battery life ({spec.battery_mah} mAh)")
                elif spec.battery_mah < 4000:
                    cons.append(f"Smaller battery capacity ({spec.battery_mah} mAh); may require daily mid-day top-ups")
                    
            # Charging wattage
            if spec.charging_watts:
                if spec.charging_watts >= 33:
                    pros.append(f"Fast charging support ({spec.charging_watts}W)")
                elif spec.charging_watts <= 15:
                    cons.append(f"Slow {spec.charging_watts}W charging speed")
            else:
                cons.append("Charging speed is not fast-charge certified")
                
            # Wireless charging
            if spec.wireless_charging:
                pros.append("Convenient wireless charging support")
                
            # OIS (Optical Image Stabilization)
            main_lower = (spec.main_camera or "").lower()
            if "ois" in main_lower or "optical image stabilization" in main_lower:
                pros.append("Optical Image Stabilization (OIS) on main camera")
            else:
                cons.append("Lacks hardware optical stabilization on main camera")
                
            # Display Type
            type_lower = (spec.display_type or "").lower()
            if any(kw in type_lower for kw in ["amoled", "oled", "ltpo"]):
                pros.append(f"Vibrant {spec.display_type} display panel")
            else:
                cons.append("Uses basic LCD panel with standard contrast")
                
            # Refresh Rate
            if rr_val:
                if rr_val >= 90:
                    pros.append(f"Smooth {rr_val}Hz high refresh rate screen")
                else:
                    cons.append("Standard 60Hz display feels less fluid than modern screens")
            else:
                cons.append("Standard 60Hz screen refresh rate")
                
            # IP Rating
            ip_val = (spec.ip_rating or "").lower()
            if "67" in ip_val or "68" in ip_val:
                pros.append(f"IP67/IP68 water and dust resistance ({spec.ip_rating})")
            elif not spec.ip_rating or spec.ip_rating == "No":
                cons.append("No official IP water/dust protection rating")
                
            # RAM
            if ram_val:
                if ram_val >= 8:
                    pros.append(f"Generous RAM ({ram_val}GB) for smooth multitasking")
                elif ram_val < 6:
                    cons.append(f"Limited RAM capacity ({ram_val}GB); background apps may reload frequently")
                    
            # Telephoto Zoom
            if spec.telephoto_camera:
                pros.append("Dedicated optical zoom camera for close-up shots")
            else:
                cons.append("No dedicated optical zoom lens")
                
            # Fallbacks if list is empty
            if not pros:
                pros.append("Compact and lightweight build")
            if not cons:
                cons.append("No major drawbacks identified for its category")
                
            # 3. Formulate Verdict & Expected Experience based on performance tier
            perf_level = perf_data["performance_level"]
            if perf_level == "Flagship":
                verdict = "A premium powerhouse device offering top-of-the-line performance, excellent display quality, and a highly versatile camera system. Highly recommended for power users, gamers, and mobile enthusiasts who want the best experience without compromises."
                expected_experience = "Expect an ultra-fluid, latency-free experience. Apps launch instantly, and demanding games run smoothly at maximum graphics settings. Combined with fast charging and a high-refresh-rate display, it feels incredibly snappy and responsive."
            elif perf_level == "Mid-Range":
                verdict = "A solid, well-rounded smartphone that strikes an excellent balance between performance and price. It handles all daily tasks and moderate gaming with ease, making it a highly practical option for value-conscious buyers."
                expected_experience = "Expect a smooth, reliable experience for daily activities. Social media scrolling, web browsing, and app switching feel seamless. While heavy gaming might require lower graphics settings, general performance remains consistently smooth."
            else:
                verdict = "A budget-friendly choice tailored for standard everyday communication, basic web browsing, and media consumption. It offers great value for casual users, but isn't built for heavy multitasking or resource-heavy gaming."
                expected_experience = "Expect a functional experience optimized for simple tasks. Scrolling and switching between apps may show occasional micro-stutters, and loading heavy files or games will take longer, but it gets the job done for standard use."
                
        # Fetch or create the interpretation record
        interpretation = phone.interpretation
        if not interpretation:
            interpretation = PhoneInterpretation(phone_id=phone.id)
            db.add(interpretation)
            
        interpretation.battery_summary = battery_data["battery_summary"]
        interpretation.normal_usage = battery_data["normal_usage"]
        interpretation.heavy_usage = battery_data["heavy_usage"]
        interpretation.charging_summary = charging_summary
        interpretation.performance_summary = perf_data["performance_summary"]
        interpretation.display_summary = display_summary
        interpretation.camera_summary = camera_summary
        interpretation.pros = pros
        interpretation.cons = cons
        interpretation.verdict = verdict
        interpretation.expected_experience = expected_experience
        
        try:
            db.commit()
            db.refresh(interpretation)
            return interpretation
        except Exception as exc:
            db.rollback()
            try:
                # If another concurrent request already committed the interpretation, update it
                from sqlalchemy import select
                stmt = select(PhoneInterpretation).where(PhoneInterpretation.phone_id == phone.id)
                existing = db.scalars(stmt).first()
                if existing:
                    existing.battery_summary = battery_data["battery_summary"]
                    existing.normal_usage = battery_data["normal_usage"]
                    existing.heavy_usage = battery_data["heavy_usage"]
                    existing.charging_summary = charging_summary
                    existing.performance_summary = perf_data["performance_summary"]
                    existing.display_summary = display_summary
                    existing.camera_summary = camera_summary
                    existing.pros = pros
                    existing.cons = cons
                    existing.verdict = verdict
                    existing.expected_experience = expected_experience
                    db.commit()
                    db.refresh(existing)
                    return existing
            except Exception as retry_exc:
                db.rollback()
            raise exc
