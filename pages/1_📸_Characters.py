"""
📸 Character Management
Manage your talent roster with reference images and voice settings.
"""

import streamlit as st
from pathlib import Path
import json
import shutil
import requests
import os
from datetime import datetime

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
CHARACTERS_DIR = APP_DIR / "characters"
OUTPUTS_DIR = APP_DIR / "outputs"

DATA_DIR.mkdir(exist_ok=True)
CHARACTERS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_api_key(service):
    """Get API key from Streamlit secrets or local files"""
    # Try Streamlit secrets first
    try:
        return st.secrets.get("api_keys", {}).get(service)
    except:
        pass
    
    # Try local secrets file
    secrets_dir = Path(os.path.expanduser("~/clawd/.secrets"))
    key_file = secrets_dir / f"{service}.json"
    if key_file.exists():
        with open(key_file) as f:
            data = json.load(f)
            return data.get("api_key") or data.get("key")
    return None

# Load characters
if "characters" not in st.session_state:
    st.session_state.characters = load_json(DATA_DIR / "characters.json", {})

st.title("📸 Characters")
st.markdown("Manage your talent roster — click any character to create content!")

# Tabs
tab1, tab2, tab3 = st.tabs(["👥 Roster", "➕ Add Character", "⚡ Quick Video"])

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
                    
                    # Actions - now with MAKE VIDEO as primary action
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🎬 Video", key=f"video_{char_id}", use_container_width=True, type="primary"):
                            st.session_state.quick_video_char = char_id
                            st.rerun()
                    with col2:
                        if st.button("✏️", key=f"edit_{char_id}", use_container_width=True):
                            st.session_state.editing_char = char_id
                            st.rerun()
                    with col3:
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

