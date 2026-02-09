"""
📸 Character Management
Manage your talent roster with reference images and voice settings.
"""

import streamlit as st
from pathlib import Path
import json
import shutil

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
CHARACTERS_DIR = APP_DIR / "characters"

DATA_DIR.mkdir(exist_ok=True)
CHARACTERS_DIR.mkdir(exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load characters
if "characters" not in st.session_state:
    st.session_state.characters = load_json(DATA_DIR / "characters.json", {})

st.title("📸 Characters")
st.markdown("Manage your talent roster with reference images and voice settings.")

# Tabs
tab1, tab2 = st.tabs(["👥 Roster", "➕ Add Character"])

with tab1:
    if not st.session_state.characters:
        st.info("No characters yet. Add some in the 'Add Character' tab!")
    else:
        # Display characters in a grid
        cols = st.columns(3)
        for i, (char_id, char) in enumerate(st.session_state.characters.items()):
            with cols[i % 3]:
                with st.container(border=True):
                    # Character image
                    img_path = CHARACTERS_DIR / f"{char_id}.png"
                    if img_path.exists():
                        st.image(str(img_path), width=150)
                    else:
                        st.markdown("🎭")
                    
                    st.markdown(f"### {char.get('name', char_id)}")
                    st.caption(char.get('role', 'Character'))
                    
                    if char.get('description'):
                        st.markdown(f"_{char['description'][:100]}..._" if len(char.get('description', '')) > 100 else f"_{char.get('description')}_")
                    
                    # Voice info
                    voice_provider = char.get('voice_provider', 'none')
                    if voice_provider != 'none':
                        st.markdown(f"🎤 **Voice:** {voice_provider.title()}")
                    
                    # Actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{char_id}", use_container_width=True):
                            st.session_state.editing_char = char_id
                            st.rerun()
                    with col2:
                        if st.button("🗑️", key=f"del_{char_id}", use_container_width=True):
                            del st.session_state.characters[char_id]
                            save_json(DATA_DIR / "characters.json", st.session_state.characters)
                            st.rerun()

with tab2:
    st.markdown("### Add New Character")
    
    with st.form("add_character"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Reference image upload
            uploaded_file = st.file_uploader("Reference Image", type=['png', 'jpg', 'jpeg', 'webp'])
            if uploaded_file:
                st.image(uploaded_file, width=200)
        
        with col2:
            char_id = st.text_input("Character ID", placeholder="claire_delish", help="Lowercase, no spaces")
            char_name = st.text_input("Display Name", placeholder="Claire Delish")
            char_role = st.text_input("Role", placeholder="Food personality")
            char_desc = st.text_area("Description", placeholder="Warm, nurturing personality...", height=100)
        
        st.divider()
        st.markdown("#### 🎤 Voice Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            voice_provider = st.selectbox("Voice Provider", ["hume", "elevenlabs", "none"])
        with col2:
            voice_id = st.text_input("Voice ID", placeholder="UUID or voice name")
        
        # Hume voice presets
        if voice_provider == "hume":
            st.markdown("**QP-1 Custom Voices:**")
            preset = st.selectbox("Or select preset", [
                "Custom (enter ID above)",
                "Female QP-1: d4e78913-ca08-40fc-89a2-c5d2eb27133d",
                "Male QP-1: 98bd98d4-0a8b-4abd-8933-c03b6c8b5321",
                "Claire Delish: 09eccfe9-8068-42c3-8f0a-e91f5d50d160",
                "Olly Bennett: de25054e-a18d-41d7-93f3-d9fb6fb63078",
                "VV Steele: d513161a-3be9-4eaa-9612-711f77268b63",
                "Pennie Power: 240fb214-35c0-4c46-ad08-ac16fe48499b",
                "Roxie Rush: 33e57cc2-1727-465b-ab0f-8ac4bca82e9b",
            ])
            if preset != "Custom (enter ID above)":
                voice_id = preset.split(": ")[1]
        
        submitted = st.form_submit_button("💾 Save Character", use_container_width=True)
        
        if submitted:
            if not char_id:
                st.error("Character ID is required!")
            elif char_id in st.session_state.characters:
                st.error("Character ID already exists!")
            else:
                # Save character data
                st.session_state.characters[char_id] = {
                    "name": char_name or char_id,
                    "role": char_role,
                    "description": char_desc,
                    "voice_provider": voice_provider,
                    "voice_id": voice_id
                }
                save_json(DATA_DIR / "characters.json", st.session_state.characters)
                
                # Save image if uploaded
                if uploaded_file:
                    img_path = CHARACTERS_DIR / f"{char_id}.png"
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                
                st.success(f"✅ Added {char_name or char_id}!")
                st.rerun()

# Edit modal
if "editing_char" in st.session_state:
    char_id = st.session_state.editing_char
    char = st.session_state.characters.get(char_id, {})
    
    st.divider()
    st.markdown(f"### ✏️ Editing: {char.get('name', char_id)}")
    
    with st.form("edit_character"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            img_path = CHARACTERS_DIR / f"{char_id}.png"
            if img_path.exists():
                st.image(str(img_path), width=200)
            uploaded_file = st.file_uploader("New Image", type=['png', 'jpg', 'jpeg', 'webp'], key="edit_img")
        
        with col2:
            char_name = st.text_input("Display Name", value=char.get('name', ''))
            char_role = st.text_input("Role", value=char.get('role', ''))
            char_desc = st.text_area("Description", value=char.get('description', ''), height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            voice_provider = st.selectbox("Voice Provider", ["hume", "elevenlabs", "none"], 
                index=["hume", "elevenlabs", "none"].index(char.get('voice_provider', 'none')))
        with col2:
            voice_id = st.text_input("Voice ID", value=char.get('voice_id', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                st.session_state.characters[char_id] = {
                    "name": char_name,
                    "role": char_role,
                    "description": char_desc,
                    "voice_provider": voice_provider,
                    "voice_id": voice_id
                }
                save_json(DATA_DIR / "characters.json", st.session_state.characters)
                
                if uploaded_file:
                    with open(CHARACTERS_DIR / f"{char_id}.png", "wb") as f:
                        f.write(uploaded_file.getvalue())
                
                del st.session_state.editing_char
                st.success("✅ Saved!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                del st.session_state.editing_char
                st.rerun()
