import streamlit as st
import math

# --- Header ---
st.title("Medical Test Pricing Calculator")
st.write("""
This tool helps you analyze the impact of pricing and test volume on revenue, cost, and profit margins.  
You can adjust your test price, volume, and opex assumptions to simulate business performance.
""")

# --- Inputs ---
st.header("Input Parameters")

current_price = st.number_input("Current Price per Test (₦)", min_value=0, value=8000, step=500)
cost_per_test = st.number_input("Cost per Test (₦)", min_value=0, value=6000, step=500)
current_volume = st.number_input("Current Monthly Volume (Tests)", min_value=1, value=100)
proposed_price = st.number_input("Proposed Price per Test (₦)", min_value=0, value=9000, step=500)
proposed_volume = st.number_input("Expected Volume at Proposed Price (Tests)", min_value=1, value=150)

volume_opex_adj = st.slider("Opex Adjustment (%) for Volume Increase", 0, 50, 20)

# --- Calculations ---
# Current performance
current_revenue = current_price * current_volume
current_cogs = cost_per_test * current_volume
current_opex = 0.25 * current_revenue
current_profit = current_revenue - current_cogs - current_opex
current_margin = (current_profit / current_revenue) * 100

# Proposed performance
proposed_revenue = proposed_price * proposed_volume
proposed_cogs = cost_per_test * proposed_volume

# Adjust OPEX to reflect scaling effect with test volume
volume_increase_factor = (proposed_volume - current_volume) / current_volume
opex_increase = max(0, volume_increase_factor) * (volume_opex_adj / 100)
proposed_opex = (0.25 * proposed_revenue) * (1 + opex_increase)

proposed_profit = proposed_revenue - proposed_cogs - proposed_opex
proposed_margin = (proposed_profit / proposed_revenue) * 100

# --- Rounding ---
def round_up(value):
    return int(math.ceil(value / 100.0)) * 100

current_revenue = round_up(current_revenue)
current_cogs = round_up(current_cogs)
current_opex = round_up(current_opex)
current_profit = round_up(current_profit)

proposed_revenue = round_up(proposed_revenue)
proposed_cogs = round_up(proposed_cogs)
proposed_opex = round_up(proposed_opex)
proposed_profit = round_up(proposed_profit)

# --- Results ---
st.header("Performance Summary")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Scenario")
    st.write(f"**Revenue:** ₦{current_revenue:,}")
    st.write(f"**COGS:** ₦{current_cogs:,}")
    st.write(f"**OPEX (25%):** ₦{current_opex:,}")
    st.write(f"**Profit:** ₦{current_profit:,}")
    st.write(f"**Profit Margin:** {current_margin:.1f}%")

with col2:
    st.subheader("Proposed Scenario")
    st.write(f"**Revenue:** ₦{proposed_revenue:,}")
    st.write(f"**COGS:** ₦{proposed_cogs:,}")
    st.write(f"**OPEX (Adjusted):** ₦{proposed_opex:,}")
    st.write(f"**Profit:** ₦{proposed_profit:,}")
    st.write(f"**Profit Margin:** {proposed_margin:.1f}%")

# --- Comparison Insight ---
st.header("Business Impact")
st.write(f"- Revenue change: ₦{round_up(proposed_revenue - current_revenue):,}")
st.write(f"- Profit change: ₦{round_up(proposed_profit - current_profit):,}")
st.write(f"- Profit margin change: {(proposed_margin - current_margin):.1f}%")
st.write(f"- Opex increased by approximately {opex_increase * 100:.1f}% due to higher volume.")
