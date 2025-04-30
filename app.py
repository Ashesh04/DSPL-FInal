import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components

# Load your data
df = pd.read_csv("revised_demographics_residing_lka.csv")

# ⬅️ This must come early
page = st.sidebar.selectbox("Select a Page", ["Overview", "Geographic Distribution", "Demographics", "Population Type Trends", "Deep Dive Explorer"])
# Load data
df = pd.read_csv("revised_demographics_residing_lka.csv")

# Initialize selected tab
if 'selected_tab' not in st.session_state:
    st.session_state.selected_tab = "Overview"

# Sidebar title
st.sidebar.title("📊 Navigation")

# ---- Custom Button Navigation ---- #
tabs = {
    "Overview": "🏠 Overview",
    "Geographic Distribution": "🌍 Geographic Distribution",
    "Demographics": "👥 Demographics",
    "Population Type Trends": "📈 Population Type Trends",
    "Deep Dive Explorer": "🔍 Deep Dive Explorer"
}

# Button styling
st.markdown("""
    <style>
        .sidebar-button {
            display: block;
            width: 100%;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: #007acc;
            border: none;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .sidebar-button:hover {
            background-color: #005c99;
        }
    </style>
""", unsafe_allow_html=True)

# Render buttons
for tab_key, tab_label in tabs.items():
    if st.sidebar.button(tab_label, key=tab_key):
        st.session_state.selected_tab = tab_key

# Page Title
st.title("🇱🇰 Population Demographics Dashboard - Sri Lanka")

# Page routing
selected_tab = st.session_state.selected_tab

# ---- OVERVIEW PAGE ---- #
if selected_tab == "Overview":
    st.subheader("Overview & Introduction")

    st.markdown("""
    **Welcome to the Sri Lanka Population Demographics Dashboard.**  
    This dashboard presents a comprehensive overview of displaced and affected populations residing in Sri Lanka, 
    including refugees, asylum seekers, internally displaced persons (IDPs), and other categories.

    The data spans from **2001 to the most recent available year**, covering diverse geographic locations and demographic 
    breakdowns such as gender, age, and living conditions (urban/rural).
    """)

    # KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="padding: 20px; background-color: #f0f0f5; border-radius: 10px; font-size: 20px; 
                        font-weight: bold; text-align: center; color: #005c99; height: 150px;">
                Total Population Records<br><span style="font-size: 30px;">{df['Total'].sum():,}</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="padding: 20px; background-color: #f0f0f5; border-radius: 10px; font-size: 20px; 
                        font-weight: bold; text-align: center; color: #005c99; height: 150px;">
                Unique Population Types<br><span style="font-size: 30px;">{df['Population Type'].nunique()}</span>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        male_total = df[[col for col in df.columns if col.startswith("Male")]].sum().sum()
        female_total = df[[col for col in df.columns if col.startswith("Female")]].sum().sum()
        st.markdown(f"""
            <div style="padding: 20px; background-color: #f0f0f5; border-radius: 10px; font-size: 20px; 
                        font-weight: bold; text-align: center; color: #005c99; height: 150px;">
                Gender Ratio (F:M)<br><span style="font-size: 30px;">{female_total:.0f}:{male_total:.0f}</span>
            </div>
        """, unsafe_allow_html=True)

    # ---- Dataset Preview ---- #
    st.markdown("### 📋 Dataset Preview")
    show_full = st.checkbox("Show full dataset", value=False)
    if show_full:
        st.dataframe(df)
    else:
        st.dataframe(df.head(20))


# ---- Geographic Distribution PAGE ---- #
elif selected_tab == "Geographic Distribution":
    st.subheader("🌍 Geographic Distribution")

    # Sidebar filters
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)

    # Filter data
    filtered_df = df[df['Year'].isin(selected_years) & df['Population Type'].isin(selected_pop_types)]

    # Display filtered data
    st.markdown("#### Showing data for selected years and population types")
    st.write(filtered_df.head(10))

    # Create map
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers (static placeholder coordinates)
    for idx, row in filtered_df.iterrows():
        location = row['location']
        population = row['Total']
        population_type = row['Population Type']
        year = row['Year']
        lat, lon = 7.0, 80.0  # Placeholder; replace with actual lat/lon if available

        folium.Marker(
            location=[lat, lon],
            popup=f"<strong>Year:</strong> {year}<br><strong>Location:</strong> {location}<br><strong>Population Type:</strong> {population_type}<br><strong>Total:</strong> {population}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)

    # Display the map
    st.markdown("### Population Distribution Map")
    components.html(m._repr_html_(), height=500)

    # Horizontal Bar Chart: Top 10 locations by total population
    st.markdown("### 📍 Top 10 Locations by Total Population")

    # Aggregate totals per location and population type
    bar_data = filtered_df.groupby(['location', 'Population Type'])['Total'].sum().reset_index()

    # Get top 10 locations by total population (across all types)
    top_locations = bar_data.groupby('location')['Total'].sum().nlargest(10).index

    # Filter bar data to only include those top 10 locations
    bar_data_top = bar_data[bar_data['location'].isin(top_locations)]

    # Plot using Plotly
    fig = px.bar(
        bar_data_top,
        x="Total",
        y="location",
        color="Population Type" if len(selected_pop_types) > 1 else None,
        orientation="h",
        title="Top 10 Locations by Total Population",
        labels={"location": "Location", "Total": "Total Population"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


# ---- Population Type Trends PAGE ---- #
elif selected_tab == "Population Type Trends":
    st.subheader("📈 Population Type Trends")

    # Sidebar filters
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)

    # Filter data
    filtered_df = df[df['Year'].isin(selected_years) & df['Population Type'].isin(selected_pop_types)]

    # Line chart for population trends
    st.markdown("### 📉 Population Type Trends Over Time")
    trend_data = filtered_df.groupby(['Year', 'Population Type'])['Total'].sum().reset_index()
    fig_trends = px.line(trend_data, x='Year', y='Total', color='Population Type',
                         title="Population Type Trends Over Time", markers=True)
    st.plotly_chart(fig_trends, use_container_width=True)

    # Gender Distribution Chart (inside this block to avoid NameError)
    st.markdown("### 🧍‍♂️🧍‍♀️ Gender Distribution by Population Type")
    gender_df = filtered_df.groupby("Population Type")[["Female Total", "Male Total"]].sum().reset_index()

    if gender_df.empty:
        st.warning("No gender data available for the selected filters.")
    else:
        gender_melted = gender_df.melt(id_vars="Population Type",
                                       value_vars=["Female Total", "Male Total"],
                                       var_name="Gender", value_name="Total")
        fig_gender = px.bar(gender_melted, x="Population Type", y="Total",
                            color="Gender", barmode="group",
                            title="Gender Distribution across Population Types")
        st.plotly_chart(fig_gender, use_container_width=True)



