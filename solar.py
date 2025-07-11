import streamlit as st
import math
import re
import pandas as pd

# Initialize session state
if 'start' not in st.session_state:
    st.session_state.start = False
if 'estimation_done' not in st.session_state:
    st.session_state.estimation_done = False
if 'selected_installer' not in st.session_state:
    st.session_state.selected_installer = None

# Intro screen
if not st.session_state.start:
    st.title("Smart Solar System Estimator")
    st.subheader("Make smarter solar decisions in minutes ⚡")
    st.write("""
        Welcome to the app❤️..
        Estimate your solar needs instantly & connect with installers.
    """)
    st.write("You'll also get a suggestion for battery backup and savings comparison. 💰")
    if st.button("🚀 Get Started"):
        st.session_state.start = True
    st.stop()

# Set page config
st.set_page_config(page_title="Smart Solar Advisor", page_icon="🌞")
st.title("📊Smart Solar System Estimator")

# City sun hours
city_sun_hours = {
    "Delhi": 5.5, "Mumbai": 4.5, "Chennai": 5.3,
    "Bangalore": 5.2, "Hyderabad": 5.4, "Ahmedabad": 5.6,
    "Kolkata": 4.8, "Jaipur": 5.7, "Lucknow": 5.2,
    "Custom (Enter manually)": None
}
selected_city = st.selectbox("📍 Select Your City/Location:", list(city_sun_hours.keys()))
sun_hours = st.number_input("🌞 Enter average sun hours per day:", min_value=1.0, max_value=7.0, value=5.0) if selected_city == "Custom (Enter manually)" else city_sun_hours[selected_city]
solar_output_per_kw = round(sun_hours * 365, 1)

area_per_kw = 10
cost_per_kw = 55000

# Mode switcher
mode = st.radio("Choose Estimation Mode:", ["Monthly Units Estimator", "Appliance-Based Estimator"])
if st.session_state.get("prev_mode") != mode:
    st.session_state.estimation_done = False
    st.session_state.selected_installer = None
    st.session_state.prev_mode = mode

# ---------------- MODE 1 ------------------
if mode == "Monthly Units Estimator":
    st.expander("📈 Monthly Units Estimator", expanded=True)
    monthly_units_input = st.number_input("Enter your average monthly electricity usage (in units/kWh):", min_value=0.0, value=300.0)
    unit_rate = st.number_input("Your grid electricity rate (₹/unit):", min_value=1.0, value=8.0)
    area_avail = st.number_input("Available installation area (sq. meters):", min_value=1)

    if st.button("Estimate"):
        daily_energy_kwh = round(monthly_units_input / 30, 2)
        required_kw = round(monthly_units_input / (solar_output_per_kw / 12), 2)
        area_needed = round(required_kw * area_per_kw, 2)
        cost_estimate = round(required_kw * cost_per_kw)
        monthly_grid_cost = round(monthly_units_input * unit_rate)
        payback_years = round(cost_estimate / (monthly_grid_cost * 12), 1)
        usable_battery_kwh = round(daily_energy_kwh / 0.8, 2)
        battery_capacity_ah = round((usable_battery_kwh * 1000) / 12, 0)
        num_150ah_batteries = math.ceil(battery_capacity_ah / 150)

        # Assign report variables
        monthly_bill = monthly_grid_cost
        system_kw = required_kw
        yearly_units = monthly_units_input * 12
        total_cost = cost_estimate
        monthly_savings = monthly_grid_cost

        st.success(f"📅 Monthly Energy Used: *{monthly_units_input} kWh*")
        st.write(f"⚡ Suggested Solar Panel Size: *{required_kw} kW*")
        st.write(f"🌍 Area Needed: *{area_needed} sq. meters*")
        st.write(f"💸 Estimated Solar Cost: *₹{cost_estimate}*")

        st.markdown("---")
        st.write("Battery Backup Suggestion")
        st.write(f"🔌 Daily backup energy needed: *{daily_energy_kwh} kWh*")
        st.write(f"📂 Usable battery capacity required (80% DoD): *{usable_battery_kwh} kWh*")
        st.write(f"🔋 Suggested Battery: *{num_150ah_batteries} x 150Ah (12V)*")

        st.markdown("---")
        st.metric("Monthly Grid Bill", f"₹{monthly_grid_cost}")
        st.metric("💰 Monthly Savings", f"₹{monthly_grid_cost}")
        st.metric("⏳ Payback Period", f"{payback_years} years")

        st.session_state.estimation_done = True
        st.session_state['required_kw'] = required_kw
        st.session_state['monthly_energy_used'] = monthly_units_input

        report_txt = f"""
Smart Solar System Estimation Report
-----------------------------------
📍 Location: {selected_city}
☀ Sun Hours: {sun_hours} hours/day

📊 Bill-Based Estimation:
- Monthly Bill: ₹ {monthly_bill}
- Electricity Rate: ₹ {unit_rate}/unit
- Estimated Annual Units: {yearly_units:.1f} kWh
- Suggested Solar Size: {system_kw} kW
- Area Needed: {area_needed} sq. meters
- Estimated Cost: ₹ {total_cost}

💰 Financials:
- Monthly Savings: ₹ {monthly_savings}
- Payback Period: {payback_years} years
"""
        st.download_button("📄 Download TXT Report", data=report_txt, file_name="solar_estimate_bill.txt")

        df = pd.DataFrame({
            "Location": [selected_city],
            "Sun Hours": [sun_hours],
            "Monthly Bill (₹)": [monthly_bill],
            "Rate (₹/unit)": [unit_rate],
            "Yearly Units": [yearly_units],
            "Suggested kW": [system_kw],
            "Area (sqm)": [area_needed],
            "Cost (₹)": [total_cost],
            "Savings (₹/month)": [monthly_savings],
            "Payback (yrs)": [payback_years]
        })
        st.download_button("📊 Download CSV Report", data=df.to_csv(index=False).encode('utf-8'), file_name="solar_estimate_bill.csv", mime='text/csv')

