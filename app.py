import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster, HeatMap
import streamlit.components.v1 as components
from PIL import Image
import math
from streamlit_folium import st_folium


st.set_page_config(layout="wide")
df = pd.read_csv("revised_demographics_residing_lka.csv")


import streamlit as st
from PIL import Image

header = Image.open("cover.jpeg")
st.image(header, width=250)  # Ultra-compact 250px width


# Load and standardize data
@st.cache_data
def load_data():
    df = pd.read_csv("revised_demographics_residing_lka.csv")
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

df = load_data()

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
                Total Population Records<br><span style="font-size: 30px;">{df['total'].sum():,}</span>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="padding: 20px; background-color: #f0f0f5; border-radius: 10px; font-size: 20px; 
                        font-weight: bold; text-align: center; color: #005c99; height: 150px;">
                Unique Population Types<br><span style="font-size: 30px;">{df['population_type'].nunique()}</span>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        male_total = df[[col for col in df.columns if col.startswith("male_")]].sum().sum()
        female_total = df[[col for col in df.columns if col.startswith("female_")]].sum().sum()
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
# Read and clean DataFrame
df = pd.read_csv("revised_demographics_residing_lka.csv")

df.columns = df.columns.str.strip()
if selected_tab == "Geographic Distribution":
    st.subheader("🌍 Geographic Distribution")

    # Sidebar filters
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)

    # Filter data
    filtered_df = df[df['Year'].isin(selected_years) & df['Population Type'].isin(selected_pop_types)]

    # Clean location names
    filtered_df['clean_location'] = filtered_df['location'].str.replace(r'\s*:\s*\w+', '', regex=True)
    location_data = filtered_df.groupby('clean_location')['Total'].sum().reset_index()

    # Sri Lanka coordinates mapping
    location_coords = {
        "Colombo": (6.9271, 79.8612),
        "Kandy": (7.2906, 80.6337),
        "Galle": (6.0535, 80.2210),
        "Jaffna": (9.6615, 80.0255),
        "Trincomalee": (8.5925, 81.1870),
        "Anuradhapura": (8.3114, 80.4037),
        "Matara": (5.9483, 80.5353),
        "Batticaloa": (7.7167, 81.7000),
        "Ratnapura": (6.6847, 80.4036),
        "Ampara": (7.2833, 81.6667),
        "Badulla": (6.9895, 81.0557),
        "Gampaha": (7.0917, 79.9997),
        "Hambantota": (6.1236, 81.1233),
        "Kalutara": (6.5833, 79.9594),
        "Kegalle": (7.2533, 80.3436),
        "Kilinochchi": (9.3833, 80.4000),
        "Kurunegala": (7.4867, 80.3647),
        "Mannar": (8.9667, 79.8833),
        "Matale": (7.4717, 80.6244),
        "Mullaitivu": (9.2667, 80.8167),
        "Polonnaruwa": (7.9333, 81.0000),
        "Puttalam": (8.0333, 79.8167),
        "Vavuniya": (8.7500, 80.5000),
        "Dispersed in the country / territory": (7.8731, 80.7718),
        "Other": (7.8731, 80.7718),
    }

    # Create tabs
    map_tab, heatmap_tab = st.tabs(["Point Map", "Heatmap"])

    with map_tab:
        st.markdown("### 📍 Population Distribution by Location")
        m = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB positron")

        for idx, row in location_data.iterrows():
            location = row['clean_location']
            population = row['Total']
            lat, lon = location_coords.get(location, (7.8731, 80.7718))

            folium.CircleMarker(
                location=[lat, lon],
                radius=3 + (population / 100000),
                popup=f"{location}<br>Population: {population:,}",
                color='#3186cc',
                fill=True,
                fill_color='#3186cc',
                fill_opacity=0.6,
                weight=1
            ).add_to(m)

        st_folium(m, width=700, height=500)

    with heatmap_tab:
        st.markdown("### 🔥 Population Density Heatmap")
        hm = folium.Map(location=[7.8731, 80.7718], zoom_start=7, tiles="CartoDB dark_matter")

        heat_data = []
        for idx, row in location_data.iterrows():
            location = row['clean_location']
            population = row['Total']
            lat, lon = location_coords.get(location, (7.8731, 80.7718))
            heat_data.append([lat, lon, min(population, 50000)])

        HeatMap(heat_data, radius=15, blur=10).add_to(hm)
        st_folium(hm, width=700, height=500)

    st.markdown("### 📊 Top 10 Locations by Total Population")
    bar_data = filtered_df.groupby(['location', 'Population Type'])['Total'].sum().reset_index()
    top_locations = bar_data.groupby('location')['Total'].sum().nlargest(10).index
    bar_data_top = bar_data[bar_data['location'].isin(top_locations)]

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

    # Changed to multiselect
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=[years[-1]])
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=[population_types[0]])

    # Filtered data
    demo_df = df[(df['Year'].isin(selected_years)) & (df['Population Type'].isin(selected_pop_types))]

    # --- Radio Buttons for Pie Charts --- #
    st.markdown("### 👤 Gender & Age Distribution Overview")
    chart_mode = st.radio("Choose View", ["Overall Gender Distribution", "Male Age Categories", "Female Age Categories"], horizontal=True)

    # Preprocess counts
    male_cols = [col for col in df.columns if col.startswith("Male ") and col != "Male Total"]
    female_cols = [col for col in df.columns if col.startswith("Female ") and col != "Female Total"]
    total_male = demo_df[male_cols].sum().sum()
    total_female = demo_df[female_cols].sum().sum()

    # 1. Overall Gender Distribution
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

    # 2. Male Age Categories
    elif chart_mode == "Male Age Categories":
        male_age_data = demo_df[male_cols].sum().reset_index()
        male_age_data.columns = ["Age Group", "Count"]
        male_age_data["Age Group"] = male_age_data["Age Group"].str.replace("Male ", "")
        fig = px.pie(male_age_data, names="Age Group", values="Count", title="Male Age Distribution",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=16, textfont_color='white', textfont_family='Arial')
        st.plotly_chart(fig, use_container_width=True)

    # 3. Female Age Categories
    elif chart_mode == "Female Age Categories":
        female_age_data = demo_df[female_cols].sum().reset_index()
        female_age_data.columns = ["Age Group", "Count"]
        female_age_data["Age Group"] = female_age_data["Age Group"].str.replace("Female ", "")
        fig = px.pie(female_age_data, names="Age Group", values="Count", title="Female Age Distribution",
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          textfont_size=16, textfont_color='white', textfont_family='Arial')
        st.plotly_chart(fig, use_container_width=True)

    # --- Stacked Bar Chart --- #
    st.markdown("### 📊 Stacked Bar Chart: Population by Age & Gender")

    # Combine male and female by age group
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

    # --- Gender and Population Type Relationship --- #
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
    
    # Sidebar filters
    years = sorted(df['Year'].unique())
    population_types = sorted(df['Population Type'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)
    selected_pop_types = st.sidebar.multiselect("Select Population Type(s)", population_types, default=population_types)
    
    # Filter data
    filtered_df = df[df['Year'].isin(selected_years) & df['Population Type'].isin(selected_pop_types)]
    
    # Create tabs for organized viewing
    tab1, tab2, tab3 = st.tabs(["Trend Analysis", "Composition", "Advanced Metrics"])
    
    with tab1:
        # 1. Main Trend Lines with Annotations
        st.markdown("### 📊 Population Type Trends Over Time")
        trend_data = filtered_df.groupby(['Year', 'Population Type'])['Total'].sum().reset_index()
        
        fig = px.line(trend_data, x='Year', y='Total', color='Population Type',
                     title="Population Trends with Peak/Valley Annotations",
                     markers=True,
                     template='plotly_white')
        
        # Add peak/valley annotations
        for pop_type in trend_data['Population Type'].unique():
            subset = trend_data[trend_data['Population Type'] == pop_type]
            peak = subset.loc[subset['Total'].idxmax()]
            valley = subset.loc[subset['Total'].idxmin()]
            
            fig.add_annotation(x=peak['Year'], y=peak['Total'],
                             text=f"Peak: {int(peak['Total']):,}",
                             showarrow=True, arrowhead=1)
            
            fig.add_annotation(x=valley['Year'], y=valley['Total'],
                             text=f"Low: {int(valley['Total']):,}",
                             showarrow=True, arrowhead=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 2. Small Multiples Trend View
        st.markdown("### 🔍 Individual Trend Lines")
        fig_small = px.line(trend_data, x='Year', y='Total', facet_col='Population Type',
                          facet_col_wrap=3, height=600)
        st.plotly_chart(fig_small, use_container_width=True)
    
    with tab2:
        # 3. Stacked Area Composition Chart
        st.markdown("### 🧩 Population Composition Over Time")
        fig_area = px.area(trend_data, x='Year', y='Total', color='Population Type',
                          title="Relative Composition of Population Types")
        st.plotly_chart(fig_area, use_container_width=True)
        
        # 4. Percentage Composition Heatmap
        st.markdown("### 🔢 Percentage Composition Heatmap")
        pivot_data = trend_data.pivot(index='Year', columns='Population Type', values='Total')
        percent_data = pivot_data.div(pivot_data.sum(axis=1), axis=0) * 100
        
        fig_heat = px.imshow(percent_data.T, 
                            labels=dict(x="Year", y="Population Type", color="Percentage"),
                            text_auto=".1f",
                            aspect="auto",
                            color_continuous_scale='Blues')
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with tab3:
        # 5. Growth Rate Analysis
        st.markdown("### 📈 Annual Growth Rates")
        yoy_data = trend_data.copy()
        yoy_data['YoY Change'] = yoy_data.groupby('Population Type')['Total'].pct_change() * 100
        
        fig_growth = px.bar(yoy_data, x='Year', y='YoY Change', color='Population Type',
                           barmode='group',
                           title="Year-over-Year Growth Rates",
                           labels={'YoY Change': 'Percentage Change (%)'})
        fig_growth.add_hline(y=0, line_dash="dash")
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # 6. Statistical Summary
        st.markdown("### 📊 Statistical Summary")
        stats = trend_data.groupby('Population Type')['Total'].agg(
            ['mean', 'median', 'std', 'min', 'max']
        ).reset_index()
        
        # Add CAGR calculation
        def calculate_cagr(group):
            if len(group) > 1:
                start = group.iloc[0]['Total']
                end = group.iloc[-1]['Total']
                years = len(group) - 1
                return ((end/start)**(1/years) - 1) * 100
            return 0
        
        cagr = trend_data.groupby('Population Type').apply(calculate_cagr)
        stats['CAGR (%)'] = stats['Population Type'].map(cagr)
        
        st.dataframe(stats.style.format({
            'mean': '{:,.0f}',
            'median': '{:,.0f}',
            'std': '{:,.1f}',
            'min': '{:,.0f}',
            'max': '{:,.0f}',
            'CAGR (%)': '{:.1f}%'
        }))



# ---- Deep Dive Explorer PAGE ---- #
elif selected_tab == "Deep Dive Explorer":
    st.title("🔍 Deep-Dive Explorer")
    st.markdown("Apply filters to explore population data in detail. Insights are useful for targeted government decision-making.")

    # Sub-tabs inside Deep Dive
    deep_dive_tabs = st.tabs(["Filters & Visuals", "Summary Stats", "Subgroup Comparison", "Data Table"])

    # --- TAB 1: Filters & Visuals --- #
    with deep_dive_tabs[0]:
        st.header("📊 Interactive Visuals")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            selected_year = st.selectbox("Year", ["All"] + sorted(df["Year"].dropna().unique()))
        with col2:
            selected_gender = st.selectbox("Gender", ["All", "Male", "Female"])
        with col3:
            selected_urban_rural = st.selectbox("Urban/Rural", ["All"] + sorted(df["urbanRural"].dropna().unique()))
        with col4:
            selected_pop_type = st.selectbox("Population Type", ["All"] + sorted(df["Population Type"].dropna().unique()))

        selected_location = st.multiselect("Location", options=sorted(df["location"].dropna().unique()), default=None)

        # Apply filters
        filtered_df = df.copy()
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df["Year"] == selected_year]
        if selected_gender != "All":
            gender_col = "Female Total" if selected_gender == "Female" else "Male Total"
            filtered_df = filtered_df[filtered_df[gender_col] > 0]
        if selected_urban_rural != "All":
            filtered_df = filtered_df[filtered_df["urbanRural"] == selected_urban_rural]
        if selected_pop_type != "All":
            filtered_df = filtered_df[filtered_df["Population Type"] == selected_pop_type]
        if selected_location:
            filtered_df = filtered_df[filtered_df["location"].isin(selected_location)]

        # KPI: Total matching population
        total_pop = filtered_df["Total"].sum()
        st.metric("Total Matching Population", f"{int(total_pop):,}")

        # Visual: Bar Chart
        chart_type = st.radio("Choose Chart Type", ["Bar Chart", "Line Chart"])
        group_by_col = st.selectbox("Group By", ["Year", "location", "Population Type", "urbanRural"])

        if chart_type == "Bar Chart":
            bar_df = filtered_df.groupby(group_by_col)["Total"].sum().reset_index()
            fig = px.bar(bar_df, x=group_by_col, y="Total", title="Total Population by " + group_by_col)
            st.plotly_chart(fig, use_container_width=True)
        else:
            line_df = filtered_df.groupby(["Year", group_by_col])["Total"].sum().reset_index()
            fig = px.line(line_df, x="Year", y="Total", color=group_by_col, markers=True,
                        title="Population Trend by " + group_by_col)
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: Summary Stats --- #
    with deep_dive_tabs[1]:
        st.header("📈 Summary Statistics")
        st.markdown("Breakdown of key metrics by category.")
        summary = df.groupby("Population Type")["Total"].agg(["sum", "mean", "max", "min"]).reset_index()
        st.dataframe(summary.style.format({"sum": "{:,}", "mean": "{:.0f}", "max": "{:,}", "min": "{:,}"}))

    # --- TAB 3: Subgroup Comparison --- #
    with deep_dive_tabs[2]:
        st.header("🔍 Subgroup Comparison")
        st.markdown("Compare two filters side by side.")
        compare_col1 = st.selectbox("First Category", ["urbanRural", "location", "Population Type"])
        compare_col2 = st.selectbox("Second Category", ["Year", "Population Type", "location"])

        comparison = df.groupby([compare_col1, compare_col2])["Total"].sum().reset_index()
        fig = px.bar(comparison, x=compare_col1, y="Total", color=compare_col2, barmode="group",
                    title=f"Population by {compare_col1} and {compare_col2}")
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 4: Data Table --- #
    with deep_dive_tabs[3]:
        st.header("📋 Filtered Data Table")
        st.dataframe(filtered_df)
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", data=csv, file_name="filtered_population_data.csv", mime="text/csv")

