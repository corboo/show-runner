"""
🎥 Production Pipeline
Generate scripts, audio, and video for your shows.
"""

import streamlit as st
from pathlib import Path
import json
import subprocess
import os
import time
from datetime import datetime

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
OUTPUTS_DIR = APP_DIR / "outputs"
CHARACTERS_DIR = APP_DIR / "characters"

DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load API keys - check Streamlit secrets first, then local files
SECRETS_DIR = Path(os.path.expanduser("~/clawd/.secrets"))

def get_api_key(service):
    # First try Streamlit secrets (for cloud deployment)
    try:
        if "api_keys" in st.secrets and service in st.secrets["api_keys"]:
            return st.secrets["api_keys"][service]
    except Exception:
        pass
    
    # Fall back to local files (for local development)
    key_file = SECRETS_DIR / f"{service}.json"
    if key_file.exists():
        with open(key_file) as f:
            data = json.load(f)
            return data.get("api_key") or data.get("key")
    return None

# Load data
if "characters" not in st.session_state:
    st.session_state.characters = load_json(DATA_DIR / "characters.json", {})

if "shows" not in st.session_state:
    st.session_state.shows = load_json(DATA_DIR / "shows.json", {})

st.title("🎥 Production")
st.markdown("Generate scripts, audio, and video for your shows.")

# Check API keys
api_status = {
    "anthropic": "✅" if get_api_key("anthropic") else "❌",
    "hume": "✅" if get_api_key("hume") else "❌",
    "ltx": "✅" if get_api_key("ltx") else "❌",
    "openai": "✅" if get_api_key("openai") else "❌",
}

with st.expander("🔑 API Status"):
    cols = st.columns(4)
    for i, (service, status) in enumerate(api_status.items()):
        cols[i].metric(service.title(), status)

# Select show and episode
st.divider()

if not st.session_state.shows:
    st.warning("No shows created yet. Create one first!")
    if st.button("➕ Create Show"):
        st.switch_page("pages/2_💡_Shows.py")