# ---------------- MODE 2 ------------------
elif mode == "Appliance-Based Estimator":
    st.header("Appliance-Based Estimator")
    with st.expander("Choose Home Type & Presets"):
        preset = st.selectbox("Select Household Type:", [
            "Custom (Manual Entry)", "Basic Rural Home",
            "Urban Middle-Class Flat", "Modern Urban Villa"
        ])

        values = {'fan_count': 0, 'fan_hours': 0, 'bulb_count': 0, 'bulb_hours': 0,
                  'tv': False, 'tv_hours': 0, 'fridge': False, 'router': False,
                  'mobile_count': 0, 'mobile_hours': 0, 'laptop_count': 0, 'laptop_hours': 0,
                  'ac': False, 'ac_hours': 0, 'washing': False, 'washing_hours': 0,
                  'ro': False, 'ro_hours': 0, 'oven': False, 'oven_hours': 0}

        # Preset logic
        if preset == "Basic Rural Home":
            values.update(dict(fan_count=2, fan_hours=6, bulb_count=4, bulb_hours=6, tv=True, tv_hours=3,
                               fridge=True, router=True, mobile_count=2, mobile_hours=2))
        elif preset == "Urban Middle-Class Flat":
            values.update(dict(fan_count=3, fan_hours=6, bulb_count=6, bulb_hours=5, tv=True, tv_hours=3,
                               fridge=True, router=True, mobile_count=3, mobile_hours=2, laptop_count=1,
                               laptop_hours=5, washing=True, washing_hours=0.5, ro=True, ro_hours=2, oven=True, oven_hours=15))
        elif preset == "Modern Urban Villa":
            values.update(dict(fan_count=4, fan_hours=6, bulb_count=10, bulb_hours=5, tv=True, tv_hours=3,
                               fridge=True, router=True, mobile_count=4, mobile_hours=2, laptop_count=2,
                               laptop_hours=4, ac=True, ac_hours=5, washing=True, washing_hours=1,
                               ro=True, ro_hours=2, oven=True, oven_hours=30))

    with st.expander("Appliance Selection"):
        fan_count = st.number_input("Ceiling Fans (75W): Count", 0, 10, values['fan_count'])
        fan_hours = st.number_input("Hours/day for Fans", 0.0, 24.0, float(values['fan_hours']))
        bulb_count = st.number_input("LED Bulbs (9W): Count", 0, 20, values['bulb_count'])
        bulb_hours = st.number_input("Hours/day for Bulbs", 0.0, 24.0, float(values['bulb_hours']))
        fridge = st.checkbox("Refrigerator (150W, 24x7)", value=values['fridge'])
        router = st.checkbox("Wi-Fi Router (10W, 24x7)", value=values['router'])
        tv = st.checkbox("TV (100W)", value=values['tv'])
        tv_hours = st.number_input("Hours/day for TV", 0.0, 24.0, float(values['tv_hours'])) if tv else 0
        mobile_count = st.number_input("Mobile Chargers (10W): Count", 0, 10, values['mobile_count'])
        mobile_hours = st.number_input("Hours/day for Mobile Charging", 0.0, 24.0, float(values['mobile_hours'])) if mobile_count > 0 else 0
        laptop_count = st.number_input("Laptops (60W): Count", 0, 5, values['laptop_count'])
        laptop_hours = st.number_input("Hours/day for Laptops", 0.0, 24.0, float(values['laptop_hours'])) if laptop_count > 0 else 0
        ac = st.checkbox("Air Conditioner (1500W)", value=values['ac'])
        ac_hours = st.number_input("Hours/day for AC", 0.0, 24.0, float(values['ac_hours'])) if ac else 0
        washing = st.checkbox("Washing Machine (500W)", value=values['washing'])
        washing_hours = st.number_input("Hours/day for Washing Machine", 0.0, 4.0, float(values['washing_hours'])) if washing else 0
        ro = st.checkbox("Water Purifier (RO - 50W)", value=values['ro'])
        ro_hours = st.number_input("Hours/day for RO", 0.0, 24.0, float(values['ro_hours'])) if ro else 0
        oven = st.checkbox("Microwave/Oven (1200W)", value=values['oven'])
        oven_hours = st.number_input("Minutes/day for Oven", 0.0, 60.0, float(values['oven_hours'])) if oven else 0
        user_unit_rate = st.number_input("Your grid electricity rate (Rs/unit):", min_value=1.0, value=8.0)
        area_avail = st.number_input("Available installation area (sq. meters):", min_value=1)

    if st.button("Estimate Based on Appliances"):
        daily_energy_wh = (
            fan_count * 75 * fan_hours + bulb_count * 9 * bulb_hours +
            (150 * 24 if fridge else 0) + (10 * 24 if router else 0) +
            (100 * tv_hours if tv else 0) + mobile_count * 10 * mobile_hours +
            laptop_count * 60 * laptop_hours + (1500 * ac_hours if ac else 0) +
            (500 * washing_hours if washing else 0) + (50 * ro_hours if ro else 0) +
            (1200 * oven_hours / 60 if oven else 0)
        )
        daily_energy_kwh = daily_energy_wh / 1000
        monthly_energy_kwh = round(daily_energy_kwh * 30, 2)
        required_kw = round(monthly_energy_kwh / (solar_output_per_kw / 12), 2)
        area_needed = round(required_kw * area_per_kw, 2)
        cost_estimate = round(required_kw * cost_per_kw)
        monthly_grid_cost = round(monthly_energy_kwh * user_unit_rate)
        payback_years = round(cost_estimate / (monthly_grid_cost * 12), 1)
        usable_battery_kwh = round(daily_energy_kwh / 0.8, 2)
        battery_capacity_ah = round((usable_battery_kwh * 1000) / 12, 0)
        num_150ah_batteries = math.ceil(battery_capacity_ah / 150)

        st.success(f"Monthly Energy Required: *{monthly_energy_kwh} units (kWh)*")
        st.write(f"Suggested Solar Panel Size: *{required_kw} kW*")
        st.write(f"Area Needed: *{area_needed} sq. meters*")
        st.write(f"Estimated Solar Cost: *Rs {cost_estimate}*")

        st.markdown("---")
        st.write("Battery Backup Suggestion")
        st.write(f"Daily backup energy needed: *{daily_energy_kwh} kWh*")
        st.write(f"Usable battery capacity required (80% DoD): *{usable_battery_kwh} kWh*")
        st.write(f"Suggested Battery: *{num_150ah_batteries} x 150Ah (12V)*")

        st.metric("Monthly Grid Bill", f"Rs {monthly_grid_cost}")
        st.metric("Monthly Savings", f"Rs {monthly_grid_cost}")
        st.metric("Payback Period", f"{payback_years} years")

        st.session_state['required_kw'] = required_kw
        st.session_state['appliance_energy_used'] = monthly_energy_kwh
        st.session_state.estimation_done = True

        report_txt = f"""
Smart Solar System Estimation Report
-----------------------------------
📍 Location: {selected_city}
☀ Sun Hours: {sun_hours} hours/day
🏠 Household Type: {preset}

📊 Appliance-Based Energy Use:
- Estimated Monthly Usage: {monthly_energy_kwh} kWh
- Required Solar Size: {required_kw} kW
- Required Area: {area_needed} sq. meters
- Estimated Solar Cost: ₹ {cost_estimate}

🔋 Battery Backup Suggestion:
- Daily Usage: {daily_energy_kwh:.2f} kWh
- Usable Battery Required: {usable_battery_kwh:.2f} kWh
- Suggested Batteries: {num_150ah_batteries} x 150Ah (12V)

💰 Financials:
- Monthly Grid Cost: ₹ {monthly_grid_cost}
- Monthly Savings: ₹ {monthly_grid_cost}
- Payback Period: {payback_years} years
"""
        st.download_button("📄 Download TXT Report", data=report_txt, file_name="solar_estimate.txt")

        df = pd.DataFrame({
            "Location": [selected_city],
            "Sun Hours": [sun_hours],
            "Preset": [preset],
            "Monthly Usage (kWh)": [monthly_energy_kwh],
            "Required kW": [required_kw],
            "Required Area (sqm)": [area_needed],
            "Solar Cost (₹)": [cost_estimate],
            "Battery Daily kWh": [daily_energy_kwh],
            "Usable Battery (kWh)": [usable_battery_kwh],
            "150Ah Batteries": [num_150ah_batteries],
            "Monthly Grid Bill (₹)": [monthly_grid_cost],
            "Payback (yrs)": [payback_years]
        })
        st.download_button("📊 Download CSV Report", data=df.to_csv(index=False).encode('utf-8'), file_name="solar_estimate.csv", mime='text/csv')

