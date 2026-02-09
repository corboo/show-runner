#!/usr/bin/env python3
"""
🎬 THE SHOW RUNNER
AI-powered show production for QP-1 / Inception Point AI

Create shows like AI House with character voices, AI video, and multi-platform output.
"""

import streamlit as st
from pathlib import Path
import json
import os

# Page config
st.set_page_config(
    page_title="The Show Runner",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
CHARACTERS_DIR = APP_DIR / "characters"
OUTPUTS_DIR = APP_DIR / "outputs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CHARACTERS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Load or initialize data
def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Initialize session state
if "characters" not in st.session_state:
    st.session_state.characters = load_json(DATA_DIR / "characters.json", {})

if "shows" not in st.session_state:
    st.session_state.shows = load_json(DATA_DIR / "shows.json", {})

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/clapperboard.png", width=60)
    st.title("🎬 The Show Runner")
    st.caption("AI Show Production System")
    
    st.divider()
    
    # Quick stats
    st.metric("Characters", len(st.session_state.characters))
    st.metric("Shows", len(st.session_state.shows))
    
    st.divider()
    
    st.caption("Built by Inception Point AI ⚡")

# Main content
st.title("🎬 The Show Runner")
st.markdown("### AI-Powered Show Production")

st.markdown("""
Welcome to **The Show Runner** - your AI-powered production studio for creating 
engaging shows with custom characters, AI-generated video, and multi-platform output.

---

#### 🚀 Quick Start

1. **📸 Characters** - Add your talent with reference images and voice settings
2. **💡 Shows** - Create show concepts with topics and character assignments  
3. **🎥 Production** - Generate scripts, audio, and video
4. **📤 Outputs** - Export for Spreaker, YouTube, TikTok, Instagram

---
""")

# Dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📸 Characters")
    if st.session_state.characters:
        for name, char in list(st.session_state.characters.items())[:3]:
            st.markdown(f"- **{char.get('name', name)}** - {char.get('role', 'Character')}")
        if len(st.session_state.characters) > 3:
            st.caption(f"+ {len(st.session_state.characters) - 3} more...")
    else:
        st.info("No characters yet. Add some!")
    
    if st.button("➕ Add Character", use_container_width=True):
        st.switch_page("pages/1_📸_Characters.py")

with col2:
    st.markdown("### 💡 Shows")
    if st.session_state.shows:
        for show_id, show in list(st.session_state.shows.items())[:3]:
            st.markdown(f"- **{show.get('title', 'Untitled')}**")
        if len(st.session_state.shows) > 3:
            st.caption(f"+ {len(st.session_state.shows) - 3} more...")
    else:
        st.info("No shows yet. Create one!")
    
    if st.button("➕ Create Show", use_container_width=True):
        st.switch_page("pages/2_💡_Shows.py")

with col3:
    st.markdown("### 🎥 Recent Productions")
    outputs = list(OUTPUTS_DIR.glob("*/"))
    if outputs:
        for output in outputs[:3]:
            st.markdown(f"- {output.name}")
    else:
        st.info("No productions yet.")
    
    if st.button("🎬 Start Production", use_container_width=True):
        st.switch_page("pages/3_🎥_Production.py")

# Featured: AI House
st.divider()
st.markdown("### 🏠 Featured: AI House")
st.markdown("""
**AI House** is our flagship show featuring four AI personalities living together in Los Angeles.

| Character | Role | Voice |
|-----------|------|-------|
| Claire Delish | Food personality | Hume Custom |
| VV Steele | Gossip queen | Hume Custom |
| Olly Bennett | Adventurer | Hume Custom |
| Pennie Power | Finance expert | Hume Custom |
| Roxie Rush | Narrator | Hume Custom |

Episodes:
- [Episode 1: Room Wars](https://williamipai.github.io/ai-house-viewer/)
- [Episode 2: Insta-Chaos](https://williamipai.github.io/ai-house-ep2-v2-viewer/)
""")

if st.button("📥 Import AI House Characters"):
    # Import AI House characters
    ai_house_chars = {
        "claire": {
            "name": "Claire Delish",
            "role": "Food personality",
            "description": "Warm, nurturing food personality. Cozy, kitchen-focused visuals.",
            "voice_id": "09eccfe9-8068-42c3-8f0a-e91f5d50d160",
            "voice_provider": "hume"
        },
        "olly": {
            "name": "Olly Bennett", 
            "role": "Adventurer",
            "description": "Quirky British adventurer. Eclectic, travel-themed visuals.",
            "voice_id": "de25054e-a18d-41d7-93f3-d9fb6fb63078",
            "voice_provider": "hume"
        },
        "vv": {
            "name": "VV Steele",
            "role": "Gossip queen",
            "description": "Dramatic gossip diva. Glamorous, social media aesthetic.",
            "voice_id": "d513161a-3be9-4eaa-9612-711f77268b63",
            "voice_provider": "hume"
        },
        "pennie": {
            "name": "Pennie Power",
            "role": "Finance expert", 
            "description": "Smart finance personality. Modern, organized aesthetic.",
            "voice_id": "240fb214-35c0-4c46-ad08-ac16fe48499b",
            "voice_provider": "hume"
        },
        "roxie": {
            "name": "Roxie Rush",
            "role": "Narrator",
            "description": "Energetic narrator with commentary flair.",
            "voice_id": "33e57cc2-1727-465b-ab0f-8ac4bca82e9b",
            "voice_provider": "hume"
        }
    }
    
    st.session_state.characters.update(ai_house_chars)
    save_json(DATA_DIR / "characters.json", st.session_state.characters)
    st.success("✅ Imported 5 AI House characters!")
    st.rerun()
