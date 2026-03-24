import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: white;
}
</style>
""", unsafe_allow_html=True)

df = pd.read_csv("Nassau Candy Distributor.csv")
# Show confirmation
#st.success("File loaded successfully ✅")

# Show shape
#st.write("Shape of dataset:", df.shape)

# Show first 5 rows
#st.dataframe(df.head())

# Convert Order Date
df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df = df.dropna(subset=["Order Date"])

# Create Margin %
df["Margin %"] = (df["Gross Profit"] / df["Sales"]) * 100

# ---------------- SIDEBAR ----------------
st.sidebar.header("Dashboard Filters")

# Date Range Filter
start_date = st.sidebar.date_input(
    "Start Date",
    df["Order Date"].min().date()
)

end_date = st.sidebar.date_input(
    "End Date",
    df["Order Date"].max().date()
)

# Division Filter
division_filter = st.sidebar.multiselect(
    "Select Division",
    df["Division"].unique(),
    default=df["Division"].unique()
)

# Margin Threshold
margin_threshold = st.sidebar.slider(
    "Margin Threshold (%)",
    0, 100, 20
)

# Product Search
# Create division-based dataframe
division_filtered_df = df[df["Division"].isin(division_filter)]

# Product Search (dependent on division)
product_search = st.sidebar.multiselect(
    "Select Product",
    options=sorted(division_filtered_df["Product Name"].unique())
)

# Apply Filters
filtered_df = df[
    (df["Order Date"].dt.date >= start_date) &
    (df["Order Date"].dt.date <= end_date) &
    (df["Division"].isin(division_filter)) &
    (df["Margin %"] >= margin_threshold)
]

# Product Filter
if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"].isin(product_search)
    ]

#Title
st.title("📊 Product Profitability & Margin Performance Dashboard — Nassau Candy Distributor")

# KPI CALCULATIONS
# ==============================
st.markdown("""
<style>

.kpi-container{
    text-align:center;
}

.kpi-icon{
    font-size:22px;
    margin-bottom:4px;
}

.kpi-value{
    font-size:32px;
    font-weight:700;
    color:#ffffff;
}


.kpi-title{
    font-size:18px;
    font-weight:600;
    color:#d0d0d0;
}

