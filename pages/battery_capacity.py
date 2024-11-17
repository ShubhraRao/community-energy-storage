import streamlit as st
import requests
import datetime
import pandas as pd

# Constants
WEATHER_API_KEY = "d85c0585a6739ae6da983c343f7849cc"
LOCATION = {"lat": 37.7749, "lon": -122.4194}
BATTERY_CAPACITY = 300
battery_state = {"current_level": 150}
heartbeat_frequency = 12  # Heartbeat frequency in minutes (dynamically set)
battery_threshold = 50  # Battery threshold in percentage (dynamically set)


@st.cache_data(ttl=3600)
def fetch_weather():
    url = f"https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": LOCATION["lat"],
        "lon": LOCATION["lon"],
        "exclude": "current,minutely",
        "appid": WEATHER_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Weather API Error: {response.status_code}, {response.text}")


def analyze_alerts(weather_data):
    """
    Analyze alerts and dynamically display warning or error messages.
    """
    severe_alert_detected = False

    if "alerts" in weather_data:
        for alert in weather_data["alerts"]:
            event = alert["event"]
            description = alert["description"]
            tags = alert.get("tags", [])
            start = datetime.datetime.fromtimestamp(alert["start"]).strftime("%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.fromtimestamp(alert["end"]).strftime("%Y-%m-%d %H:%M:%S")

            # Display Alert Information
            if any(tag in ["Flood", "Storm", "Coastal event"] for tag in tags):
                st.error(f"🚨 Severe Warning Detected: {event}")
                severe_alert_detected = True
            else:
                st.warning(f"⚠️ Alert: {event}")
            st.warning(
            f"""
            **Event**: {alert['event']}  
            **Sender**: {alert['sender_name']}  
            **Description**: {alert['description']}  
            **Start**: {start}  
            **End**: {end}  
            **Tags**: {', '.join(alert['tags'])}
            """)

    if not severe_alert_detected:
        st.success("✅ No Severe Alerts Detected.")

    return severe_alert_detected



def predict_generation(weather_data):
    hourly_data = weather_data["hourly"]
    generation_forecast = []
    for hour in hourly_data:
        timestamp = datetime.datetime.fromtimestamp(hour["dt"])
        solar_radiation = hour.get("uvi", 0)
        estimated_generation = solar_radiation * 5
        generation_forecast.append({"timestamp": timestamp, "generation": estimated_generation})
    return pd.DataFrame(generation_forecast)


def decision_maker(generation_forecast, battery_state, conserve_energy):
    decisions = []
    for _, row in generation_forecast.iterrows():
        timestamp = row["timestamp"]
        generation = row["generation"]
        available_capacity = BATTERY_CAPACITY - battery_state["current_level"]

        if conserve_energy or (generation <= available_capacity and battery_state["current_level"] <= battery_threshold):
            decision = "Store Energy"
            battery_state["current_level"] += generation * 0.8
        else:
            decision = "Push to Grid"
            battery_state["current_level"] -= 10

        battery_state["current_level"] = max(0, min(BATTERY_CAPACITY, battery_state["current_level"]))
        decisions.append({"timestamp": timestamp, "decision": decision, "battery_level": battery_state["current_level"]})
    return pd.DataFrame(decisions)


# Streamlit UI
st.title("⚡ Monitor your EnergyHaven:")

# Sidebar (Dynamic Settings)
st.sidebar.header("CON")
st.sidebar.markdown(f"**Heartbeat Frequency**: {heartbeat_frequency} minutes")
st.sidebar.markdown(f"**Battery Threshold**: {battery_threshold}%")
st.sidebar.markdown(f"**Initial Battery Level**: {battery_state['current_level']} kWh")
st.sidebar.markdown(f"**Total Battery Capacity**: {BATTERY_CAPACITY} kWh")

# Main Simulation Logic
# if st.button("Simulate Energy Management"):
with st.spinner("Fetching weather data..."):
    weather_data = fetch_weather()

# Alerts and Decisions
conserve_energy = analyze_alerts(weather_data)
generation_forecast = predict_generation(weather_data)
decision_df = decision_maker(generation_forecast, battery_state, conserve_energy)

# Battery Visualization
st.subheader("Your EnergyHaven")
battery_percentage = (battery_state["current_level"] / BATTERY_CAPACITY) * 100
st.progress(int(battery_percentage))
st.write(f"Battery Level: **{battery_state['current_level']:.2f} / {BATTERY_CAPACITY} kWh**")
if conserve_energy:
    st.write("⚠️ Push to Grid Paused Due to Alert Detected!")

# Timeline Chart
st.subheader("Energy Management Decisions")
st.line_chart(decision_df.set_index("timestamp")["battery_level"], use_container_width=True)
st.write(decision_df)
