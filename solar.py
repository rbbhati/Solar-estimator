import streamlit as st
import math

# Initialize session state variables
if 'start' not in st.session_state:
    st.session_state.start = False
if 'estimation_done' not in st.session_state:
    st.session_state.estimation_done = False
if 'selected_installer' not in st.session_state:
    st.session_state.selected_installer = None

# INTRO SCREEN
if not st.session_state.start:
    st.title(" Smart Solar System Estimator")
    st.subheader("Make smarter solar decisions in minutes ⚡")
    st.write("""
        Welcome to the app❤️..
        Estimate your solar needs instantly & connect with installers.
    """)
    st.write("You'll also get a suggestion for battery backup and savings comparison. 💰")

    if st.button("🚀 Get Started"):
        st.session_state.start = True
    st.stop()

# MAIN INTERFACE
st.set_page_config(page_title="Smart Solar Advisor", page_icon="🌞")
st.title("📊Smart Solar System Estimator")

# Sun hours by city
city_sun_hours = {
    "Delhi": 5.5, "Mumbai": 4.5, "Chennai": 5.3,
    "Bangalore": 5.2, "Hyderabad": 5.4, "Ahmedabad": 5.6,
    "Kolkata": 4.8, "Jaipur": 5.7, "Lucknow": 5.2,
    "Custom (Enter manually)": None
}

selected_city = st.selectbox("📍 Select Your City/Location:", list(city_sun_hours.keys()))
sun_hours = st.number_input("🌞 Enter average sun hours per day:", min_value=1.0, max_value=7.0, value=5.0) if selected_city == "Custom (Enter manually)" else city_sun_hours[selected_city]
solar_output_per_kw = round(sun_hours * 365, 1)
st.caption("ℹ️ These values are annual averages. Sunlight hours may vary seasonally.")

# Constants
area_per_kw = 10
cost_per_kw = 55000

# MODE SELECTOR
mode = st.radio("Choose Estimation Mode:", ["Monthly Units Estimator", "Appliance-Based Estimator"])
prev_mode = st.session_state.get("prev_mode")
if prev_mode != mode:
    st.session_state.estimation_done = False
    st.session_state.selected_installer = None
    st.session_state.prev_mode = mode

# -------------------- MODE 1 --------------------
if mode == "Monthly Units Estimator":
    st.expander("📈 Monthly Units Estimator")
    monthly_units_input = st.number_input("Enter your average monthly electricity usage (in units/kWh):", min_value=0.0, value=300.0)
    energy_Kwh = monthly_units_input
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
        st.session_state['monthly_energy_used'] = energy_Kwh
        report = f"""
Smart Solar System Estimation Report (Monthly Units Mode)

📍 Location: {selected_city}
☀️ Sun Hours: {sun_hours}
📅 Monthly Energy Used: {monthly_units_input} kWh
🔋 Required Solar Size: {required_kw} kW
🏠 Area Needed: {area_needed} sq. meters
💸 Estimated System Cost: ₹{cost_estimate}
🔋 Battery: {num_150ah_batteries} x 150Ah (12V)
📂 Usable Battery Capacity (80% DoD): {usable_battery_kwh} kWh
📈 Monthly Grid Bill: ₹{monthly_grid_cost}
💰 Monthly Savings: ₹{monthly_grid_cost}
⏳ Payback Period: {payback_years} years
"""
        st.download_button("📥 Download Full Report", data=report, file_name="solar_estimate_monthly.txt")
        