# ---------------- INSTALLERS ------------------
installers = [
    {"name": "SolarTech Pvt Ltd", "rate": 52000, "warranty": "10 Years", "rating": 4.6},
    {"name": "SunPro Installers", "rate": 55000, "warranty": "12 Years", "rating": 4.8},
    {"name": "BrightFuture Solar", "rate": 50000, "warranty": "8 Years", "rating": 4.5}
]

st.markdown("---")
st.subheader("🔧 Recommended Solar Installers")
selected_installer = st.session_state.get("selected_installer")

for idx, installer in enumerate(installers):
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"""
            ### {installer['name']}
            💰 ₹{installer['rate']}/kW  
            🛡 {installer['warranty']}  
            ⭐ {installer['rating']} / 5
        """)
    with col2:
        if st.button("📩 Get Quote", key=f"quote_{idx}"):
            st.session_state.selected_installer = installer["name"]
            selected_installer = installer["name"]

if selected_installer and st.session_state.estimation_done:
    with st.expander(f"📩 Fill your details to get a quote from {selected_installer}"):
        name = st.text_input("👤 Full Name")
        phone = st.text_input("📞 Phone Number")
        email = st.text_input("📧 Email Address")
        location = st.text_input("📍 Your Location (City or Area)", selected_city)
        est_kw = st.session_state.get("required_kw", 0)
        usage_kwh = st.session_state.get("monthly_energy_used", st.session_state.get("appliance_energy_used", 0))

        st.markdown(f"📦 *Estimated System Size:* {est_kw} kW")
        st.markdown(f"⚡ *Estimated Monthly Usage:* {usage_kwh} kWh")

        if st.button("Submit Lead"):
            if not name or not phone or not email:
                st.error("❌ Please fill in all required fields.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.warning("⚠ Please enter a valid email address.")
            else:
                with st.spinner("Submitting your details..."):
                    st.success("✅ Your request has been submitted! We'll connect you with the installer shortly.")
                    st.session_state.selected_installer = None

# Footer
st.markdown("---")
st.caption("Smart Solar Estimator | by Ronit Bhati")

