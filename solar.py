# -*- coding: utf-8 -*-
import streamlit as st
import math
import re
import pandas as pd

# --- Session Initialization ---
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'start' not in st.session_state:
    st.session_state.start = False
if 'estimation_done' not in st.session_state:
    st.session_state.estimation_done = False
if 'selected_installer' not in st.session_state:
    st.session_state.selected_installer = None
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Unknown Location"
if 'sun_hours' not in st.session_state:
    st.session_state.sun_hours = 5.0
if 'preset' not in st.session_state:
    st.session_state.preset = "Custom"
if 'show_contact_form' not in st.session_state:
    st.session_state.show_contact_form = False
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False

# --- Navigation Functions ---
def next_step():
    st.session_state.step += 1
    st.session_state.calculation_done = False
    st.rerun()

def prev_step():
    st.session_state.step -= 1
    st.rerun()

# --- Welcome Screen ---
if not st.session_state.start:
    st.set_page_config(page_title="Smart Solar Advisor", page_icon="🌞")
    st.title("Smart Solar System Estimator")
    st.subheader("Make smarter solar decisions in minutes ⚡")
    st.write("Welcome to the app ❤️.. Estimate your solar needs instantly & connect with installers.")
    st.write("You'll also get a suggestion for battery backup and savings comparison.")
    if st.button("🚀 Get Started", key="start_btn"):
        st.session_state.start = True
        st.rerun()
    st.stop()

# --- Page Config ---
st.set_page_config(page_title="Smart Solar Advisor", page_icon="🌞")
st.title("📊 Smart Solar System Estimator")

# --- Sun Hours Dictionary ---
city_sun_hours = {
    "Delhi": 5.5, "Mumbai": 4.5, "Chennai": 5.3,
    "Bangalore": 5.2, "Hyderabad": 5.4, "Ahmedabad": 5.6,
    "Kolkata": 4.8, "Jaipur": 5.7, "Lucknow": 5.2,
    "Custom (Enter manually)": None
}

# --- Step 0: Mode Selection ---
if st.session_state.step == 0:
    st.subheader("Step 1: Choose Estimation Mode")
    st.session_state.mode = st.radio(
        "Choose Estimation Mode:",
        ["Monthly Units Estimator", "Appliance-Based Estimator"],
        key="mode_selector"
    )
    if st.button("Next ➡", key="step0_next"):
        next_step()

# ---------------- MODE 1 ------------------
elif st.session_state.step == 1 and st.session_state.mode == "Monthly Units Estimator":
    st.subheader("Step 2: Monthly Units Estimation")

    st.session_state.selected_city = st.selectbox("Select Your City/Location:", list(city_sun_hours.keys()), key="monthly_city")
    st.session_state.sun_hours = st.number_input("Enter average sun hours per day:",
                                min_value=1.0, max_value=7.0, value=5.0,
                                key="monthly_sun_hours") if st.session_state.selected_city == "Custom (Enter manually)" else city_sun_hours[st.session_state.selected_city]
    
    with st.expander("📈 Monthly Units Estimator", expanded=True):
        monthly_units_input = st.number_input("Enter your average monthly electricity usage (kWh):", min_value=0.0, value=300.0, key="monthly_units")
        unit_rate = st.number_input("Your grid electricity rate (₹/unit):", min_value=1.0, value=8.0, key="monthly_unit_rate")
        area_avail = st.number_input("Available installation area (sq. meters):", min_value=1, key="monthly_area")

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅ Back", on_click=prev_step, key="monthly_back")
    with col2:
        if st.button("Next ➡", key="monthly_next"):
            # Perform calculations
            solar_output_per_kw = round(st.session_state.sun_hours * 365, 1)
            area_per_kw = 10
            cost_per_kw = 50000
            
            daily_energy_kwh = round(monthly_units_input / 30, 2)
            required_kw = round(monthly_units_input / (solar_output_per_kw / 12), 2)
            area_needed = round(required_kw * area_per_kw, 2)
            cost_estimate = round(required_kw * cost_per_kw)
            monthly_grid_cost = round(monthly_units_input * unit_rate)
            payback_years = round(cost_estimate / (monthly_grid_cost * 12), 1)
            usable_battery_kwh = round(daily_energy_kwh / 0.8, 2)
            battery_capacity_ah = round((usable_battery_kwh * 1000) / 12, 0)
            num_150ah_batteries = math.ceil(battery_capacity_ah / 150)
            
            # Store results
            st.session_state.update({
                'monthly_energy_used': monthly_units_input,
                'required_kw': required_kw,
                'area_needed': area_needed,
                'cost_estimate': cost_estimate,
                'monthly_grid_cost': monthly_grid_cost,
                'payback_years': payback_years,
                'usable_battery_kwh': usable_battery_kwh,
                'num_150ah_batteries': num_150ah_batteries,
                'daily_energy_kwh': daily_energy_kwh,
                'unit_rate': unit_rate,
                'calculation_done': True,
                'estimation_done': True,
                'step': st.session_state.step +1
            })
            st.rerun()