# -------------------- MODE 2 --------------------
elif mode == "Appliance-Based Estimator":
  st.header("Appliance-Based Estimator")
  with st.expander("Choose Home Type & Presets"):
    preset = st.selectbox("select Household Type:", [
        "Custom (Manual Entry)",
        "Basic Rural Home",
        "Urban Middle-Class Flat",
        "Modern Urban Villa"
    ])

    values = { 'fan_count': 0, 'fan_hours': 0, 'bulb_count': 0, 'bulb_hours': 0,
        'tv': False, 'tv_hours': 0, 'fridge': False, 'router': False,
        'mobile_count': 0, 'mobile_hours': 0, 'laptop_count': 0, 'laptop_hours': 0,
        'ac': False, 'ac_hours': 0, 'washing': False, 'washing_hours': 0,
        'ro': False, 'ro_hours': 0, 'oven': False, 'oven_hours': 0 }

    # Update presets
    if preset == "Basic Rural Home":
        values.update(dict(fan_count=2, fan_hours=6, bulb_count=4, bulb_hours=6, tv=True, tv_hours=3,
                           fridge=True, router=True, mobile_count=2, mobile_hours=2))
    elif preset == "Urban Middle-Class Flat":
        values.update(dict(fan_count=3, fan_hours=6, bulb_count=6, bulb_hours=5, tv=True, tv_hours=3,
                           fridge=True, router=True, mobile_count=3, mobile_hours=2, laptop_count=1,
                           laptop_hours=5, washing=True, washing_hours=0.5, ro=True, ro_hours=2,
                           oven=True, oven_hours=15))
    elif preset == "Modern Urban Villa":
        values.update(dict(fan_count=4, fan_hours=6, bulb_count=10, bulb_hours=5, tv=True, tv_hours=3,
                           fridge=True, router=True, mobile_count=4, mobile_hours=2, laptop_count=2,
                           laptop_hours=4, ac=True, ac_hours=5, washing=True, washing_hours=1,
                           ro=True, ro_hours=2, oven=True, oven_hours=30))

    with st.expander("Appliance Selection")
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

        st.session_state.appliance_energy_used = monthly_energy_kwh
        st.session_state.estimation_done = True
        total_energy_kwh = 0
        total_energy_kwh = 0 
        appliances = []
        num_appliances = st.number_input("How many different types of appliances do you want to enter?", min_value=1, max_value=10, step=1)
        for appliance in appliances:
          watt = appliance["wattage"]
          hours = appliance["hours"]
          quantity = appliance["quantity"]
          energy_kwh = (watt * hours * quantity) / 1000  # Convert Wh to kWh
          total_energy_kwh += energy_kwh

        appliance_energy_used = total_energy_kwh
        required_kw = round(appliance_energy_used / (sun_hours * 30), 2)

        st.session_state['required_kw'] = required_kw
        st.session_state['appliance_energy_used'] = appliance_energy_used
        report = f"""
Smart Solar System Estimation Report (Appliance-Based Mode)

📍 Location: {selected_city}
☀️ Sun Hours: {sun_hours}
📅 Monthly Energy Required: {appliance_energy_used} kWh
🔋 Required Solar Size: {required_kw} kW
🏠 Area Needed: {round(required_kw * area_per_kw, 2)} sq. meters
💸 Estimated System Cost: ₹{round(required_kw * cost_per_kw)}
📂 Usable Battery Capacity (80% DoD): {round((appliance_energy_used / 30) / 0.8, 2)} kWh
🔋 Battery: {math.ceil(((appliance_energy_used / 30) / 0.8 * 1000) / 12 / 150)} x 150Ah (12V)
"""

        st.download_button("📥 Download Full Report", data=report, file_name="solar_estimate_appliances.txt")


# -------------------- INSTALLERS --------------------
if st.session_state.estimation_done:
    st.markdown("### 🛠 Recommended Solar Installers Near You")
    installers = [
        {"name": "SolarPro Energy", "price": 52000, "warranty": "10 years", "rating": 4.5},
        {"name": "SunBright Solar", "price": 55000, "warranty": "12 years", "rating": 4.3},
        {"name": "GreenSpark Installers", "price": 50000, "warranty": "8 years", "rating": 4.2},
    ]

    for idx, installer in enumerate(installers):
        st.markdown(f"**{installer['name']}**  \n💰 ₹{installer['price']}/kW  \n🔹 {installer['warranty']}  \n⭐ {installer['rating']} / 5")
        if st.button(f"📝 Get Estimate from {installer['name']}", key=f"installer_button_{idx}"):
            st.session_state.selected_installer = installer
        st.markdown("---")

    selected_installer = st.session_state.get("selected_installer")
    if selected_installer:
        st.markdown(f"### 📞 Installer Contact Form for *{selected_installer['name']}*")
        name = st.text_input("Full Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        location = st.text_input("Your Location", selected_city)
        required_kw = st.session_state.get("required_kw", 0)
        energy_used = st.session_state.get("monthly_energy_used") if mode == "Monthly Units Estimator" else st.session_state.get("appliance_energy_used", 0)
        st.markdown(f"*Estimated System Size:* {required_kw:.2f} kW")
        st.markdown(f"*Estimated Monthly Usage:* {energy_used:.2f} kWh")
        if st.button("Submit Lead"):
            st.success("✅ Your request has been submitted! We'll connect you with the installer shortly.")
            st.session_state.selected_installer = None

# FOOTER
st.markdown("---")
st.caption(" Smart Solar Estimator | by Ronit Bhati")
