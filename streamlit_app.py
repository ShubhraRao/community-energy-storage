import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Disaster-Ready Community Cost Estimator",
    page_icon=":house:",
    layout="wide"
)

st.title(":house: Disaster-Ready Community Cost Estimator")
st.markdown(
    "This tool estimates the cost of creating a disaster-ready community with solar and battery backups."
)

st.sidebar.header("Community Inputs")
num_houses = st.sidebar.number_input("Number of Houses in the Community", min_value=1, value=100)
average_daily_consumption = st.sidebar.number_input("Average Daily Energy Consumption per House (kWh)", value=30.0)
daily_solar_production = st.sidebar.number_input("Daily Solar Energy Production per House (kWh)", value=35.0)
battery_cost_per_kwh = st.sidebar.number_input("Battery Cost per kWh ($)", value=200.0)
solar_cost_per_kw = st.sidebar.number_input("Solar Installation Cost per kW ($)", value=2500.0)
blackout_duration_hours = st.sidebar.number_input("Expected Blackout Duration (Hours)", value=48)
critical_load_percentage = st.sidebar.slider("Critical Load Percentage During Blackout (%)", 10, 100, 50)

def calculate_energy_needs(num_houses, average_daily_consumption, blackout_duration_hours, critical_load_percentage):
    blackout_duration_days = blackout_duration_hours / 24
    total_daily_consumption = num_houses * average_daily_consumption
    critical_load = (critical_load_percentage / 100) * total_daily_consumption
    total_energy_needed = critical_load * blackout_duration_days
    return total_daily_consumption, total_energy_needed

def calculate_costs(total_energy_needed, num_houses, daily_solar_production, battery_cost_per_kwh, solar_cost_per_kw):
    peak_solar_hours = 6  # Adjust for location
    total_battery_cost = math.ceil(total_energy_needed) * battery_cost_per_kwh
    total_solar_capacity = math.ceil(num_houses * (daily_solar_production / peak_solar_hours))
    total_solar_cost = total_solar_capacity * solar_cost_per_kw
    return total_battery_cost, total_solar_cost, total_battery_cost + total_solar_cost

total_daily_consumption, total_energy_needed = calculate_energy_needs(
    num_houses,
    average_daily_consumption,
    blackout_duration_hours,
    critical_load_percentage
)

total_battery_cost, total_solar_cost, total_project_cost = calculate_costs(
    total_energy_needed,
    num_houses,
    daily_solar_production,
    battery_cost_per_kwh,
    solar_cost_per_kw
)

st.header("Community Disaster-Readiness Analysis")
st.subheader("Energy Needs")
st.metric("Total Daily Community Energy Consumption", f"{total_daily_consumption:,.2f} kWh")
st.metric("Total Energy Required During Blackout", f"{total_energy_needed:,.2f} kWh")

st.subheader("Cost Estimates")
st.metric("Total Battery Cost", f"${total_battery_cost:,.2f}")
st.metric("Total Solar Installation Cost", f"${total_solar_cost:,.2f}")
st.metric("Total Project Cost", f"${total_project_cost:,.2f}")

st.subheader("Energy and Cost Breakdown")
cols = st.columns(2)

with cols[0]:
    energy_data = pd.DataFrame({
        "Metric": ["Daily Consumption", "Energy Needed (Blackout)"],
        "Energy (kWh)": [total_daily_consumption, total_energy_needed]
    })
    fig, ax = plt.subplots()
    energy_data.plot(kind="bar", x="Metric", y="Energy (kWh)", ax=ax, legend=False)
    ax.set_ylabel("Energy (kWh)")
    ax.set_title("Energy Requirements")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)

with cols[1]:
    cost_data = pd.DataFrame({
        "Cost Item": ["Battery", "Solar Installation"],
        "Cost ($)": [total_battery_cost, total_solar_cost]
    })
    fig2, ax2 = plt.subplots()
    cost_data.plot(kind="bar", x="Cost Item", y="Cost ($)", ax=ax2, legend=False)
    ax2.set_ylabel("Cost ($)")
    ax2.set_title("Cost Breakdown")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
    st.pyplot(fig2)

st.subheader("Benefits of Disaster-Ready Communities")
st.markdown(
    "By investing in solar and battery storage, communities can reduce blackout impacts and ensure energy resilience."
)

st.info("Use this analysis to plan your construction project and make your community safer and disaster-ready!")