# ---------------- MODE 1 RESULTS ------------------
elif st.session_state.step == 2 and st.session_state.mode == "Monthly Units Estimator":
    # ===== ADD THIS VERIFICATION BLOCK RIGHT HERE =====
    if not st.session_state.get('calculation_done', False):
        st.error("❌ Please complete the estimation on the previous page")
        if st.button("← Back to Estimation"):
            st.session_state.step = 1  # Go back to calculation page
            st.rerun()
        st.stop()  # This prevents the rest of the results page from showing
    
    # ===== YOUR EXISTING RESULTS CODE STARTS HERE =====
    st.subheader("Step 3: Your Estimation Results")

    if st.session_state.get('calculation_done'):
        # Display results
        st.success(f"📅 Monthly Energy Used: {st.session_state.monthly_energy_used} kWh")
        st.write(f"⚡ Suggested Solar Panel Size: {st.session_state.required_kw} kW")
        st.write(f"🌍 Area Needed: {st.session_state.area_needed} sq. meters")
        st.write(f"💸 Estimated Solar Cost: ₹{st.session_state.cost_estimate}")

        st.markdown("---")
        st.write("Battery Backup Suggestion")
        st.write(f"🔌 Daily backup energy needed: {st.session_state.daily_energy_kwh} kWh")
        st.write(f"📂 Usable battery capacity required (80% DoD): {st.session_state.usable_battery_kwh} kWh")
        st.write(f"🔋 Suggested Battery: {st.session_state.num_150ah_batteries} x 150Ah (12V)")

        st.metric("Monthly Grid Bill", f"₹{st.session_state.monthly_grid_cost}")
        st.metric("💰 Monthly Savings", f"₹{st.session_state.monthly_grid_cost}")
        st.metric("⏳ Payback Period", f"{st.session_state.payback_years} years")

        # Report generation
        report_txt = f"""Smart Solar System Estimation Report
-----------------------------------
Location: {st.session_state.selected_city}
Sun Hours: {st.session_state.sun_hours} hours/day

Monthly Bill: ₹ {st.session_state.monthly_grid_cost}
Electricity Rate: ₹ {st.session_state.unit_rate}/unit
Estimated Annual Units: {st.session_state.monthly_energy_used * 12:.1f} kWh
Suggested Solar Size: {st.session_state.required_kw} kW
Area Needed: {st.session_state.area_needed} sq. meters
Estimated Cost: ₹ {st.session_state.cost_estimate}

Monthly Savings: ₹ {st.session_state.monthly_grid_cost}
Payback Period: {st.session_state.payback_years} years
"""

        # CSV Report
        df = pd.DataFrame({
            "Location": [st.session_state.selected_city],
            "Sun Hours": [st.session_state.sun_hours],
            "Monthly Bill (₹)": [st.session_state.monthly_grid_cost],
            "Rate (₹/unit)": [st.session_state.unit_rate],
            "Yearly Units": [st.session_state.monthly_energy_used * 12],
            "Suggested kW": [st.session_state.required_kw],
            "Area (sqm)": [st.session_state.area_needed],
            "Cost (₹)": [st.session_state.cost_estimate],
            "Savings (₹/month)": [st.session_state.monthly_grid_cost],
            "Payback (yrs)": [st.session_state.payback_years]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Download TXT Report",
                data=report_txt.encode('utf-8'),
                file_name="solar_estimate_bill.txt"
            )
        with col2:
            st.download_button(
                "📊 Download CSV Report",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="solar_estimate_bill.csv",
                mime='text/csv'
            )

        st.button("⬅ Back", on_click=prev_step, key="monthly_results_back")
        if st.button("🚀 Connect with Installer", key="go_to_installer_monthly"):
            st.session_state.step = 3
            st.rerun()
    else:
        st.warning("❌ Please complete the estimation first")
        if st.button("⬅ Back to Form"):
            prev_step()

# ---------------- MODE 2 ------------------
elif st.session_state.step == 1 and st.session_state.mode == "Appliance-Based Estimator":
    st.subheader("Step 2: Appliance-Based Estimation")

    with st.expander("Choose Home Type & Presets"):
        st.session_state.preset = st.selectbox("Select Household Type:", [
            "Custom (Manual Entry)", "Basic Rural Home",
            "Urban Middle-Class Flat", "Modern Urban Villa"
        ], key="preset_type")

        # Default appliance settings
        values = {
            'fan_count': 0, 'fan_hours': 0, 'bulb_count': 0, 'bulb_hours': 0,
            'tv': False, 'tv_hours': 0, 'fridge': False, 'router': False,
            'mobile_count': 0, 'mobile_hours': 0, 'laptop_count': 0, 'laptop_hours': 0,
            'ac': False, 'ac_hours': 0, 'washing': False, 'washing_hours': 0,
            'ro': False, 'ro_hours': 0, 'oven': False, 'oven_hours': 0
        }

        # Presets update
        if st.session_state.preset == "Basic Rural Home":
            values.update({
                'fan_count': 2, 'fan_hours': 6, 'bulb_count': 4, 'bulb_hours': 6,
                'tv': True, 'tv_hours': 3, 'fridge': True, 'router': True,
                'mobile_count': 2, 'mobile_hours': 2
            })
        elif st.session_state.preset == "Urban Middle-Class Flat":
            values.update({
                'fan_count': 3, 'fan_hours': 6, 'bulb_count': 6, 'bulb_hours': 5,
                'tv': True, 'tv_hours': 3, 'fridge': True, 'router': True,
                'mobile_count': 3, 'mobile_hours': 2, 'laptop_count': 1, 'laptop_hours': 5,
                'washing': True, 'washing_hours': 0.5, 'ro': True, 'ro_hours': 2,
                'oven': True, 'oven_hours': 15
            })
        elif st.session_state.preset == "Modern Urban Villa":
            values.update({
                'fan_count': 4, 'fan_hours': 6, 'bulb_count': 10, 'bulb_hours': 5,
                'tv': True, 'tv_hours': 3, 'fridge': True, 'router': True,
                'mobile_count': 4, 'mobile_hours': 2, 'laptop_count': 2, 'laptop_hours': 4,
                'ac': True, 'ac_hours': 5, 'washing': True, 'washing_hours': 1,
                'ro': True, 'ro_hours': 2, 'oven': True, 'oven_hours': 30
            })

    with st.expander("Appliance Selection"):
        fan_count = st.number_input("Ceiling Fans (75W): Count", 0, 10, values['fan_count'], key="fan_count")
        fan_hours = st.number_input("Hours/day for Fans", 0.0, 24.0, float(values['fan_hours']), key="fan_hours")
        bulb_count = st.number_input("LED Bulbs (9W): Count", 0, 20, values['bulb_count'], key="bulb_count")
        bulb_hours = st.number_input("Hours/day for Bulbs", 0.0, 24.0, float(values['bulb_hours']), key="bulb_hours")
        fridge = st.checkbox("Refrigerator (150W, 24x7)", value=values['fridge'], key="fridge")
        router = st.checkbox("Wi-Fi Router (10W, 24x7)", value=values['router'], key="router")
        tv = st.checkbox("TV (100W)", value=values['tv'], key="tv")
        tv_hours = st.number_input("Hours/day for TV", 0.0, 24.0, float(values['tv_hours']), key="tv_hours") if tv else 0
        mobile_count = st.number_input("Mobile Chargers (10W): Count", 0, 10, values['mobile_count'], key="mobile_count")
        mobile_hours = st.number_input("Hours/day for Mobile Charging", 0.0, 24.0, float(values['mobile_hours']), key="mobile_hours") if mobile_count > 0 else 0
        laptop_count = st.number_input("Laptops (60W): Count", 0, 5, values['laptop_count'], key="laptop_count")
        laptop_hours = st.number_input("Hours/day for Laptops", 0.0, 24.0, float(values['laptop_hours']), key="laptop_hours") if laptop_count > 0 else 0
        ac = st.checkbox("Air Conditioner (1500W)", value=values['ac'], key="ac")
        ac_hours = st.number_input("Hours/day for AC", 0.0, 24.0, float(values['ac_hours']), key="ac_hours") if ac else 0
        washing = st.checkbox("Washing Machine (500W)", value=values['washing'], key="washing")
        washing_hours = st.number_input("Hours/day for Washing Machine", 0.0, 4.0, float(values['washing_hours']), key="washing_hours") if washing else 0
        ro = st.checkbox("Water Purifier (RO - 50W)", value=values['ro'], key="ro")
        ro_hours = st.number_input("Hours/day for RO", 0.0, 24.0, float(values['ro_hours']), key="ro_hours") if ro else 0
        oven = st.checkbox("Microwave/Oven (1200W)", value=values['oven'], key="oven")
        oven_hours = st.number_input("Minutes/day for Oven", 0.0, 60.0, float(values['oven_hours']), key="oven_hours") if oven else 0

        user_unit_rate = st.number_input("Your grid electricity rate (Rs/unit):", min_value=1.0, value=8.0, key="appl_unit_rate")
        area_avail = st.number_input("Available installation area (sq. meters):", min_value=1, key="appl_area")

        st.session_state.appliance_inputs = {
            "preset": st.session_state.preset, 
            "fan_count": fan_count, 
            "fan_hours": fan_hours,
            "bulb_count": bulb_count, 
            "bulb_hours": bulb_hours, 
            "tv": tv, 
            "tv_hours": tv_hours,
            "fridge": fridge, 
            "router": router, 
            "mobile_count": mobile_count, 
            "mobile_hours": mobile_hours,
            "laptop_count": laptop_count, 
            "laptop_hours": laptop_hours, 
            "ac": ac, 
            "ac_hours": ac_hours,
            "washing": washing, 
            "washing_hours": washing_hours, 
            "ro": ro, 
            "ro_hours": ro_hours,
            "oven": oven, 
            "oven_hours": oven_hours, 
            "user_unit_rate": user_unit_rate,
            "area_avail": area_avail
        }

    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅ Back", on_click=prev_step, key="appl_back")
    with col2:
        if st.button("Next ➡", key="appl_next"):
            # Perform calculations
            inputs = st.session_state.appliance_inputs
            cost_per_kw = 50000
            area_per_kw = 10

            daily_energy_wh = (
                inputs["fan_count"] * 75 * inputs["fan_hours"] +
                inputs["bulb_count"] * 9 * inputs["bulb_hours"] +
                (150 * 24 if inputs["fridge"] else 0) +
                (10 * 24 if inputs["router"] else 0) +
                (100 * inputs["tv_hours"] if inputs["tv"] else 0) +
                inputs["mobile_count"] * 10 * inputs["mobile_hours"] +
                inputs["laptop_count"] * 60 * inputs["laptop_hours"] +
                (1500 * inputs["ac_hours"] if inputs["ac"] else 0) +
                (500 * inputs["washing_hours"] if inputs["washing"] else 0) +
                (50 * inputs["ro_hours"] if inputs["ro"] else 0) +
                (1200 * inputs["oven_hours"] / 60 if inputs["oven"] else 0)
            )

            daily_energy_kwh = daily_energy_wh / 1000
            monthly_energy_kwh = round(daily_energy_kwh * 30, 2)
            required_kw = round(monthly_energy_kwh / (st.session_state.sun_hours * 30), 2)
            area_needed = round(required_kw * area_per_kw, 2)
            cost_estimate = round(required_kw * cost_per_kw)
            monthly_grid_cost = round(monthly_energy_kwh * inputs["user_unit_rate"])
            payback_years = round(cost_estimate / (monthly_grid_cost * 12), 1)
            usable_battery_kwh = round(daily_energy_kwh / 0.8, 2)
            battery_capacity_ah = round((usable_battery_kwh * 1000) / 12, 0)
            num_150ah_batteries = math.ceil(battery_capacity_ah / 150)

            # Store results
            st.session_state.update({
                'monthly_energy_kwh': monthly_energy_kwh,
                'required_kw': required_kw,
                'area_needed': area_needed,
                'cost_estimate': cost_estimate,
                'monthly_grid_cost': monthly_grid_cost,
                'payback_years': payback_years,
                'usable_battery_kwh': usable_battery_kwh,
                'num_150ah_batteries': num_150ah_batteries,
                'daily_energy_kwh': daily_energy_kwh,
                'user_unit_rate': inputs["user_unit_rate"],
                'calculation_done': True,
                'estimation_done': True,
                'step': st.session_state.step + 1
            })
            st.rerun()

# ---------------- MODE 2 RESULTS ------------------
elif st.session_state.step == 2 and st.session_state.mode == "Appliance-Based Estimator":
    # ===== ADD THE SAME VERIFICATION BLOCK HERE =====
    if not st.session_state.get('calculation_done', False):
        st.error("❌ Please complete the estimation on the previous page")
        if st.button("← Back to Estimation"):
            st.session_state.step = 1
            st.rerun()
        st.stop()
    
    # ===== THEN CONTINUE WITH YOUR EXISTING CODE =====
    st.subheader("Step 3: Appliance-Based Estimation Result")

    if st.session_state.get('calculation_done'):
        # Display results
        st.success(f"📅 Monthly Energy Required: {st.session_state.monthly_energy_kwh} kWh")
        st.write(f"⚡ Suggested Solar Panel Size: {st.session_state.required_kw} kW")
        st.write(f"🌍 Area Needed: {st.session_state.area_needed} sq. meters")
        st.write(f"💸 Estimated Solar Cost: ₹{st.session_state.cost_estimate}")

        st.markdown("---")
        st.write("Battery Backup Suggestion")
        st.write(f"🔌 Daily backup energy needed: {st.session_state.daily_energy_kwh:.2f} kWh")
        st.write(f"📂 Usable battery capacity required (80% DoD): {st.session_state.usable_battery_kwh} kWh")
        st.write(f"🔋 Suggested Battery: {st.session_state.num_150ah_batteries} x 150Ah (12V)")

        st.metric("Monthly Grid Bill", f"₹{st.session_state.monthly_grid_cost}")
        st.metric("💰 Monthly Savings", f"₹{st.session_state.monthly_grid_cost}")
        st.metric("⏳ Payback Period", f"{st.session_state.payback_years} years")

        # Report generation
        report_txt = f"""Smart Solar System Estimation Report
-----------------------------------
Location: {st.session_state.selected_city}
Sun Hours: {st.session_state.sun_hours} hours/day
Household Type: {st.session_state.preset}

Appliance-Based Energy Use:
- Estimated Monthly Usage: {st.session_state.monthly_energy_kwh} kWh
- Required Solar Size: {st.session_state.required_kw} kW
- Required Area: {st.session_state.area_needed} sq. meters
- Estimated Solar Cost: ₹{st.session_state.cost_estimate}

Battery Backup Suggestion:
- Daily Usage: {st.session_state.daily_energy_kwh:.2f} kWh
- Usable Battery Required: {st.session_state.usable_battery_kwh:.2f} kWh
- Suggested Batteries: {st.session_state.num_150ah_batteries} x 150Ah (12V)

Financials:
- Monthly Grid Cost: ₹{st.session_state.monthly_grid_cost}
- Monthly Savings: ₹{st.session_state.monthly_grid_cost}
- Payback Period: {st.session_state.payback_years} years
"""

        # CSV Report
        df = pd.DataFrame({
            "Location": [st.session_state.selected_city],
            "Sun Hours": [st.session_state.sun_hours],
            "Preset": [st.session_state.preset],
            "Monthly Usage (kWh)": [st.session_state.monthly_energy_kwh],
            "Required kW": [st.session_state.required_kw],
            "Required Area (sqm)": [st.session_state.area_needed],
            "Solar Cost (₹)": [st.session_state.cost_estimate],
            "Battery Daily kWh": [st.session_state.daily_energy_kwh],
            "Usable Battery (kWh)": [st.session_state.usable_battery_kwh],
            "150Ah Batteries": [st.session_state.num_150ah_batteries],
            "Monthly Grid Bill (₹)": [st.session_state.monthly_grid_cost],
            "Payback (yrs)": [st.session_state.payback_years]
        })

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📄 Download TXT Report",
                data=report_txt.encode('utf-8'),
                file_name="solar_estimate_appliance.txt"
            )
        with col2:
            st.download_button(
                "📊 Download CSV Report",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="solar_estimate_appliance.csv",
                mime='text/csv'
            )

        st.button("⬅ Back", on_click=prev_step, key="appl_result_back")
        if st.button("🚀 Connect with Installer", key="appl_go_to_installer"):
            st.session_state.step = 3
            st.rerun()
    else:
        st.warning("❌ Please complete the estimation first")
        if st.button("⬅ Back to Form"):
            prev_step()