with tab3:
    st.markdown("### ⚡ Quick Video Generator")
    st.markdown("Select a character and create a video in one step!")
    
    # Check if character was selected from roster
    selected_char_id = st.session_state.get('quick_video_char', None)
    
    # Character selector
    if st.session_state.characters:
        char_options = {f"{c.get('name', cid)} ({cid})": cid for cid, c in st.session_state.characters.items()}
        
        # Set default if coming from roster
        default_idx = 0
        if selected_char_id and selected_char_id in st.session_state.characters:
            char_list = list(char_options.values())
            if selected_char_id in char_list:
                default_idx = char_list.index(selected_char_id)
        
        selected_char_name = st.selectbox(
            "Select Character", 
            list(char_options.keys()),
            index=default_idx
        )
        char_id = char_options[selected_char_name]
        char = st.session_state.characters[char_id]
        
        # Show selected character
        col1, col2 = st.columns([1, 2])
        with col1:
            img_path = CHARACTERS_DIR / f"{char_id}.png"
            if img_path.exists():
                st.image(str(img_path), width=150)
            else:
                st.markdown("🎭")
            st.markdown(f"**{char.get('name', char_id)}**")
            st.caption(char.get('role', ''))
            if char.get('voice_id'):
                st.markdown(f"🎤 Voice ready")
        
        with col2:
            st.markdown("#### Script Options")
            
            script_mode = st.radio(
                "Script Mode",
                ["✍️ Write my own script", "🤖 Generate from topic"],
                horizontal=True
            )
            
            if script_mode == "✍️ Write my own script":
                script_text = st.text_area(
                    "Your Script",
                    placeholder=f"Write what {char.get('name', char_id)} should say...\n\nExample: Hey everyone! Today I want to talk about...",
                    height=200
                )
            else:
                topic = st.text_input(
                    "Topic",
                    placeholder="e.g., 5 tips for better mornings"
                )
                tone = st.selectbox(
                    "Tone",
                    ["Energetic & Fun", "Calm & Thoughtful", "Educational", "Comedic", "Inspirational"]
                )
                duration = st.select_slider(
                    "Target Duration",
                    options=["15 sec (TikTok)", "30 sec (Reel)", "60 sec (Short)", "2-3 min (YouTube)"],
                    value="30 sec (Reel)"
                )
                script_text = None  # Will be generated
        
        st.divider()
        
        # Output format
        st.markdown("#### Output Format")
        output_format = st.selectbox(
            "Platform",
            ["📱 Instagram Reel (9:16)", "📺 YouTube Short (9:16)", "🎬 YouTube Video (16:9)", "🎵 TikTok (9:16)"]
        )
        
        # Generate button
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            generate_audio = st.button("🎤 Generate Audio Only", use_container_width=True)
        with col2:
            generate_full = st.button("🎬 Generate Full Video", use_container_width=True, type="primary")
        
        if generate_audio or generate_full:
            # Create output directory
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = OUTPUTS_DIR / f"quick_{char_id}_{timestamp}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Generate script if needed
            if script_mode == "🤖 Generate from topic" and topic:
                with st.spinner("✍️ Writing script..."):
                    api_key = get_api_key("anthropic")
                    if not api_key:
                        st.error("❌ Anthropic API key not configured!")
                        st.info("Add it in Streamlit Cloud Settings → Secrets")
                        st.stop()
                    
                    # Build prompt based on character
                    prompt = f"""Write a short video script for {char.get('name', char_id)}.

**Character:** {char.get('name', char_id)}
**Role:** {char.get('role', 'Content creator')}
**Description:** {char.get('description', 'Engaging personality')}

**Topic:** {topic}
**Tone:** {tone}
**Target Duration:** {duration}

Write the script as direct dialogue - what the character says to camera. 
No stage directions, just the spoken words.
Make it sound natural, conversational, and true to the character.
Include personality, catchphrases, and authentic voice.

Script:"""

                    response = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": api_key,
                            "content-type": "application/json",
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-3-5-sonnet-20241022",
                            "max_tokens": 2048,
                            "messages": [{"role": "user", "content": prompt}]
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        script_text = response.json()["content"][0]["text"]
                        st.success("✅ Script generated!")
                        with st.expander("View Script"):
                            st.markdown(script_text)
                        
                        # Save script
                        with open(output_dir / "script.txt", "w") as f:
                            f.write(script_text)
                    else:
                        st.error(f"Script generation failed: {response.status_code}")
                        st.stop()
            
            if not script_text:
                st.error("Please provide a script or topic!")
                st.stop()
            
            # Step 2: Generate audio with Hume
            with st.spinner("🎤 Generating voice..."):
                hume_key = get_api_key("hume")
                voice_id = char.get('voice_id')
                
                if not hume_key:
                    st.error("❌ Hume API key not configured!")
                    st.info("Add it in Streamlit Cloud Settings → Secrets")
                    st.stop()
                
                if not voice_id:
                    st.error(f"❌ No voice ID set for {char.get('name', char_id)}")
                    st.info("Edit the character to add a Hume voice ID")
                    st.stop()
                
                # Call Hume TTS API
                tts_response = requests.post(
                    "https://api.hume.ai/v0/tts",
                    headers={
                        "X-Hume-Api-Key": hume_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": script_text,
                        "voice": {"id": voice_id}
                    },
                    timeout=120
                )
                
                if tts_response.status_code == 200:
                    audio_path = output_dir / "audio.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(tts_response.content)
                    
                    st.success("✅ Audio generated!")
                    st.audio(str(audio_path))
                    
                    # Download button for audio
                    with open(audio_path, "rb") as f:
                        st.download_button(
                            "📥 Download Audio",
                            f,
                            file_name=f"{char_id}_{timestamp}.mp3",
                            mime="audio/mpeg"
                        )
                else:
                    st.error(f"Audio generation failed: {tts_response.status_code}")
                    try:
                        st.json(tts_response.json())
                    except:
                        st.text(tts_response.text[:500])
                    st.stop()
            
            # Step 3: Generate video if requested
            if generate_full:
                with st.spinner("🎬 Generating video... (this may take a few minutes)"):
                    ltx_key = get_api_key("ltx")
                    
                    if not ltx_key:
                        st.warning("⚠️ LTX API key not configured - video generation skipped")
                        st.info("Add it in Streamlit Cloud Settings → Secrets for full video generation")
                    else:
                        # Determine aspect ratio
                        if "9:16" in output_format:
                            resolution = "1080x1920"  # Portrait
                        else:
                            resolution = "1920x1080"  # Landscape
                        
                        # Create video prompt based on character
                        video_prompt = f"""A {char.get('role', 'content creator')} speaking to camera. 
{char.get('description', 'Professional, engaging presence')}. 
High quality, well-lit, modern setting. Social media video style."""

                        # Call LTX Video API
                        video_response = requests.post(
                            "https://api.ltx.video/v1/text-to-video",
                            headers={
                                "Authorization": f"Bearer {ltx_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "prompt": video_prompt,
                                "model": "ltx-2-fast",
                                "duration": 6,
                                "resolution": resolution,
                                "generate_audio": False
                            },
                            timeout=300
                        )
                        
                        if video_response.status_code == 200:
                            video_path = output_dir / "video.mp4"
                            with open(video_path, "wb") as f:
                                f.write(video_response.content)
                            
                            st.success("✅ Video generated!")
                            st.video(str(video_path))
                            
                            with open(video_path, "rb") as f:
                                st.download_button(
                                    "📥 Download Video",
                                    f,
                                    file_name=f"{char_id}_{timestamp}.mp4",
                                    mime="video/mp4"
                                )
                            
                            st.info("💡 **Tip:** Combine the audio and video in CapCut or your favorite editor for the final result!")
                        else:
                            st.warning(f"Video generation issue: {video_response.status_code}")
                            st.info("Audio is ready! You can use a static image or generate video separately.")
            
            st.success(f"🎉 Files saved to: {output_dir}")
    
    else:
        st.warning("No characters in roster. Add some first!")

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

# Clear quick video selection on page load if not coming from a button
if 'quick_video_char' in st.session_state and not st.session_state.get('_from_roster_click'):
    pass  # Keep selection
