import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("revised_demographics_residing_lka.csv")

st.set_page_config(layout="wide", page_title="Sri Lanka Population Dashboard")

# Sidebar navigation with buttons
st.sidebar.title("📊 Navigation")
tabs = ["Overview", "Geographic Distribution", "Demographics", "Population Type Trends", "Deep Dive Explorer"]

# Create large clickable buttons for navigation
button_style = """
    <style>
        .css-1lsmgbg { font-size: 20px; padding: 18px 40px; margin: 12px 0; background-color: #99c2e6; border-radius: 8px; }
        .css-1lsmgbg:hover { background-color: #005c99; color: white; }
        .block-container { padding: 1rem 2rem; }
        .sidebar .css-1d391kg { position: absolute; top: 0; }
        .sidebar .css-1d391kg h1 { color: #005c99; font-size: 24px; }
        .css-1a3yfiq { width: 100%; }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

# Initialize the selected tab with the first tab by default
selected_tab = None

# Create buttons to select the tabs
for tab in tabs:
    if st.sidebar.button(tab, key=tab):
        selected_tab = tab

st.title("🇱🇰 Population Demographics Dashboard - Sri Lanka")

# Common filters
years = sorted(df['Year'].unique())
pop_types = sorted(df['Population Type'].unique())
blue_palette = px.colors.sequential.Blues

# ---- TAB 1: OVERVIEW ---- #
if selected_tab == "Overview":
    st.subheader("Overview & Introduction")

    st.markdown("""
    **Welcome to the Sri Lanka Population Demographics Dashboard.**  
    This dashboard presents a comprehensive overview of displaced and affected populations residing in Sri Lanka, 
    including refugees, asylum seekers, internally displaced persons (IDPs), and other categories. It is designed 
    to support government officials and policymakers in making data-driven decisions related to humanitarian assistance, 
    resource allocation, and long-term planning.

    The data spans from **2001 to the most recent available year**, covering diverse geographic locations and demographic 
    breakdowns such as gender, age, and living conditions (urban/rural). This initial overview provides key statistics 
    and trends to contextualize the overall population landscape.
    """)

    # KPI cards in prominent boxes with enhanced fonts
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

    # Gender pie chart with larger size and enhanced fonts
    gender_df = pd.DataFrame({
        'Gender': ['Female', 'Male'],
        'Count': [female_total, male_total]
    })
    fig_gender = px.pie(gender_df, names='Gender', values='Count', title='Gender Distribution',
                        color_discrete_map={"Female": "#005c99", "Male": "#99c2e6"})
    fig_gender.update_traces(textposition='inside', textinfo='percent+label', textfont_size=18)
    fig_gender.update_layout(height=450, margin=dict(t=30, b=30, l=20, r=20), font=dict(size=16))
    st.plotly_chart(fig_gender, use_container_width=True)

    # Line chart of total population over years
    yearly_totals = df.groupby("Year")['Total'].sum().reset_index()
    fig = px.line(yearly_totals, x="Year", y="Total", title="Total Population Over Time",
                  markers=True, color_discrete_sequence=blue_palette)
    fig.update_layout(height=350, margin=dict(t=30, b=30), font=dict(size=16))
    st.plotly_chart(fig, use_container_width=True)

    # Population by Type over years
    type_by_year = df.groupby(['Year', 'Population Type'])['Total'].sum().reset_index()
    fig2 = px.bar(type_by_year, x='Year', y='Total', color='Population Type', 
                  title='Population by Type Over the Years', barmode='stack',
                  color_discrete_sequence=blue_palette)
    fig2.update_layout(height=400, margin=dict(t=40, b=30), font=dict(size=16))
    st.plotly_chart(fig2, use_container_width=True)

