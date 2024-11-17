import streamlit as st
import requests
import json

# Page Configuration
st.set_page_config(
    page_title="Disaster Relief Center Energy Calculator",
    page_icon=":office:",
    layout="wide"
)

# Palmetto API Key
API_KEY = "MoOE7vb4yPDdaUuwtxpC66NuslKPJzbX52DEsGltog0"
API_ENDPOINT = "https://ei.palmetto.com/api/v0/bem/calculate"

# Helper Function: Send API Request
def fetch_power_consumption(stories, sq_feet, appliance_data):
    """
    Fetch power consumption using the Palmetto API based on building details and appliances.
    """
    try:
        sq_meters = sq_feet * 0.092903  # Convert square feet to square meters

        # Construct baseline attributes
        baseline_attributes = [
            {"name": "building_type", "value": building_type},
            {"name": "num_stories", "value": stories},
            {"name": "floor_area", "value": sq_meters},
            {"name": "hvac_cooling", "value": hvac_cooling},
            {"name": "lighting", "value": lighting_type},
            {"name": "plug_loads", "value": max(0.78, plug_load_value)}  # Enforce minimum of 0.78
        ]

        # Add appliances as individual entries (no aggregation for appliances with constraints)
        if isinstance(appliance_data, list):  # Appliance data should be a list for multiple entries
            baseline_attributes.extend(appliance_data)
        else:
            st.error("Appliance data is not a list.")
            return None

        # Construct Payload
        payload = {
            "consumption": {
                "actuals": [
      {
        "from_datetime": "2023-01-01T00:00:00",
        "to_datetime": "2024-01-01T00:00:00",
        "value": 3774,
        "variable": "consumption.electricity"
      }
    ],
                "attributes": {
                    "baseline": baseline_attributes,
                    "hypothetical": []
                },
                "calibration": {
                    "apply_residuals": True,
                    "method": "uniform-mean",
                    "sample_size": 1
                }
            },
            "costs": {
    "emission_rates": {
      "electricity": {
        "units": "kgCO2/kWh",
        "value": 0.47045
      },
      "fossil_fuel": {
        "units": "kgCO2/kWh",
        "value": 0.1872057318321392
      }
    },
            },
            "utility_rates": {
      "electricity": {
        "units": "$/kWh",
        "value": 0.29305
      },
      "fossil_fuel": {
        "units": "$/kWh",
        "value": 0.069771
      },
      "pv_buyback": {
        "units": "$/kWh",
        "value": 0.2
      },
      "pv_ppa": {
        "units": "$/kWh",
        "value": 0.26
      }
    },
            "location": {"latitude": 33.6973272, "longitude": -117.1956648},
            "parameters": {
                "from_datetime": "2023-01-01T00:00:00",
                "to_datetime": "2024-01-01T00:00:00",
                "clip_by": "inner",
                "group_by": "month",
                "interval_format": "long",
                "variables": ["consumption.electricity"]
            },"production": {
    "actuals": [
      {
        "from_datetime": "2023-01-01T00:00:00",
        "to_datetime": "2024-01-01T00:00:00",
        "value": 7.3,
        "variable": "production.electricity"
      }
    ],
    "attributes": {
      "baseline": [
        {
          "name": "capacity",
          "value": 10
        }
      ],
      "hypothetical": []
    },
    "calibration": {
      "method": "uniform-mean"
    }
  },
  "storage": {
    "attributes": {
      "baseline": [
        {
          "name": "capacity",
          "value": 10
        },
        {
          "name": "power",
          "value": 5
        },
        {
          "name": "capacity_recommendation_quantile",
          "value": 0.5
        }
      ],
      "hypothetical": []
    }
  }
}
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

        # API Request
        response = requests.post(API_ENDPOINT, json=payload, headers=headers)

        # st.json(payload)  # Debug: Log payload
        print(json.dumps(payload, indent=2)) 
        if response.status_code == 200:
            # st.json(response.json())
            data = response.json()
            total_annual_consumption = sum(interval["value"] for interval in data["data"]["intervals"])
            return response.json(), total_annual_consumption
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None, total_annual_consumption
    except Exception as e:
        st.error(f"Error fetching power consumption: {e}")
        return None, total_annual_consumption

# Streamlit UI
st.title(":office: Disaster Relief Center Energy Calculator")
st.markdown("Estimate the energy consumption of a disaster relief center based on building details and appliances.")

# Sidebar Inputs
st.sidebar.header("Building Details")
building_type = st.sidebar.selectbox(
    "Select Building Type",
    [
        "Single-Family Detached",
        "Single-Family Attached",
        "Multi-Family (2 units)",
        "Multi-Family (3 or 4 units)",
        "Multi-Family (5 to 9 units)",
        "Multi-Family (10 to 19 units)",
        "Multi-Family (20 to 49 units)",
        "Multi-Family (50 or more units)",
        "Mobile Home",
    ],
)