else:
    col1, col2 = st.columns(2)
    
    with col1:
        show_options = {f"{s.get('title', 'Untitled')}": sid for sid, s in st.session_state.shows.items()}
        selected_show_name = st.selectbox("Select Show", list(show_options.keys()))
        selected_show_id = show_options[selected_show_name]
        show = st.session_state.shows[selected_show_id]
    
    with col2:
        episodes = show.get("episodes", [])
        if episodes:
            ep_options = {f"{i+1}. {ep.get('title', 'Untitled')}": i for i, ep in enumerate(episodes)}
            selected_ep_name = st.selectbox("Select Episode", list(ep_options.keys()))
            selected_ep_idx = ep_options[selected_ep_name]
            episode = episodes[selected_ep_idx]
        else:
            st.warning("No episodes in this show.")
            episode = None

    if episode:
        st.divider()
        
        # Show episode details
        with st.container(border=True):
            st.markdown(f"### {show.get('title')}: {episode.get('title')}")
            st.markdown(f"**Topic:** {episode.get('topic', 'Not specified')}")
            st.markdown(f"**Tone:** {episode.get('tone', 'Not specified')}")
            st.markdown(f"**Cast:** {', '.join([st.session_state.characters.get(c, {}).get('name', c) for c in show.get('characters', [])])}")
            if show.get('narrator'):
                st.markdown(f"**Narrator:** {st.session_state.characters.get(show['narrator'], {}).get('name', show['narrator'])}")
        
        # Production pipeline
        st.divider()
        st.markdown("## 🚀 Production Pipeline")
        
        # Create output directory for this production
        production_id = f"{selected_show_id}_{selected_ep_idx}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        production_dir = OUTPUTS_DIR / production_id
        
        # Step 1: Script Generation
        st.markdown("### 1️⃣ Script Generation")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            script_model = st.selectbox("AI Model", ["claude-3-5-sonnet", "gpt-4o", "claude-3-opus"])
            target_lines = st.slider("Target Dialogue Lines", 20, 100, 50)
        
        script_path = production_dir / "script.md"
        
        if script_path.exists():
            with open(script_path) as f:
                existing_script = f.read()
            st.success("✅ Script exists!")
            with st.expander("View Script"):
                st.markdown(existing_script)
        else:
            if st.button("📝 Generate Script", use_container_width=True):
                production_dir.mkdir(parents=True, exist_ok=True)
                
                with st.spinner("Generating script..."):
                    # Build character descriptions
                    char_descriptions = []
                    for char_id in show.get('characters', []):
                        char = st.session_state.characters.get(char_id, {})
                        char_descriptions.append(f"- **{char.get('name', char_id)}**: {char.get('description', char.get('role', 'Character'))}")
                    
                    narrator_info = ""
                    if show.get('narrator'):
                        narrator = st.session_state.characters.get(show['narrator'], {})
                        narrator_info = f"\n\n**Narrator:** {narrator.get('name', show['narrator'])} - {narrator.get('description', 'Provides commentary')}"
                    
                    prompt = f"""Write a script for an AI-generated video episode.

**Show:** {show.get('title')}
**Format:** {show.get('format', 'Sitcom')}
**Episode:** {episode.get('title')}
**Topic:** {episode.get('topic')}
**Tone:** {episode.get('tone', 'Comedic')}
**Visual Style:** {show.get('visual_style', 'Modern, cinematic')}

**Characters:**
{chr(10).join(char_descriptions)}
{narrator_info}

**Requirements:**
1. Write approximately {target_lines} dialogue lines
2. Mark each line with the character name in CAPS
3. Include [SCENE] markers for visual changes
4. Include V.O. (voiceover) lines for narrator sections
5. Add stage directions in (parentheses)
6. Make it engaging, funny, and suitable for social media clips

**Format Example:**
[SCENE: Morning in the apartment, sunlight streaming through windows]

ROXIE (V.O.): It started like any other morning at the AI House...

CLAIRE: (entering with coffee) Good morning everyone!

VV: (scrolling phone) Did you see what trending on Instagram?

Write the full script:"""

                    # Use Anthropic API
                    import requests
                    
                    api_key = get_api_key("anthropic")
                    if not api_key:
                        st.error("Anthropic API key not found!")
                    else:
                        response = requests.post(
                            "https://api.anthropic.com/v1/messages",
                            headers={
                                "x-api-key": api_key,
                                "content-type": "application/json",
                                "anthropic-version": "2023-06-01"
                            },
                            json={
                                "model": "claude-3-5-sonnet-20241022",
                                "max_tokens": 8192,
                                "messages": [{"role": "user", "content": prompt}]
                            },
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            script = response.json()["content"][0]["text"]
                            
                            with open(script_path, "w") as f:
                                f.write(script)
                            
                            st.success("✅ Script generated!")
                            with st.expander("View Script"):
                                st.markdown(script)
                            st.rerun()
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text[:200]}")
        
        # Step 2: Audio Generation
        st.markdown("### 2️⃣ Audio Generation")
        
        audio_dir = production_dir / "audio"
        combined_audio = audio_dir / "combined.mp3"
        
        if combined_audio.exists():
            st.success("✅ Audio exists!")
            st.audio(str(combined_audio))
        elif script_path.exists():
            if st.button("🎤 Generate Audio (Hume TTS)", use_container_width=True):
                audio_dir.mkdir(parents=True, exist_ok=True)
                
                with st.spinner("Generating audio... This may take a few minutes."):
                    # Parse script and generate audio
                    # This would use the Hume TTS API
                    st.info("Audio generation would run here using Hume TTS API")
                    st.warning("Full audio generation requires running the production script externally.")
        else:
            st.info("Generate script first")
        
        # Step 3: Video Generation
        st.markdown("### 3️⃣ Video Generation")
        
        video_path = production_dir / "video" / "final.mp4"
        
        if video_path.exists():
            st.success("✅ Video exists!")
            st.video(str(video_path))
        elif combined_audio.exists():
            video_method = st.radio("Video Method", [
                "🎬 Full AI Video (LTX - recommended)",
                "📸 Static Images + Audio",
                "🎭 Lip-sync Talking Heads (D-ID)"
            ])
            
            if st.button("🎥 Generate Video", use_container_width=True):
                with st.spinner("Generating video... This may take 10-20 minutes."):
                    st.info("Video generation would run here using LTX/D-ID APIs")
                    st.warning("Full video generation requires running the Forge pipeline externally.")
        else:
            st.info("Generate audio first")
        
        # Step 4: Export
        st.markdown("### 4️⃣ Export & Publish")
        
        if video_path.exists():
            st.markdown("**Output Options:**")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 🎧 Spreaker")
                if st.button("Export Audio for Podcast", use_container_width=True):
                    st.info("Would export audio to Spreaker format")
            
            with col2:
                st.markdown("#### 📺 YouTube")
                if st.button("Export Full Video", use_container_width=True):
                    st.info("Would export full video for YouTube")
            
            with col3:
                st.markdown("#### 📱 Social Clips")
                if st.button("Generate TikTok/Reels", use_container_width=True):
                    st.info("Would generate short clips for TikTok/Instagram")
        else:
            st.info("Generate video first")
        
        # Quick production (run full pipeline)
        st.divider()
        st.markdown("### ⚡ Quick Production")
        st.markdown("Run the full pipeline with one click (uses Forge system).")
        
        if st.button("🚀 Run Full Production Pipeline", use_container_width=True, type="primary"):
            st.info("""
            **Full production would:**
            1. Generate script with Claude
            2. Generate character audio with Hume TTS
            3. Transcribe and create scene prompts with GPT-4o
            4. Generate video scenes with LTX Video
            5. Combine audio + video
            6. Create social clips
            
            **To run manually:**
            ```bash
            cd ~/clawd/show-runner
            python3 produce.py --show {selected_show_id} --episode {selected_ep_idx}
            ```
            """)
