import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

# 1. Page Config
st.set_page_config(page_title="Delhi AI Pollution Tracker", page_icon="😷", layout="wide")

st.title("😷 AI Pollution Tracker: Delhi")
st.markdown("This map shows **PM2.5 predictions** based on live weather patterns using **XGBoost on Azure**.")

# 2. Load Data (Keyless / Public URL)
@st.cache_data(ttl=3600) # Cache for 1 hour to save bandwidth
def load_data():
    # REPLACE THIS URL with your actual file URL from Azure
    # Format: https://<storage_account_name>.blob.core.windows.net/<container>/<file.csv>
    DATA_URL = "https://delhipollutiondev9770.blob.core.windows.net/gold/delhi_heatmap.csv"
    
    try:
        # Pandas can read directly from a URL!
        return pd.read_csv(DATA_URL)
    except Exception as e:
        st.error(f"Could not read data. Ensure the container is Public 'Blob' access. Error: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # 3. Metrics
    col1, col2, col3 = st.columns(3)
    avg_pm = int(df['predicted_pm25'].mean())
    max_pm = int(df['predicted_pm25'].max())
    
    col1.metric("Average PM2.5", f"{avg_pm}", "µg/m³")
    col2.metric("Highest Pollution Spot", f"{max_pm}", "Severe")
    col3.metric("Locations Tracked", f"{len(df)}")

    # 4. Map
    m = folium.Map(location=[28.61, 77.23], zoom_start=10, tiles='CartoDB positron')
    
    heat_data = df[['latitude', 'longitude', 'predicted_pm25']].values.tolist()
    HeatMap(heat_data, radius=25, blur=20, gradient={0.4: 'green', 0.65: 'orange', 1: 'red'}).add_to(m)

    for _, row in df.iterrows():
        val = row['predicted_pm25']
        color = "green" if val <= 50 else "orange" if val <= 200 else "red"
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=6, color=color, fill=True, fill_opacity=0.8,
            tooltip=f"PM2.5: {int(val)}"
        ).add_to(m)

    st_folium(m, width=1200, height=500)

else:
    st.warning("Waiting for data connection...")