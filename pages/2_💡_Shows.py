"""
💡 Show Management
Create and manage show concepts with character assignments.
"""

import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import uuid

APP_DIR = Path(__file__).parent.parent
DATA_DIR = APP_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load data
if "characters" not in st.session_state:
    st.session_state.characters = load_json(DATA_DIR / "characters.json", {})

if "shows" not in st.session_state:
    st.session_state.shows = load_json(DATA_DIR / "shows.json", {})

st.title("💡 Shows")
st.markdown("Create and manage show concepts.")

# Tabs
tab1, tab2, tab3 = st.tabs(["📺 My Shows", "➕ Create Show", "📋 Templates"])

with tab1:
    if not st.session_state.shows:
        st.info("No shows yet. Create one in the 'Create Show' tab!")
    else:
        for show_id, show in st.session_state.shows.items():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"### {show.get('title', 'Untitled')}")
                    st.caption(f"Format: {show.get('format', 'Unknown')} | Episodes: {len(show.get('episodes', []))}")
                    st.markdown(show.get('description', '')[:200] + "..." if len(show.get('description', '')) > 200 else show.get('description', ''))
                    
                    # Characters
                    chars = show.get('characters', [])
                    if chars:
                        char_names = [st.session_state.characters.get(c, {}).get('name', c) for c in chars]
                        st.markdown(f"**Cast:** {', '.join(char_names)}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_show_{show_id}", use_container_width=True):
                        st.session_state.editing_show = show_id
                        st.rerun()
                    
                    if st.button("🎬 Produce", key=f"produce_{show_id}", use_container_width=True):
                        st.session_state.producing_show = show_id
                        st.switch_page("pages/3_🎥_Production.py")
                
                with col3:
                    if st.button("🗑️ Delete", key=f"del_show_{show_id}", use_container_width=True):
                        del st.session_state.shows[show_id]
                        save_json(DATA_DIR / "shows.json", st.session_state.shows)
                        st.rerun()

