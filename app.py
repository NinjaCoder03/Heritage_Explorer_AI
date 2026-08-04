import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import streamlit as st
import google.generativeai as genai
from PIL import Image
import folium
from streamlit_folium import st_folium
import re

# 1. Setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Heritage Storyteller & Navigator", layout="wide")
st.title("🏛️ Heritage Storyteller & Navigator")

# Initialize Session State to prevent re-loading
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "story_text" not in st.session_state:
    st.session_state.story_text = ""
if "coords" not in st.session_state:
    st.session_state.coords = []

# Input Section
img_file = st.file_uploader("Upload Monument Photo", type=['jpg', 'png', 'jpeg'])

# If a new file is uploaded, reset the state to allow fresh analysis
if img_file and st.button("Analyze Image"):
    st.session_state.analysis_done = False 

if img_file:
    img = Image.open(img_file)
    st.image(img, width=400)
    
    # ONLY run this if it hasn't been done yet
    if not st.session_state.analysis_done:
        with st.spinner('Storyteller is analyzing the heritage site...'):
            prompt = """
            Act as a professional English Heritage Guide and Storyteller.
            1. Identify this monument and tell its historical story in 3 engaging paragraphs in English.
            2. Recommend 5 other MUST-VISIT heritage sites within an 800-1000km radius.
            3. Provide exact coordinates for ALL 6 locations (Main + 5 Nearby) in this specific format:
            MAP_START
            [Lat1, Lon1]
            [Lat2, Lon2]
            [Lat3, Lon3]
            [Lat4, Lon4]
            [Lat5, Lon5]
            [Lat6, Lon6]
            MAP_END
            """
            try:
                response = model.generate_content([prompt, img])
                st.session_state.story_text = response.text.split("MAP_START")[0]
                
                coord_pattern = r"\[\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*\]"
                found_coords = re.findall(coord_pattern, response.text)
                st.session_state.coords = [[float(c[0]), float(c[1])] for c in found_coords]
                
                st.session_state.analysis_done = True # Mark as complete!
            except Exception as e:
                st.error(f"Error: {e}")

    # Display results from Session State (No re-loading!)
    if st.session_state.analysis_done:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("📜 The Legend (English Edition):")
            st.write(st.session_state.story_text)

        with col2:
            if st.session_state.coords:
                st.subheader("📍 Your 1000km Heritage Route")
                m = folium.Map(location=st.session_state.coords[0], zoom_start=5)
                for i, coord in enumerate(st.session_state.coords):
                    label = "Current Site" if i == 0 else f"Stop {i}"
                    folium.Marker(location=coord, popup=label).add_to(m)
                
                st_folium(m, width=600, height=450, key="heritage_map")

                # Navigation Link
                c = st.session_state.coords
                dest = f"{c[-1][0]},{c[-1][1]}"
                waypts = "|".join([f"{coord[0]},{coord[1]}" for coord in c[:-1]])
                nav_url = f"https://www.google.com/maps/dir/?api=1&origin={c[0][0]},{c[0][1]}&destination={dest}&waypoints={waypts}&travelmode=driving"
                st.link_button("🚀 Launch Real-Time Navigation", nav_url)

st.divider()
st.caption("HeritageAI | Session Optimized for Hackathon")