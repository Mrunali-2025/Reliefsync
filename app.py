import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
from classifier import classify_message
from extractor import extract_info

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="ReliefSync Pro", layout="wide", page_icon="🆘")

# --- 2. THEME & STYLING ---
st.markdown("""
    <style>
    /* Background Gradient */
    .stApp {
        background-color: #94a3b8; 
        background-image: linear-gradient(315deg, #94a3b8 0%, #cbd5e1 74%);
    }
    
    /* SOS Icon Styling */
    .sos-icon {
        background-color: #ff4b6b;
        color: white;
        padding: 4px 10px;
        border-radius: 8px;
        font-weight: 900;
        font-size: 24px;
        display: inline-block;
        vertical-align: middle;
        margin-right: 10px;
    }

    /* Main Title Styling */
    .title-text {
        color: #1e293b;
        font-size: 36px;
        font-weight: 700;
        display: inline-block;
        vertical-align: middle;
    }

    /* Subtitle Styling */
    .subtitle-text {
        color: #334155;
        font-size: 14px;
        margin-top: 15px;
        margin-bottom: 25px;
    }

    /* Updated Custom Metric Styling (Fixed Spacing) */
    .metric-label {
        color: #475569;
        font-size: 14px;
        margin-bottom: 5px; /* Added space between label and value */
        display: block;
    }
    .metric-value {
        color: #1e293b;
        font-size: 36px; /* Slightly larger */
        font-weight: 700;
        margin-top: 0px;
        line-height: 1;
    }

    /* Action Buttons */
    .stButton>button {
        background-color: #1e293b;
        color: white;
        border-radius: 8px;
        width: 100%;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE INITIALIZATION ---
if 'database' not in st.session_state:
    st.session_state.database = []

# --- 4. VERIFIED HELP CENTERS ---
HELP_CENTERS = [
    {"Name": "City Medical Center", "Type": "Medical", "Lat": 19.0760, "Lon": 72.8777},
    {"Name": "Red Cross Food Bank", "Type": "Food/Water", "Lat": 19.1200, "Lon": 72.9000},
    {"Name": "Civic Emergency Shelter", "Type": "Shelter", "Lat": 19.0500, "Lon": 72.8200}
]

# --- 5. SIDEBAR: UNIVERSAL TRANSLATOR ---
st.sidebar.title("🌍 Global Translator")
st.sidebar.write("Translate any crisis signal to English.")
quick_text = st.sidebar.text_area("Paste foreign text here:", height=100)
if st.sidebar.button("Translate Now"):
    if quick_text:
            with st.spinner("AI Translating..."):
                res = extract_info(quick_text)
            st.sidebar.markdown(f"**Original Language:** {res['language']}")
            st.sidebar.success(f"**English:** {res['translation']}")

# --- 6. TOP HEADER & METRICS (Matches your picture) ---
df = pd.DataFrame(st.session_state.database)

# Custom Header
st.markdown(f"""
    <div>
        <span class="sos-icon">SOS</span>
        <span class="title-text">ReliefSync: Resource Detector</span>
    </div>
    <div class="subtitle-text">AI-Powered Emergency Resource Mapping & Intelligence</div>
""", unsafe_allow_html=True)

# Custom Metrics Layout
total_signals = len(df)
critical_count = len(df[df['urgency'] > 7]) if not df.empty else 0

m1, m2, m3 = st.columns(3) # Adjusted widths

with m1:
    st.markdown(f'<p class="metric-label">Total Requests</p><p class="metric-value">{total_signals}</p>', unsafe_allow_html=True)

with m2:
    st.markdown(f'<p class="metric-label">Critical Priority</p><p class="metric-value">{critical_count}</p>', unsafe_allow_html=True)

with m3:
    st.markdown(f'''
        <p class="metric-label">System Status</p>
        <p class="metric-value">Live ✅</p>
    ''', unsafe_allow_html=True)

st.divider()

# --- 7. INPUT SECTION ---
st.subheader("📥 Ingest Emergency Signal")
col_in, col_btn = st.columns([4, 1])
with col_in:
    user_input = st.text_input("", placeholder="e.g., 'Need Oxygen Cylinder at City Hospital. Call 9988776655'...")
with col_btn:
    st.write("##") 
    if st.button("🚀 DEPLOY AI"):
        if user_input:
            with st.spinner("Analyzing..."):
                cat = classify_message(user_input)
                if "oxygen" in user_input.lower():
                    cat = "Medical"
                
                if cat == "Noise":
                    st.toast("Message filtered as non-emergency chatter.")
                else:
                    details = extract_info(user_input)
                    
                    if cat == "Medical": 
                        center = HELP_CENTERS[0]['Name']
                    elif cat == "Shelter": 
                        center = HELP_CENTERS[2]['Name']
                    else: 
                        center = HELP_CENTERS[1]['Name']
                    
                    new_entry = {
                        "Category": cat,
                        "item": details.get("item", "Check Original"),
                        "location": details.get("location", "Detected in text"),
                        "contact": details.get("contact", "N/A"),
                        "urgency": int(details.get("urgency", 5)),
                        "language": details.get("language", "Detected"), 
                        "translation": details.get("translation", user_input),
                        "Original": user_input,
                        "Nearest Center": center,
                        "Dispatched": False,
                        "lat": 19.0760 + random.uniform(-0.06, 0.06),
                        "lon": 72.8777 + random.uniform(-0.06, 0.06)
                    }
                    if "oxygen" in user_input.lower() or "blood" in user_input.lower():
                        new_entry['urgency'] = 10
                    
                    st.session_state.database.append(new_entry)
                    st.rerun()

# --- 8. MAP & DISPATCH QUEUE ---
if not df.empty:
    col_map, col_queue = st.columns([1.5, 1])

    with col_map:
        st.subheader("📍 Geospatial Distribution")
        m = folium.Map(location=[19.0760, 72.8777], zoom_start=11)
        for hc in HELP_CENTERS:
            folium.Marker([hc['Lat'], hc['Lon']], popup=hc['Name'], 
                          icon=folium.Icon(color='blue', icon='plus-sign')).add_to(m)
        for idx, req in df.iterrows():
            folium.Marker(
                [req['lat'], req['lon']], 
                popup=f"NEED: {req['item']}", 
                icon=folium.Icon(color='red' if req['urgency'] > 7 else 'orange', icon='exclamation-sign')
            ).add_to(m)
        st_folium(m, width="100%", height=450)

    with col_queue:
        st.subheader("⚡ Live Dispatch Queue")
        st.data_editor(
            df[['Dispatched', 'item', 'urgency', 'Nearest Center']],
            column_config={
                "Dispatched": st.column_config.CheckboxColumn("Sent?", default=False),
                "urgency": st.column_config.ProgressColumn("Urgency", min_value=1, max_value=10),
            },
            disabled=["item", "urgency", "Nearest Center"],
            hide_index=True,
            use_container_width=True
        )

    # --- 9. MASTER LOG ---
    st.divider()
    st.subheader("📋 Crisis Master Log")
    st.dataframe(
        df[['Category', 'language','item', 'location', 'contact', 'Nearest Center', 'translation', 'Original']], 
        use_container_width=True
    )
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export Dispatch Data (CSV)", csv, "relief_data.csv", "text/csv")

else:
    st.info("Awaiting incoming crisis signals...")