with tab2:
    st.markdown("### Create New Show")
    
    with st.form("create_show"):
        # Basic info
        title = st.text_input("Show Title", placeholder="AI House")
        description = st.text_area("Description", placeholder="A sitcom about AI personalities living together...", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            format_type = st.selectbox("Format", [
                "Sitcom / Comedy",
                "Documentary",
                "News / Commentary", 
                "Interview",
                "Educational",
                "Drama",
                "Custom"
            ])
        with col2:
            target_duration = st.selectbox("Target Duration", [
                "Short (1-3 min)",
                "Medium (3-7 min)",
                "Long (7-15 min)",
                "Full Episode (15-30 min)"
            ])
        
        st.divider()
        st.markdown("#### 🎭 Cast")
        
        if not st.session_state.characters:
            st.warning("No characters available. Add some in the Characters page first!")
            selected_chars = []
        else:
            char_options = {f"{v.get('name', k)} ({v.get('role', 'Character')})": k 
                          for k, v in st.session_state.characters.items()}
            selected_display = st.multiselect("Select Characters", list(char_options.keys()))
            selected_chars = [char_options[d] for d in selected_display]
        
        # Narrator
        narrator = st.selectbox("Narrator", ["None"] + list(st.session_state.characters.keys()))
        
        st.divider()
        st.markdown("#### 💡 Episode Concept")
        
        episode_title = st.text_input("Episode Title", placeholder="Episode 1: Room Wars")
        episode_topic = st.text_area("Topic / Premise", placeholder="The roommates must decide who gets the best bedroom...", height=100)
        
        # Tone and style
        col1, col2 = st.columns(2)
        with col1:
            tone = st.selectbox("Tone", ["Comedic", "Dramatic", "Educational", "Casual", "Energetic", "Mysterious"])
        with col2:
            style = st.text_input("Visual Style", placeholder="Mid-century modern LA apartment, warm lighting...")
        
        # Additional references
        st.markdown("#### 📎 Reference Materials (Optional)")
        ref_images = st.file_uploader("Reference Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        ref_notes = st.text_area("Additional Notes", placeholder="Any specific scenes, jokes, or moments to include...", height=80)
        
        submitted = st.form_submit_button("💾 Create Show", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("Show title is required!")
            else:
                show_id = str(uuid.uuid4())[:8]
                
                st.session_state.shows[show_id] = {
                    "title": title,
                    "description": description,
                    "format": format_type,
                    "target_duration": target_duration,
                    "characters": selected_chars,
                    "narrator": narrator if narrator != "None" else None,
                    "visual_style": style,
                    "created_at": datetime.now().isoformat(),
                    "episodes": [{
                        "title": episode_title or "Episode 1",
                        "topic": episode_topic,
                        "tone": tone,
                        "ref_notes": ref_notes,
                        "status": "draft"
                    }] if episode_topic else []
                }
                
                save_json(DATA_DIR / "shows.json", st.session_state.shows)
                
                # Save reference images
                if ref_images:
                    show_refs = DATA_DIR / "show_refs" / show_id
                    show_refs.mkdir(parents=True, exist_ok=True)
                    for i, img in enumerate(ref_images):
                        with open(show_refs / f"ref_{i}.png", "wb") as f:
                            f.write(img.getvalue())
                
                st.success(f"✅ Created '{title}'!")
                st.rerun()

with tab3:
    st.markdown("### 📋 Show Templates")
    st.markdown("Quick-start templates for common show formats.")
    
    templates = [
        {
            "name": "🏠 AI House Clone",
            "format": "Sitcom / Comedy",
            "description": "AI personalities living together, dealing with everyday situations with comedic results.",
            "style": "Mid-century modern apartment, warm lighting, Instagram-worthy interiors",
            "tone": "Comedic",
            "duration": "Medium (3-7 min)"
        },
        {
            "name": "📰 AI News Desk",
            "format": "News / Commentary",
            "description": "AI hosts discuss and react to trending topics with wit and insight.",
            "style": "Modern news studio, clean graphics, professional lighting",
            "tone": "Energetic",
            "duration": "Short (1-3 min)"
        },
        {
            "name": "🎓 Explainer Series",
            "format": "Educational",
            "description": "AI host explains complex topics in an engaging, accessible way.",
            "style": "Clean whiteboard aesthetic, animated graphics, friendly visuals",
            "tone": "Educational",
            "duration": "Medium (3-7 min)"
        },
        {
            "name": "🎙️ AI Talk Show",
            "format": "Interview",
            "description": "AI host interviews characters or discusses topics with panel guests.",
            "style": "Late night talk show set, warm studio lighting, cozy atmosphere",
            "tone": "Casual",
            "duration": "Long (7-15 min)"
        }
    ]
    
    cols = st.columns(2)
    for i, template in enumerate(templates):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### {template['name']}")
                st.caption(f"{template['format']} | {template['duration']}")
                st.markdown(template['description'])
                st.markdown(f"**Style:** {template['style']}")
                st.markdown(f"**Tone:** {template['tone']}")
                
                if st.button(f"Use Template", key=f"template_{i}", use_container_width=True):
                    st.session_state.template_data = template
                    st.info("Template loaded! Go to 'Create Show' tab to customize.")

# Edit show modal
if "editing_show" in st.session_state:
    show_id = st.session_state.editing_show
    show = st.session_state.shows.get(show_id, {})
    
    st.divider()
    st.markdown(f"### ✏️ Editing: {show.get('title', 'Untitled')}")
    
    # Add episode form
    st.markdown("#### Add Episode")
    with st.form("add_episode"):
        ep_title = st.text_input("Episode Title")
        ep_topic = st.text_area("Topic / Premise", height=100)
        ep_tone = st.selectbox("Tone", ["Comedic", "Dramatic", "Educational", "Casual", "Energetic"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("➕ Add Episode", use_container_width=True):
                if ep_title:
                    if "episodes" not in show:
                        show["episodes"] = []
                    show["episodes"].append({
                        "title": ep_title,
                        "topic": ep_topic,
                        "tone": ep_tone,
                        "status": "draft"
                    })
                    st.session_state.shows[show_id] = show
                    save_json(DATA_DIR / "shows.json", st.session_state.shows)
                    st.success(f"Added episode: {ep_title}")
                    st.rerun()
        with col2:
            if st.form_submit_button("❌ Done Editing", use_container_width=True):
                del st.session_state.editing_show
                st.rerun()
    
    # List episodes
    if show.get("episodes"):
        st.markdown("#### Episodes")
        for i, ep in enumerate(show["episodes"]):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{i+1}. {ep.get('title', 'Untitled')}** ({ep.get('status', 'draft')})")
                    st.caption(ep.get('topic', '')[:100])
                with col2:
                    if st.button("🗑️", key=f"del_ep_{i}"):
                        show["episodes"].pop(i)
                        st.session_state.shows[show_id] = show
                        save_json(DATA_DIR / "shows.json", st.session_state.shows)
                        st.rerun()
