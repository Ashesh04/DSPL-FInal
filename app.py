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

# 3. Gender Breakdown
st.subheader("👫 Gender Breakdown")

gender_cols = ["Female Total", "Male Total", "Female Unknown", "Male Unknown"]
gender_totals = filtered_df[gender_cols].sum()

fig, ax = plt.subplots()
ax.pie(gender_totals, labels=gender_cols, autopct="%1.1f%%", startangle=140)
ax.axis("equal")
st.pyplot(fig)

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
