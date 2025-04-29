import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("revised_demographics_residing_lka.csv")

df = load_data()

# Page setup
st.set_page_config(page_title="Sri Lanka Demographics Dashboard", layout="wide")

# Title
st.title("📊 Comprehensive Dashboard: Displaced Populations in Sri Lanka")

# Sidebar Filters
st.sidebar.header("🔎 Filter Your Data")

# Year Filter
years = sorted(df["Year"].unique())
year_selected = st.sidebar.multiselect("Select Year(s):", years, default=years)

# Population Type Filter
pop_types = df["Population Type"].unique()
pop_selected = st.sidebar.multiselect("Select Population Type(s):", pop_types, default=list(pop_types))

# Urban/Rural Filter
urban_rural = df["urbanRural"].unique()
urban_selected = st.sidebar.multiselect("Select Urban/Rural Type(s):", urban_rural, default=list(urban_rural))

# Accommodation Type Filter
accom_types = df["accommodationType"].unique()
accom_selected = st.sidebar.multiselect("Select Accommodation Type(s):", accom_types, default=list(accom_types))

# Filtering dataset
filtered_df = df[
    (df["Year"].isin(year_selected)) &
    (df["Population Type"].isin(pop_selected)) &
    (df["urbanRural"].isin(urban_selected)) &
    (df["accommodationType"].isin(accom_selected))
]

# Metric cards
st.metric("👥 Total People (Filtered)", f"{filtered_df['Total'].sum():,}")
st.metric("📍 Number of Unique Locations", filtered_df['location'].nunique())
st.metric("🌎 Countries of Origin", filtered_df['Country of Origin Name'].nunique())

st.divider()

# Main Analysis

# 1. Population by Year
st.subheader("🗓️ Population Over Years")
pop_by_year = filtered_df.groupby("Year")["Total"].sum()
st.line_chart(pop_by_year)

# 2. Top Locations
st.subheader("🏙️ Top 10 Locations by Population")
top_locations = filtered_df.groupby("location")["Total"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_locations)

# 3. Gender Overview + Age Group Breakdown
st.subheader("👫 Gender Overview and Age Group Breakdown")

# --- Overall Gender Split (Including Unknowns) ---
st.markdown("### 🧮 Overall Gender Split")
overall_gender = {
    "Female Total": filtered_df["Female Total"].sum(),
    "Male Total": filtered_df["Male Total"].sum(),
    "Female Unknown": filtered_df["Female Unknown"].sum(),
    "Male Unknown": filtered_df["Male Unknown"].sum()
}
fig_overall, ax_overall = plt.subplots()
ax_overall.pie(overall_gender.values(), labels=overall_gender.keys(), autopct="%1.1f%%", startangle=90)
ax_overall.axis("equal")
st.pyplot(fig_overall)

# --- Female Age Group Breakdown ---
st.markdown("### 👩 Female Age Group Breakdown")
female_age_cols = ["Female 0-4", "Female 5-11", "Female 12-17", "Female 18-59", "Female 60 or more"]
female_ages = filtered_df[female_age_cols].sum()
fig_female, ax_female = plt.subplots()
ax_female.pie(female_ages.values, labels=female_ages.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
ax_female.axis("equal")
st.pyplot(fig_female)

# --- Male Age Group Breakdown ---
st.markdown("### 👨 Male Age Group Breakdown")
male_age_cols = ["Male 0-4", "Male 5-11", "Male 12-17", "Male 18-59", "Male 60 or more"]
male_ages = filtered_df[male_age_cols].sum()
fig_male, ax_male = plt.subplots()
ax_male.pie(male_ages.values, labels=male_ages.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("muted"))
ax_male.axis("equal")
st.pyplot(fig_male)


# 4. Urban vs Rural
st.subheader("🏡 Urban vs Rural Distribution")
urban_counts = filtered_df["urbanRural"].value_counts()
fig2, ax2 = plt.subplots()
urban_counts.plot(kind="bar", color="skyblue", ax=ax2)
ax2.set_ylabel("Number of Records")
st.pyplot(fig2)

# 5. Accommodation Types
st.subheader("🏠 Accommodation Type Distribution")
accom_counts = filtered_df["accommodationType"].value_counts()
fig3, ax3 = plt.subplots()
accom_counts.plot(kind="bar", color="lightgreen", ax=ax3)
ax3.set_ylabel("Number of Records")
st.pyplot(fig3)

# 6. Population Type Encoded
st.subheader("🛂 Population Categories")
encoded_cols = ["PopType_ASY", "PopType_IDP", "PopType_RDP", "PopType_REF", "PopType_RET"]

encoded_counts = {}
for col in encoded_cols:
    encoded_counts[col] = filtered_df[col].sum()

encoded_series = pd.Series(encoded_counts)
fig4, ax4 = plt.subplots()
encoded_series.plot(kind="barh", color="coral", ax=ax4)
ax4.set_xlabel("Number of Cases")
st.pyplot(fig4)

# 7. Country of Origin vs Asylum
st.subheader("🌍 Country of Origin vs Country of Asylum")
origin_asylum = filtered_df.groupby(["Country of Origin Name", "Country of Asylum Name"])["Total"].sum().reset_index()
st.dataframe(origin_asylum)

st.divider()

# Download filtered dataset
st.sidebar.download_button(
    label="📥 Download Filtered Dataset",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_sri_lanka_data.csv",
    mime="text/csv"
)

st.markdown("Developed for 5DATA004W – Comprehensive Dashboard")

# =============================
# 1. OVERALL OVERVIEW SECTION
# =============================

st.header("📋 Overall Overview")

# --- Big KPI Cards ---
total_population = df["Total"].sum()

# Calculate total Refugees, IDPs, Asylum Seekers
# Assuming Population Type column has values like REF, IDP, ASY
relevant_types = ["REF", "IDP", "ASY"]
total_relevant = df[df["Population Type"].isin(relevant_types)]["Total"].sum()

col1, col2 = st.columns(2)

with col1:
    st.metric(label="👥 Total Population Residing in Sri Lanka", value=f"{total_population:,}")

with col2:
    st.metric(label="🛂 Total Refugees, IDPs, Asylum Seekers", value=f"{total_relevant:,}")

st.divider()

# --- Urban vs Rural Pie Chart ---
st.subheader("🏡 Urban vs Rural Population Split")

urban_rural_counts = df["urbanRural"].value_counts()
fig_urban_rural, ax_urban_rural = plt.subplots()
ax_urban_rural.pie(
    urban_rural_counts.values,
    labels=urban_rural_counts.index,
    autopct="%1.1f%%",
    startangle=90,
    colors=["#4CAF50", "#2196F3", "#FFC107"]
)
ax_urban_rural.axis("equal")
st.pyplot(fig_urban_rural)

st.divider()

# --- Year Range ---
st.subheader("📅 Year Range Covered")

earliest_year = df["Year"].min()
latest_year = df["Year"].max()

st.info(f"**Dataset covers from {earliest_year} to {latest_year}**")

