import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import requests
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Delhi AI Pollution Tracker", page_icon="🌍", layout="wide")

# --- 2. CONSTANTS ---
# Use the URL you provided
DATA_URL = "https://delhipollutiondev9770.blob.core.windows.net/gold/delhi_heatmap.csv"

# --- 3. HELPER: GET DATA FRESHNESS ---
def get_last_updated():
    try:
        # Request only headers (lightweight, doesn't download file)
        response = requests.head(DATA_URL)
        
        # Azure returns time in GMT (e.g., "Fri, 02 Jan 2026 10:00:00 GMT")
        last_modified = response.headers.get('Last-Modified')
        
        if last_modified:
            # Parse and format for a cleaner look
            dt_gmt = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')
            return dt_gmt.strftime("%d %b %Y, %I:%M %p GMT")
            
        return "Unknown"
    except Exception:
        return "Unknown"

# --- 4. HEADER & STATUS ---
# Changed Emoji to Earth 🌍
st.title("🌍 AI Pollution Tracker: Delhi")

# Display Last Updated Time
last_run = get_last_updated()
st.caption(f"✅ **System Status:** Live | 🕒 **Last Updated:** {last_run}")
st.markdown("This map shows **PM2.5 predictions** based on live weather patterns using **XGBoost on Azure**.")

# --- 5. LOAD DATA ---
@st.cache_data(ttl=3600)
def load_data():
    try:
        return pd.read_csv(DATA_URL)
    except Exception as e:
        st.error(f"Could not read data. Ensure the container is Public 'Blob' access. Error: {e}")
        return pd.DataFrame()

df = load_data()

# --- 6. MAP & METRICS ---
if not df.empty:
    # A. Metrics
    col1, col2, col3 = st.columns(3)
    avg_pm = int(df['predicted_pm25'].mean())
    max_pm = int(df['predicted_pm25'].max())
    
    col1.metric("Average PM2.5", f"{avg_pm}", "µg/m³")
    col2.metric("Highest Pollution Spot", f"{max_pm}", "Severe")
    col3.metric("Locations Tracked", f"{len(df)}")

    # B. Map Generation
    m = folium.Map(location=[28.61, 77.23], zoom_start=10, tiles='CartoDB positron')
    
    # Layer 1: Heatmap (Background)
    heat_data = df[['latitude', 'longitude', 'predicted_pm25']].values.tolist()
    HeatMap(heat_data, radius=25, blur=20, gradient={0.4: 'green', 0.65: 'orange', 1: 'red'}).add_to(m)

    # Layer 2: Circle Markers (Foreground Details)
    for _, row in df.iterrows():
        val = row['predicted_pm25']
        # Color Logic
        color = "green" if val <= 50 else "orange" if val <= 200 else "red"
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6, 
            color=color, 
            fill=True, 
            fill_opacity=0.8,
            tooltip=f"PM2.5: {int(val)}"
        ).add_to(m)

    st_folium(m, width=1200, height=500)

else:
    st.warning("Waiting for data connection...")