import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="Campus Growth Portal",
    page_icon="📈",
    layout="wide"
)

# --- Title and Header ---
st.title("📈 Campus Growth Portal")
st.markdown("A Mission Control dashboard for the University Ambassador Program.")

# --- Helper Function to Generate Fake Data ---
@st.cache_data
def generate_data():
    """Generates realistic fake data for the dashboard."""
    universities = [
        "University of Southern California", "University of Texas at Austin", "New York University",
        "University of Florida", "Ohio State University", "University of Michigan",
        "Arizona State University", "University of Washington", "Penn State University",
        "University of Colorado Boulder"
    ]
    
    first_names = ["Jessica", "David", "Maria", "John", "Sarah", "Michael", "Emily", "Chris", "Laura", "James"]
    last_names = ["Miller", "Chen", "Garcia", "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Wilson"]
    
    # Create Reps DataFrame
    num_reps = 50
    rep_data = {
        "rep_name": [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_reps)],
        "university": np.random.choice(universities, num_reps),
        "signups_last_30d": np.random.randint(5, 100, num_reps),
        "events_created_last_30d": np.random.randint(0, 15, num_reps),
    }
    reps_df = pd.DataFrame(rep_data)

    # Create Campus Leaderboard from Reps data
    campus_df = reps_df.groupby("university").agg(
        num_reps=('rep_name', 'count'),
        signups_last_30d=('signups_last_30d', 'sum'),
        events_created_last_30d=('events_created_last_30d', 'sum')
    ).reset_index()
    # Generate realistic percentage numbers for growth
    campus_df['growth_mom'] = np.random.uniform(-10.0, 25.0, len(campus_df))
    campus_df = campus_df.sort_values("signups_last_30d", ascending=False)
    
    # Create Activity Log
    activities = [
        "just onboarded a new organization:", "created a new event:", "hit their monthly sign-up bonus!",
        "scheduled a demo with the student government:", "is leading a workshop on event planning."
    ]
    onboarded_orgs = ["Sigma Alpha Mu", "Women in CS", "The Marketing Club", "Delta Gamma", "Engineering Student Council"]
    activity_log = []
    for _ in range(10):
        rep_name = np.random.choice(reps_df['rep_name'])
        university = np.random.choice(reps_df['university'])
        activity = np.random.choice(activities)
        
        log_entry = f"- {rep_name} ({university}) {activity}"
        if "onboarded" in activity:
            log_entry += f" {np.random.choice(onboarded_orgs)}"
        
        activity_log.append(log_entry)

    # Create Funnel Data
    funnel_data = {
        'stage': ["Orgs Identified", "Orgs Contacted", "Demos Scheduled", "Orgs Onboarded"],
        'value': [1200, 650, 150, 75]
    }

    # Create Map Data
    map_data = {
        'university': universities,
        'lat': [34.0224, 30.2849, 40.7295, 29.6436, 40.0067, 42.2780, 33.4242, 47.6553, 40.7982, 40.0076],
        'lon': [-118.2851, -97.7341, -73.9965, -82.3488, -83.0143, -83.7382, -111.9392, -122.3035, -77.8599, -105.2631],
    }
    map_df = pd.DataFrame(map_data).merge(campus_df[['university', 'signups_last_30d']], on='university', how='left').fillna(0)

    return reps_df, campus_df, activity_log, funnel_data, map_df

# --- Call the function to create all the necessary variables ---
reps_df, campus_df, activity_log, funnel_data, map_df = generate_data()

# --- National Performance Overview (KPI Cards) ---
st.subheader("National Performance Overview")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_reps = campus_df['num_reps'].sum()
total_signups = campus_df['signups_last_30d'].sum()
total_events = campus_df['events_created_last_30d'].sum()
top_campus = campus_df.iloc[0]['university']

kpi1.metric(label="Total Reps", value=f"{total_reps}")
kpi2.metric(label="Sign-ups (Last 30d)", value=f"{total_signups:,}")
kpi3.metric(label="Events Created (Last 30d)", value=f"{total_events}")
kpi4.metric(label="Top Performing Campus", value=top_campus)

st.markdown("---")

# --- Main Dashboard Layout (Leaderboards, Funnel, Map) ---
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("Campus Leaderboard")
    st.dataframe(
        campus_df,
        column_config={
            "university": "University",
            "num_reps": "Reps",
            "signups_last_30d": "Sign-ups (30d)",
            "events_created_last_30d": "Events (30d)",
            "growth_mom": st.column_config.ProgressColumn(
                "Growth (MoM)", format="%.1f%%", min_value=-25, max_value=25
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top Reps (by Sign-ups)")
    top_reps_df = reps_df.sort_values("signups_last_30d", ascending=False).head(5)
    st.dataframe(
        top_reps_df,
        column_config={
            "rep_name": "Representative",
            "university": "University",
            "signups_last_30d": "Sign-ups (30d)",
            "events_created_last_30d": "Events Created",
        },
        use_container_width=True,
        hide_index=True,
    )

with col2:
    st.subheader("Outreach & Onboarding Funnel")
    funnel_fig = px.funnel(funnel_data, x='value', y='stage')
    funnel_fig.update_layout(
        showlegend=False, 
        yaxis_title=None, 
        xaxis_title=None,
        margin=dict(l=0, r=0, t=20, b=0)
    )
    st.plotly_chart(funnel_fig, use_container_width=True)

    st.subheader("Rep Activity Log")
    st.container(height=280, border=True).markdown("\n".join(activity_log))

st.markdown("---")

# --- Interactive Map View ---
st.subheader("Program Footprint")

fig = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    size="signups_last_30d",
    hover_name="university",
    hover_data={
        "signups_last_30d": True,
        "lat": False,
        "lon": False,
    },
    color_discrete_sequence=["#FF4B4B"],
    zoom=3,
    height=500
)

fig.update_layout(
    mapbox_style="carto-positron",
    margin={"r":0,"t":0,"l":0,"b":0}
)

st.plotly_chart(fig, use_container_width=True)
st.caption("Hover over a dot to see university details. Dot size represents sign-ups in the last 30 days.")
