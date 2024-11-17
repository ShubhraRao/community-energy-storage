import streamlit as st
import math
import matplotlib.pyplot as plt

# Streamlit Page Configuration
st.set_page_config(
    page_title="Donate Your Excess Energy",
    page_icon=":sparkles:",
    layout="wide"
)

# # Title and Introduction
# st.title(":sparkles: Donate Your Excess Energy")


# Static Variables (Adjustable)
community_name = st.sidebar.text_input("Community Name", value="Menifee, CA")
latitude = 33.6973272
longitude = -117.1956648
estimated_excess_energy = st.sidebar.number_input(
    "Estimated Excess Energy (kWh)", value=5000, step=100
)

# Sidebar Donation Percentage Input
st.sidebar.header("Donation Settings")
donation_percentage = st.sidebar.slider(
    "What percentage of your excess energy would you like to donate?",
    min_value=0,
    max_value=100,
    value=25,  # Default donation
    step=5
)

# Calculations for Donated and Remaining Energy
donated_energy = (donation_percentage / 100) * estimated_excess_energy
remaining_energy = estimated_excess_energy - donated_energy

# Impact Calculations
def calculate_relatable_impacts(energy_donated, shelter_energy=30, tree_energy=1):
    shelters_supported = energy_donated // shelter_energy
    trees_lit = energy_donated // tree_energy
    return {
        "shelters_supported": int(shelters_supported),
        "trees_lit": int(trees_lit)
    }

impact_metrics = calculate_relatable_impacts(donated_energy)

# Header: Community Impact
st.header(f":sparkles: Donate Your Excess Energy from {community_name}")
st.markdown(
    """
    By donating your excess energy, you can make a huge impact on your community. Help power shelters, light up trees, 
    and contribute to a sustainable future!
    """
)
# Metrics Section
st.metric("Total Monthly Excess Energy (kWh)", f"{estimated_excess_energy:,}")
st.metric("Energy Donated (kWh)", f"{donated_energy:,.2f}")
st.metric("Energy Remaining for Community Grid (kWh)", f"{remaining_energy:,.2f}")

# Donation Impact
st.subheader("Your Donation Makes a Difference!")
st.write(
    f"With your donation of {donation_percentage}% of excess energy, "
    f"your community can achieve the following:"
)

# Columns for Metrics
cols = st.columns(2)
with cols[0]:
    st.metric("Shelters Powered", impact_metrics["shelters_supported"])
with cols[1]:
    st.metric("Trees Lit", impact_metrics["trees_lit"])

# Message for the User
st.info(
    "Donating your energy helps support your community in meaningful ways. "
    "Every bit of energy you donate goes a long way in powering vital services!"
)

# Visualization: Energy Flow Breakdown
st.subheader("Energy Flow Breakdown")
labels = ["Donated Energy", "Remaining Energy for Grid"]
sizes = [donated_energy, remaining_energy]
explode = (0.1, 0)  # Highlight the donated energy

fig1, ax1 = plt.subplots()
ax1.pie(
    sizes,
    explode=explode,
    labels=labels,
    autopct="%1.1f%%",
    startangle=140,
    textprops={"fontsize": 12}
)
ax1.set_title("Energy Distribution", fontsize=14)
ax1.axis("equal")
st.pyplot(fig1)

# Footer: Additional Information
st.subheader("Make a Bigger Difference")
st.markdown(
    """
    **Did you know?**  
    A portion of every energy donation goes towards community upliftment projects. [Learn More](https://example.com).  
    Thank you for making a difference!  
    """
)