</style>
""", unsafe_allow_html=True)


# Base Totals
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_units = filtered_df["Units"].sum()

# 1️⃣ Gross Margin (%)
gross_margin = (total_profit / total_sales) * 100 if total_sales != 0 else 0

# 2️⃣ Profit per Unit
profit_per_unit = total_profit / total_units if total_units != 0 else 0


# ==============================
# Product Contribution
# ==============================

product_summary = filtered_df.groupby("Product Name").agg({
    "Sales": "sum",
    "Gross Profit": "sum"
}).reset_index()

# Top product by revenue
top_revenue_product = product_summary.sort_values(
    by="Sales",
    ascending=False
).iloc[0]

revenue_contribution = (
    top_revenue_product["Sales"] / total_sales
) * 100 if total_sales != 0 else 0


# Top product by profit
top_profit_product = product_summary.sort_values(
    by="Gross Profit",
    ascending=False
).iloc[0]

profit_contribution = (
    top_profit_product["Gross Profit"] / total_profit
) * 100 if total_profit != 0 else 0


# ==============================
# Margin Volatility
# ==============================

monthly_margin = filtered_df.groupby(
    pd.Grouper(key="Order Date", freq="M")
)[["Sales", "Gross Profit"]].sum()

monthly_margin["Margin %"] = (
    monthly_margin["Gross Profit"] /
    monthly_margin["Sales"]
) * 100

monthly_margin = monthly_margin.replace([float("inf"), -float("inf")], 0)

margin_volatility = monthly_margin["Margin %"].std()

###################


col1, col2, col3, col4, col5 = st.columns(5)

col1.markdown(f"""
<div class="kpi-container">
<div class="kpi-icon">💰</div>
<div class="kpi-value">{gross_margin:.2f}%</div>
<div class="kpi-title">Gross Margin</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-container">
<div class="kpi-icon">📦</div>
<div class="kpi-value">${profit_per_unit:.2f}</div>
<div class="kpi-title">Profit / Unit</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-container">
<div class="kpi-icon">📊</div>
<div class="kpi-value">{revenue_contribution:.2f}%</div>
<div class="kpi-title">Revenue Share</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-container">
<div class="kpi-icon">🏆</div>
<div class="kpi-value">{profit_contribution:.2f}%</div>
<div class="kpi-title">Profit Share</div>
</div>
""", unsafe_allow_html=True)

col5.markdown(f"""
<div class="kpi-container">
<div class="kpi-icon">📉</div>
<div class="kpi-value">{margin_volatility:.2f}</div>
<div class="kpi-title">Margin Volatility</div>
</div>
""", unsafe_allow_html=True)

#######################



# Aggregate product metrics
product_summary = filtered_df.groupby("Product Name").agg({
    "Sales": "sum",
    "Gross Profit": "sum",
    "Units": "sum"
}).reset_index()

# Calculate margin & profit per unit
product_summary["Margin %"] = (
    product_summary["Gross Profit"] /
    product_summary["Sales"]
) * 100

product_summary["Profit per Unit"] = (
    product_summary["Gross Profit"] /
    product_summary["Units"]
)
st.markdown("<br><br>", unsafe_allow_html=True)
########################


import plotly.express as px

st.subheader("🏆 Product Margin(%) Performance Leaderboard")

margin_leaderboard = product_summary.sort_values(
    by="Margin %",
    ascending=True
)

fig = px.bar(
    margin_leaderboard,
    x="Margin %",
    y="Product Name",
    orientation="h",
    color="Margin %",
    color_continuous_scale="Blues",
    hover_data=["Sales", "Gross Profit", "Units"],
    text="Margin %"   # 👈 shows values on bars
)

fig.update_traces(
    texttemplate="%{text:.1f}%",   # format percentage
    textposition="outside"         # place text outside bar
)

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    #title="Product Margin Performance",
    height=600,
    coloraxis_showscale=False,
    yaxis_title=None,
    xaxis_visible=False,
     margin=dict(t=30) 
)

st.plotly_chart(fig, use_container_width=True)
#########################################

import plotly.express as px

# Calculate total profit
total_profit = product_summary["Gross Profit"].sum()

# Profit contribution %
product_summary["Profit Contribution %"] = (
    product_summary["Gross Profit"] / total_profit
) * 100

# Sort products by profit
profit_contribution = product_summary.sort_values(
    by="Gross Profit",
    ascending=False
)

st.subheader("💰 Profit Contribution by Product")

fig = px.bar(
    profit_contribution,
    x="Product Name",
    y="Gross Profit",
    color="Gross Profit",
    color_continuous_scale="Greens",
    hover_data=["Sales", "Units", "Profit Contribution %"],
    text="Profit Contribution %"
)

fig.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    xaxis_title=None,
    yaxis_title="Gross Profit",
    margin=dict(t=30),
    height=500
)

st.plotly_chart(fig, use_container_width=True)


#  Division Performance Dashboard
# ● Revenue vs profit comparison
# ● Margin distribution by division



import plotly.graph_objects as go

st.subheader("🏢 Revenue vs Profit by Division")

# Aggregate division metrics
division_summary = filtered_df.groupby("Division").agg({
    "Sales": "sum",
    "Gross Profit": "sum"
}).reset_index()

# Sort by revenue
division_summary = division_summary.sort_values(
    by="Sales",
    ascending=False
)

fig = go.Figure()

# Revenue bars
fig.add_trace(go.Bar(
    x=division_summary["Division"],
    y=division_summary["Sales"],
    name="Revenue",
    marker_color="#1e3a8a",
    text=division_summary["Sales"],
    texttemplate="$%{text:,.0f}",
    textposition="outside"
))

# Profit bars
fig.add_trace(go.Bar(
    x=division_summary["Division"],
    y=division_summary["Gross Profit"],
    name="Profit",
    marker_color="#0d9488",
    text=division_summary["Gross Profit"],
    texttemplate="$%{text:,.0f}",
    textposition="outside"
))

fig.update_layout(
    barmode="group",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis_visible=False,
    #title="Revenue vs Profit by Division",
    margin=dict(t=30),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

###################
st.subheader("📊 Margin Distribution by Division")

# Calculate margin %
division_summary["Margin %"] = (
    division_summary["Gross Profit"] /
    division_summary["Sales"]
) * 100

division_summary = division_summary.sort_values(
    by="Margin %",
    ascending=False
)

import numpy as np
import matplotlib.pyplot as plt

# Professional gradient colors
colors = plt.cm.cividis(
    np.linspace(0.3, 0.9, len(division_summary))
)

fig, ax = plt.subplots(figsize=(8,5))
fig.patch.set_alpha(0)
ax.set_facecolor("none")

# Remove white background
fig.patch.set_alpha(0)
ax.set_facecolor("none")

bars = ax.barh(
    division_summary["Division"],
    division_summary["Margin %"],
    color=colors,
    height=0.6
)

#ax.set_title("Division Margin Performance", color="white")
ax.tick_params(axis='y', colors='white')

ax.invert_yaxis()

# Remove x-axis
ax.xaxis.set_visible(False)

# Remove borders
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)

# Add labels
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 0.3,
        bar.get_y() + bar.get_height()/2,
        f"{width:.1f}%",
        va="center",
        fontsize=9,
        color="white"
    )

st.pyplot(fig)
# Title color
ax.set_title("Division Margin Performance", color="white")

# Y-axis labels color (division names)
ax.tick_params(axis='y', colors='white')


##########
#  Cost vs Margin Diagnostics
# ● Cost-sales scatter plots
# ● Margin risk flags
st.subheader("📉 Cost vs Margin Diagnostics")

# Aggregate product level metrics
cost_summary = filtered_df.groupby("Product Name").agg({
    "Sales": "sum",
    "Cost": "sum",
    "Gross Profit": "sum",
    "Units": "sum"
}).reset_index()

# Calculate Margin %
cost_summary["Margin %"] = (
    cost_summary["Gross Profit"] / cost_summary["Sales"]
).replace([float("inf"), -float("inf")], 0) * 100

# Profit per unit
cost_summary["Profit per Unit"] = (
    cost_summary["Gross Profit"] / cost_summary["Units"]
)

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10,6))

fig.patch.set_alpha(0)
ax.set_facecolor("none")

# Scatter plot with margin coloring
scatter = ax.scatter(
    cost_summary["Sales"],
    cost_summary["Cost"],
    c=cost_summary["Margin %"],
    cmap="RdYlGn",
    s=120,
    alpha=0.85
)

# Median diagnostic lines
sales_median = cost_summary["Sales"].median()
cost_median = cost_summary["Cost"].median()

ax.axvline(sales_median, linestyle="--", alpha=0.5)
ax.axhline(cost_median, linestyle="--", alpha=0.5)

ax.set_xlabel("Sales", color="white")
ax.set_ylabel("Cost", color="white")
ax.set_title("Cost vs Sales Efficiency by Product", color="white")

ax.tick_params(colors="white")
ax.grid(True, linestyle="--", alpha=0.25)

# Remove borders
for spine in ax.spines.values():
    spine.set_visible(False)

# Color bar for margin
cbar = plt.colorbar(scatter)
cbar.set_label("Margin %", color="white")
cbar.ax.yaxis.set_tick_params(color="white")
plt.setp(cbar.ax.get_yticklabels(), color="white")

st.pyplot(fig)




# Identify risky products
risk_products = cost_summary[cost_summary["Margin %"] < 10]

st.subheader("⚠ Margin Risk Products")

if risk_products.empty:

    st.success("✅ No margin risk products detected")

else:

    risk_products = risk_products.sort_values(
        by="Margin %",
        ascending=True
    )

    fig, ax = plt.subplots(figsize=(9,5))

    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # Red bars for risky products
    bars = ax.barh(
        risk_products["Product Name"],
        risk_products["Margin %"],
        color="#ef4444"
    )

    # Risk threshold line
    ax.axvline(
        10,
        linestyle="--",
        color="orange",
        alpha=0.8
    )

    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")

    # Remove borders
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Margin labels
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.3,
            bar.get_y() + bar.get_height()/2,
            f"{width:.1f}%",
            va="center",
            color="white"
        )

    st.pyplot(fig)
#  Profit Concentration Analysis
# ● Pareto charts
# ● Dependency indicators
st.subheader("📊 Profit Concentration Analysis (Pareto)")

# Aggregate product profit
pareto_df = filtered_df.groupby("Product Name").agg({
    "Gross Profit": "sum"
}).reset_index()

# Sort descending
pareto_df = pareto_df.sort_values(
    by="Gross Profit",
    ascending=False
)

# Cumulative %
pareto_df["Cumulative %"] = (
    pareto_df["Gross Profit"].cumsum() /
    pareto_df["Gross Profit"].sum()
) * 100

# Products contributing to 80% profit
top_products = pareto_df[
    pareto_df["Cumulative %"] <= 80
]

dependency_ratio = (
    len(top_products) /
    len(pareto_df)
) * 100


# ---------------- KPI SECTION ---------------- #

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Products Generating 80% Profit",
        len(top_products)
    )

with col2:
    st.metric(
        "Total Products",
        len(pareto_df)
    )

with col3:
    st.metric(
        "Profit Dependency %",
        f"{dependency_ratio:.1f}%"
    )


# ---------------- PARETO CHART ---------------- #

import matplotlib.pyplot as plt

pareto_chart_df = pareto_df.head(25)

fig, ax1 = plt.subplots(figsize=(11,5))

fig.patch.set_alpha(0)
ax1.set_facecolor("none")

# Profit bars
bars = ax1.bar(
    pareto_chart_df["Product Name"],
    pareto_chart_df["Gross Profit"],
    color="#3b82f6"
)

ax1.set_ylabel("Profit", color="white")
ax1.tick_params(axis='y', colors='white')
ax1.tick_params(axis='x', colors='white')

plt.xticks(rotation=70)

# Cumulative line
ax2 = ax1.twinx()

ax2.plot(
    pareto_chart_df["Product Name"],
    pareto_chart_df["Cumulative %"],
    color="#f97316",
    marker="o",
    linewidth=2
)

ax2.set_ylabel("Cumulative %", color="white")
ax2.tick_params(axis='y', colors='white')

# 80% reference line
ax2.axhline(
    80,
    color="#22c55e",
    linestyle="--",
    linewidth=2
)

# Highlight the 80% zone
ax2.fill_between(
    pareto_chart_df["Product Name"],
    pareto_chart_df["Cumulative %"],
    80,
    where=(pareto_chart_df["Cumulative %"] <= 80),
    color="#22c55e",
    alpha=0.15
)

# Remove borders
for spine in ax1.spines.values():
    spine.set_visible(False)

for spine in ax2.spines.values():
    spine.set_visible(False)

ax1.set_title(
    "Profit Contribution by Product (Pareto Analysis)",
    color="white",
    fontsize=14
)

st.pyplot(fig)

# ---------------- FOOTER ---------------- #

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<style>
.footer {
    position: relative;
    text-align: center;
    padding: 20px;
    margin-top: 40px;
    border-top: 1px solid #444;
}

.footer a {
    text-decoration: none;
    padding: 10px 18px;
    margin: 8px;
    border-radius: 8px;
    font-weight: 600;
    display: inline-block;
}

.github {
    background-color: #24292e;
    color: white !important;
}

.linkedin {
    background-color: #0A66C2;
    color: white !important;
}

.footer a:hover {
    opacity: 0.8;
}
</style>

<div class="footer">

<h5>👩‍💻 Created by Prachi Patil</h5>

<a class="github" href="https://github.com/prachipatil1301" target="_blank">
🚀 GitHub
</a>

<a class="linkedin" href="https://linkedin.com/in/prachi-patil-5a3a61392" target="_blank">
💼 LinkedIn
</a>

</div>
""", unsafe_allow_html=True)
