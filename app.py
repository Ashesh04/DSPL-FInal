import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
from PIL import Image

# Background image CSS
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("cover.jpeg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load your data
df = pd.read_csv("revised_demographics_residing_lka.csv")

# ⬅️ This must come early
page = st.sidebar.selectbox("Select a Page", ["Overview", "Geographic Distribution", "Demographics", "Population Type Trends", "Deep Dive Explorer"])

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

# Page routing
selected_tab = st.session_state.selected_tab

# Overview page
if selected_tab == "Overview":
    st.title("📊 Population Demographics Dashboard - Sri Lanka")

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

# ---- Demographics PAGE ---- #
elif selected_tab == "Demographics":
    import plotly.express as px

    st.subheader("👥 Demographics by Age and Gender")

    # --- Filters --- #
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())

    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=[years[-1]])
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=[population_types[0]])

    demo_df = df[(df['Year'].isin(selected_years)) & (df['Population Type'].isin(selected_pop_types))]

    st.markdown("### 👤 Gender & Age Distribution Overview")
    chart_mode = st.radio("Choose View", ["Overall Gender Distribution", "Male Age Categories", "Female Age Categories"], horizontal=True)

    male_cols = [col for col in df.columns if col.startswith("Male ") and col != "Male Total"]
    female_cols = [col for col in df.columns if col.startswith("Female ") and col != "Female Total"]
    total_male = demo_df[male_cols].sum().sum()
    total_female = demo_df[female_cols].sum().sum()

    if chart_mode == "Overall Gender Distribution":
        gender_data = pd.DataFrame({
            "Gender": ["Male", "Female"],
            "Count": [total_male, total_female]
        })
        fig = px.pie(gender_data, names="Gender", values="Count", title="Gender Distribution",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=16, textfont_color='white', textfont_family='Arial')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_mode == "Male Age Categories":
        male_age_data = demo_df[male_cols].sum().reset_index()
        male_age_data.columns = ["Age Group", "Count"]
        male_age_data["Age Group"] = male_age_data["Age Group"].str.replace("Male ", "")
        fig = px.pie(male_age_data, names="Age Group", values="Count", title="Male Age Distribution",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=16, textfont_color='white', textfont_family='Arial')
        st.plotly_chart(fig, use_container_width=True)

    elif chart_mode == "Female Age Categories":
        female_age_data = demo_df[female_cols].sum().reset_index()
        female_age_data.columns = ["Age Group", "Count"]
        female_age_data["Age Group"] = female_age_data["Age Group"].str.replace("Female ", "")
        fig = px.pie(female_age_data, names="Age Group", values="Count", title="Female Age Distribution",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=16, textfont_color='white', textfont_family='Arial')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📊 Stacked Bar Chart: Population by Age & Gender")

    age_groups = [col.replace("Male ", "") for col in male_cols]
    stacked_data = pd.DataFrame({
        "Age Group": age_groups,
        "Male": demo_df[male_cols].sum().values,
        "Female": demo_df[female_cols].sum().values
    })
    stacked_melted = stacked_data.melt(id_vars="Age Group", var_name="Gender", value_name="Count")

    fig_bar = px.bar(
        stacked_melted,
        x="Age Group",
        y="Count",
        color="Gender",
        barmode="stack",
        title="Stacked Age & Gender Distribution",
        color_discrete_map={"Male": "#5DADE2", "Female": "#AF7AC5"}
    )
    fig_bar.update_layout(xaxis_title="Age Group", yaxis_title="Population Count")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 🔍 Gender and Population Type Relationship")

    selected_years_relation = st.multiselect("Select Year(s)", years, default=years)
    selected_pop_type_radio = st.radio("Select Population Type", population_types)

    relation_df = df[(df['Year'].isin(selected_years_relation)) & (df['Population Type'] == selected_pop_type_radio)]

    male_long = relation_df.melt(id_vars=['Year', 'Population Type'], value_vars=male_cols, var_name='Age Group', value_name='Count')
    male_long['Gender'] = 'Male'
    male_long['Age Group'] = male_long['Age Group'].str.replace('Male ', '')

    female_long = relation_df.melt(id_vars=['Year', 'Population Type'], value_vars=female_cols, var_name='Age Group', value_name='Count')
    female_long['Gender'] = 'Female'
    female_long['Age Group'] = female_long['Age Group'].str.replace('Female ', '')

    combined_long = pd.concat([male_long, female_long])

    fig_combo = px.bar(
        combined_long,
        x='Age Group',
        y='Count',
        color='Gender',
        facet_col='Population Type',
        barmode='group',
        category_orders={"Age Group": ["0-4", "5-11", "12-17", "18-59", "60 or more"]},
        title="Gender and Age Distribution by Population Type",
        color_discrete_map={"Male": "#5DADE2", "Female": "#AF7AC5"}
    )
    fig_combo.update_layout(height=600, xaxis_title="Age Group", yaxis_title="Population Count")
    st.plotly_chart(fig_combo, use_container_width=True)

    st.markdown("This chart highlights the relationship between gender, age groups, and different population types across selected years.")

# ---- Population Type Trends PAGE ---- #
elif selected_tab == "Population Type Trends":
    st.subheader("📈 Population Type Trends")

    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)

    filtered_df = df[df['Year'].isin(selected_years) & df['Population Type'].isin(selected_pop_types)]

    st.markdown("### 📉 Population Type Trends Over Time")
    trend_data = filtered_df.groupby(['Year', 'Population Type'])['Total'].sum().reset_index()
    fig_trends = px.line(trend_data, x='Year', y='Total', color='Population Type',
                         title="Population Type Trends Over Time", markers=True)
    st.plotly_chart(fig_trends, use_container_width=True)

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

# ---- Deep Dive Explorer PAGE ---- #
elif selected_tab == "Deep Dive Explorer":
    st.subheader("🔍 Deep Dive Explorer")

    # --- Filters --- #
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    locations = sorted(df['location'].dropna().unique())

    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)
    selected_locations = st.sidebar.multiselect("Select Location(s)", locations, default=locations[:10])

    filtered_df = df[
        (df['Year'].isin(selected_years)) &
        (df['Population Type'].isin(selected_pop_types)) &
        (df['location'].isin(selected_locations))
    ]

    st.markdown("### 📌 Summary Statistics")
    st.write(f"**Total Records:** {len(filtered_df)}")
    st.write(f"**Total Population:** {filtered_df['Total'].sum():,}")

    # --- Chart: Population Over Time --- #
    st.markdown("### 📈 Population Trends Over Time")
    trend_data = filtered_df.groupby(["Year", "Population Type"])["Total"].sum().reset_index()
    fig = px.line(trend_data, x="Year", y="Total", color="Population Type", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- Chart: Top 10 Locations by Total Population --- #
    st.markdown("### 🗺️ Top Locations by Population")
    top_locs = filtered_df.groupby("location")["Total"].sum().nlargest(10).reset_index()
    fig_bar = px.bar(top_locs, x="Total", y="location", orientation="h", title="Top 10 Locations")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Gender Breakdown Pie --- #
    st.markdown("### 👤 Gender Breakdown")
    total_male = filtered_df[[col for col in df.columns if col.startswith("Male")]].sum().sum()
    total_female = filtered_df[[col for col in df.columns if col.startswith("Female")]].sum().sum()
    pie_df = pd.DataFrame({
        "Gender": ["Male", "Female"],
        "Total": [total_male, total_female]
    })
    fig_pie = px.pie(pie_df, names="Gender", values="Total", title="Gender Distribution")
    st.plotly_chart(fig_pie, use_container_width=True)

