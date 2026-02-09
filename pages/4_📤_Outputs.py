"""
📤 Outputs
View, download, and publish your productions.
"""

import streamlit as st
from pathlib import Path
import json
import os
from datetime import datetime

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"
OUTPUTS_DIR = APP_DIR / "outputs"

OUTPUTS_DIR.mkdir(exist_ok=True)

st.title("📤 Outputs")
st.markdown("View, download, and publish your productions.")

# List all productions
productions = sorted(OUTPUTS_DIR.glob("*/"), key=lambda x: x.stat().st_mtime, reverse=True)

if not productions:
    st.info("No productions yet. Go to Production to create one!")
    if st.button("🎥 Start Production"):
        st.switch_page("pages/3_🎥_Production.py")
else:
    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("🔍 Search", placeholder="Filter productions...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Newest", "Oldest", "Name"])
    
    if sort_by == "Oldest":
        productions = reversed(productions)
    elif sort_by == "Name":
        productions = sorted(productions, key=lambda x: x.name)
    
    st.divider()
    
    for prod_dir in productions:
        if search and search.lower() not in prod_dir.name.lower():
            continue
        
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### 🎬 {prod_dir.name}")
                
                # Check what files exist
                files = list(prod_dir.rglob("*"))
                file_types = []
                
                script_path = prod_dir / "script.md"
                audio_path = prod_dir / "audio" / "combined.mp3"
                video_path = prod_dir / "video" / "final.mp4"
                
                if script_path.exists():
                    file_types.append("📝 Script")
                if audio_path.exists():
                    file_types.append("🎤 Audio")
                if video_path.exists():
                    file_types.append("🎥 Video")
                
                clips_dir = prod_dir / "clips"
                if clips_dir.exists():
                    num_clips = len(list(clips_dir.glob("*.mp4")))
                    if num_clips:
                        file_types.append(f"📱 {num_clips} Clips")
                
                st.caption(" | ".join(file_types) if file_types else "Empty")
                
                # Timestamp
                mtime = datetime.fromtimestamp(prod_dir.stat().st_mtime)
                st.caption(f"Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                # Actions
                if video_path.exists():
                    with open(video_path, "rb") as f:
                        st.download_button(
                            "⬇️ Video",
                            f.read(),
                            file_name=f"{prod_dir.name}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                
                if audio_path.exists():
                    with open(audio_path, "rb") as f:
                        st.download_button(
                            "⬇️ Audio",
                            f.read(),
                            file_name=f"{prod_dir.name}.mp3",
                            mime="audio/mpeg",
                            use_container_width=True
                        )
                
                if st.button("🗑️ Delete", key=f"del_{prod_dir.name}", use_container_width=True):
                    import shutil
                    shutil.rmtree(prod_dir)
                    st.rerun()
            
            # Expandable details
            with st.expander("View Details"):
                tabs = st.tabs(["Script", "Audio", "Video", "Clips"])
                
                with tabs[0]:
                    if script_path.exists():
                        with open(script_path) as f:
                            st.markdown(f.read())
                    else:
                        st.info("No script generated")
                
                with tabs[1]:
                    if audio_path.exists():
                        st.audio(str(audio_path))
                        
                        # List individual audio files
                        audio_files = list((prod_dir / "audio").glob("*.mp3"))
                        if len(audio_files) > 1:
                            st.caption(f"{len(audio_files)} audio files")
                    else:
                        st.info("No audio generated")
                
                with tabs[2]:
                    if video_path.exists():
                        st.video(str(video_path))
                    else:
                        st.info("No video generated")
                
                with tabs[3]:
                    if clips_dir.exists():
                        clips = list(clips_dir.glob("*.mp4"))
                        if clips:
                            for clip in clips:
                                st.markdown(f"**{clip.name}**")
                                st.video(str(clip))
                        else:
                            st.info("No clips generated")
                    else:
                        st.info("No clips generated")

# Publishing section
st.divider()
st.markdown("## 📢 Publishing")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🎧 Spreaker")
        st.caption("Publish podcast audio")
        
        # Check Spreaker credentials
        spreaker_key = Path(os.path.expanduser("~/clawd/.secrets/spreaker.json"))
        if spreaker_key.exists():
            st.success("✅ Connected")
            if st.button("Publish to Spreaker", use_container_width=True):
                st.info("Spreaker publishing would happen here")
        else:
            st.warning("⚠️ Not configured")
            st.caption("Add spreaker.json to .secrets/")

with col2:
    with st.container(border=True):
        st.markdown("### 📺 YouTube")
        st.caption("Upload full videos")
        
        youtube_key = Path(os.path.expanduser("~/clawd/.secrets/youtube.json"))
        if youtube_key.exists():
            st.success("✅ Connected")
            if st.button("Upload to YouTube", use_container_width=True):
                st.info("YouTube upload would happen here")
        else:
            st.warning("⚠️ Not configured")
            st.caption("Add youtube.json to .secrets/")

with col3:
    with st.container(border=True):
        st.markdown("### 📱 Social Media")
        st.caption("TikTok, Instagram, etc.")
        
        st.info("📤 Manual upload")
        st.caption("Download clips and upload to platforms")

# Clip generator
st.divider()
st.markdown("## ✂️ Clip Generator")
st.markdown("Create short clips from your videos for TikTok and Instagram.")

video_productions = [p for p in OUTPUTS_DIR.glob("*/video/final.mp4")]

if video_productions:
    selected_video = st.selectbox("Select Video", [str(v.parent.parent.name) for v in video_productions])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        start_time = st.number_input("Start (seconds)", min_value=0, value=0)
    with col2:
        duration = st.number_input("Duration (seconds)", min_value=5, max_value=60, value=30)
    with col3:
        aspect = st.selectbox("Aspect Ratio", ["9:16 (TikTok/Reels)", "1:1 (Square)", "16:9 (Original)"])
    
    if st.button("✂️ Create Clip", use_container_width=True):
        st.info(f"Would create {duration}s clip starting at {start_time}s in {aspect} format")
else:
    st.info("No videos available. Generate one first!")