num_stories = st.sidebar.number_input("Number of Stories", min_value=1, value=1, step=1)
sq_feet = st.sidebar.number_input("Total Square Feet", min_value=100, value=1000, step=100)
hvac_cooling = st.sidebar.checkbox("Enable HVAC Cooling?", value=False)
lighting_type = st.sidebar.selectbox("Lighting Type", ["Incandescent", "CFL", "LED"])

plug_load_options = {
    "Minimal (0.78)": 0.78,
    "Standard (1.0)": 1.0,
    "High (1.5)": 1.5,
    "Maximum (1.66)": 1.66,
}

selected_plug_load = st.sidebar.selectbox("Select Plug Load Bracket", options=list(plug_load_options.keys()))
plug_load_value = plug_load_options[selected_plug_load]

# Appliance Options
appliance_options = {
    "Dishwasher Efficiency": {
        "name": "dishwasher_efficiency",
        "type": "dict",
        "values": {
            "Inefficient": 318,
            "Standard": 290,
            "EnergyStar": 240,
            "EnergyStar Compact": 155,
        },
    },
    "Refrigerator Efficiency": {
        "name": "refrigerator_efficiency",
        "type": "number",
        "range": (0, 1360),
    },
    "Freezer Extra Efficiency": {
        "name": "freezer_extra_efficiency",
        "type": "number",
        "range": (0, 1000),
    },
    "Clothes Dryer Efficiency": {
        "name": "clothes_dryer_efficiency",
        "type": "enum",
        "values": ["None", "Standard", "EnergyStar"],
    },
    "Clothes Washer Efficiency": {
        "name": "clothes_washer_efficiency",
        "type": "enum",
        "values": ["None", "Standard", "EnergyStar"],
    },
}


# Dynamic Appliance Input Section
st.sidebar.header("Add Appliances")
if "appliances" not in st.session_state:
    st.session_state.appliances = []

if st.sidebar.button("Add Appliance"):
    st.session_state.appliances.append({})

# Collect Appliance Inputs
appliance_data = []
for i, appliance in enumerate(st.session_state.appliances):
    st.sidebar.subheader(f"Appliance #{i + 1}")
    appliance_type = st.sidebar.selectbox(
        f"Select Appliance Type #{i + 1}",
        list(appliance_options.keys()),
        key=f"appliance_type_{i}",
    )
    appliance_config = appliance_options[appliance_type]

    if appliance_config["type"] == "enum":
        selected_option = st.sidebar.selectbox(
            f"Select {appliance_type} Option",
            options=appliance_config["values"],
            key=f"appliance_enum_{i}",
        )
        value = selected_option
    elif appliance_config["type"] == "number":
        value = st.sidebar.number_input(
            f"Enter {appliance_type} Value (kWh/year)",
            min_value=appliance_config["range"][0],
            max_value=appliance_config["range"][1],
            value=appliance_config["range"][0],
            step=10,
            key=f"appliance_number_{i}",
        )
    elif appliance_config["type"] == "dict":
        selected_option = st.sidebar.selectbox(
            f"Select {appliance_type} Option",
            options=list(appliance_config["values"].keys()),
            key=f"appliance_dict_{i}",
        )
        value = appliance_config["values"][selected_option]

    # Treat each appliance as an individual entry for API compliance
    appliance_data.append({"name": appliance_config["name"], "value": value})

backup_days = st.sidebar.number_input("Enter the number of backup days required:", min_value=1, value=1, step=1)

# Submit and Fetch Results
if st.sidebar.button("Calculate Energy Consumption"):
    with st.spinner("Calculating power consumption..."):
        api_result, total_annual_consumption = fetch_power_consumption(num_stories, sq_feet, appliance_data)
        print(total_annual_consumption)
        average_daily_consumption = total_annual_consumption / 365
        efficiency = 0.9
        battery_capacity_backup = (average_daily_consumption * backup_days) / efficiency
        peak_shaving_capacity = (average_daily_consumption * 0.2) / efficiency
        
        if api_result:
            total_consumption = sum(
                interval["value"] for interval in api_result.get("intervals", [])
            )
            st.subheader("Results")
            # st.metric("Total Energy Consumption (kWh)", f"{total_annual_consumption:,.2f}")
            st.metric("Average Daily Consumption:", f"{average_daily_consumption:.2f} kWh")
            st.metric("Battery Capacity for", f"{backup_days}-Day Backup: ",f"{battery_capacity_backup:.2f} kWh")
            st.metric("Battery Capacity for Peak Shaving (20%):", f"{peak_shaving_capacity:.2f} kWh")

        else:
            st.error("Failed to fetch results. Please check your inputs.")