# ---------------- INSTALLER CONNECTION ------------------
elif st.session_state.step == 3:
    st.subheader("Step 4: Connect with a Trusted Solar Installer 🔧")
    st.markdown("Browse verified local installers and submit your details to get a quote.")

    installers = [
        {"name": "SolarTech Pvt Ltd", "rate": 52000, "warranty": "10 Years", "rating": 4.6},
        {"name": "SunPro Installers", "rate": 55000, "warranty": "12 Years", "rating": 4.8},
        {"name": "BrightFuture Solar", "rate": 50000, "warranty": "8 Years", "rating": 4.5}
    ]

    # Display installers
    for idx, installer in enumerate(installers):
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""
                **{installer['name']}**  
                💰 ₹{installer['rate']}/kW  
                🛡 Warranty: {installer['warranty']}  
                ⭐ Rating: {installer['rating']} / 5
                """)
            with col2:
                if st.button("📩 Get Quote", key=f"quote_{idx}"):
                    st.session_state.selected_installer = installer["name"]
                    st.session_state.show_contact_form = True
                    st.rerun()

    # Show contact form if installer selected
    if st.session_state.get('show_contact_form') and st.session_state.selected_installer:
        with st.form(key="installer_contact_form"):
            st.markdown(f"### Contact {st.session_state.selected_installer}")
            
            name = st.text_input("👤 Full Name*")
            phone = st.text_input("📞 Phone Number*")
            email = st.text_input("📧 Email Address*")
            location = st.text_input("📍 Your Location", value=st.session_state.get("selected_city", ""))
            
            st.markdown("**System Details:**")
            est_kw = st.session_state.get('required_kw', 0)
            usage_kwh = st.session_state.get('monthly_energy_used', st.session_state.get('monthly_energy_kwh', 0))
            
            st.markdown(f"- Estimated System Size: {est_kw} kW")
            st.markdown(f"- Estimated Monthly Usage: {usage_kwh} kWh")
            submitted = st.form_submit_button("✅ Submit Request")
            if submitted:
                errors = []

                if not name.strip():
                   errors.append("❗ Full Name is required.")
                if not phone.isdigit() or len(phone) != 10:
                   errors.append("❗ Phone Number must be 10 digits.")
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                   errors.append("❗ Enter a valid Email Address.")

                if errors:
                  for err in errors:
                    st.error(err)
                st.warning("🚫 Please correct the errors before submitting.")
                else:
                    st.success(f"✅ Your request to {st.session_state.selected_installer} has been submitted!")
                    st.session_state.show_contact_form = False
                    st.session_state.selected_installer = None
                    st.rerun()

    # Navigation buttons
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button("⬅ Back to Results", on_click=lambda: st.session_state.update(step=2), key="installer_back")
    with col2:
        st.button("🏁 Finish", on_click=lambda: st.session_state.update(step=0, mode=None, start=False), key="finish_button")

# Footer
st.markdown("---")
st.caption("Smart Solar Estimator | by Ronit Bhati")
