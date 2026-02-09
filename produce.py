#!/usr/bin/env python3
"""
🎬 THE SHOW RUNNER - Production Pipeline
Run the full production pipeline from command line.

Usage:
    python produce.py --show <show_id> --episode <episode_idx>
    python produce.py --config production.json
"""

import os
import sys
import json
import argparse
import subprocess
import requests
import time
from pathlib import Path
from datetime import datetime

# Paths
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
OUTPUTS_DIR = APP_DIR / "outputs"
CHARACTERS_DIR = APP_DIR / "characters"
SECRETS_DIR = Path(os.path.expanduser("~/clawd/.secrets"))

def load_json(path, default=None):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def get_api_key(service):
    key_file = SECRETS_DIR / f"{service}.json"
    if key_file.exists():
        with open(key_file) as f:
            data = json.load(f)
            return data.get("api_key") or data.get("key")
    return None

class ShowRunner:
    def __init__(self, show_id, episode_idx):
        self.show_id = show_id
        self.episode_idx = episode_idx
        
        # Load data
        self.characters = load_json(DATA_DIR / "characters.json", {})
        self.shows = load_json(DATA_DIR / "shows.json", {})
        
        if show_id not in self.shows:
            raise ValueError(f"Show not found: {show_id}")
        
        self.show = self.shows[show_id]
        self.episodes = self.show.get("episodes", [])
        
        if episode_idx >= len(self.episodes):
            raise ValueError(f"Episode {episode_idx} not found")
        
        self.episode = self.episodes[episode_idx]
        
        # Create production directory
        self.production_id = f"{show_id}_{episode_idx}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        self.production_dir = OUTPUTS_DIR / self.production_id
        self.production_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🎬 Production: {self.production_id}")
        print(f"   Show: {self.show.get('title')}")
        print(f"   Episode: {self.episode.get('title')}")
        print(f"   Output: {self.production_dir}")
        print()
    
    def generate_script(self):
        """Generate script using Claude."""
        print("📝 Step 1: Generating Script...")
        
        script_path = self.production_dir / "script.md"
        if script_path.exists():
            print("   ✓ Script already exists")
            return script_path
        
        # Build character descriptions
        char_descriptions = []
        for char_id in self.show.get('characters', []):
            char = self.characters.get(char_id, {})
            char_descriptions.append(f"- **{char.get('name', char_id)}**: {char.get('description', char.get('role', 'Character'))}")
        
        narrator_info = ""
        if self.show.get('narrator'):
            narrator = self.characters.get(self.show['narrator'], {})
            narrator_info = f"\n\n**Narrator:** {narrator.get('name', self.show['narrator'])} - {narrator.get('description', 'Provides commentary')}"
        
        prompt = f"""Write a script for an AI-generated video episode.

**Show:** {self.show.get('title')}
**Format:** {self.show.get('format', 'Sitcom')}
**Episode:** {self.episode.get('title')}
**Topic:** {self.episode.get('topic')}
**Tone:** {self.episode.get('tone', 'Comedic')}
**Visual Style:** {self.show.get('visual_style', 'Modern, cinematic')}

**Characters:**
{chr(10).join(char_descriptions)}
{narrator_info}

**Requirements:**
1. Write approximately 50 dialogue lines
2. Mark each line with the character name in CAPS
3. Include [SCENE] markers for visual changes  
4. Include V.O. (voiceover) lines for narrator sections
5. Add stage directions in (parentheses)
6. Make it engaging, funny, and suitable for social media clips
7. Include shot type hints: 🎭 TALKING HEAD, 🎬 B-ROLL, 📱 SCREEN

**Format Example:**
[SCENE: Morning in the apartment, sunlight streaming through windows]
🎬 B-ROLL

ROXIE (V.O.): It started like any other morning at the AI House...

🎭 TALKING HEAD
CLAIRE: (entering with coffee) Good morning everyone!

Write the full script:"""

        api_key = get_api_key("anthropic")
        if not api_key:
            raise ValueError("Anthropic API key not found!")
        
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
        
        if response.status_code != 200:
            raise Exception(f"Claude API error: {response.status_code} - {response.text[:200]}")
        
        script = response.json()["content"][0]["text"]
        
        with open(script_path, "w") as f:
            f.write(script)
        
        print(f"   ✓ Script saved ({len(script)} chars)")
        return script_path
    
    def parse_script(self, script_path):
        """Parse script into dialogue lines."""
        print("   Parsing script...")
        
        with open(script_path) as f:
            script = f.read()
        
        lines = []
        current_scene = ""
        
        for line in script.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Scene marker
            if line.startswith('[SCENE'):
                current_scene = line
                continue
            
            # Shot type markers
            if line in ['🎭 TALKING HEAD', '🎬 B-ROLL', '📱 SCREEN']:
                continue
            
            # Dialogue line (CHARACTER: text)
            if ':' in line and line.split(':')[0].isupper():
                parts = line.split(':', 1)
                character = parts[0].strip()
                text = parts[1].strip()
                
                # Remove stage directions from text
                if '(' in text and ')' in text:
                    # Keep text after stage direction
                    import re
                    text = re.sub(r'\([^)]*\)\s*', '', text).strip()
                
                if text:
                    # Check if V.O.
                    is_vo = '(V.O.)' in character or 'V.O.' in character
                    char_name = character.replace('(V.O.)', '').replace('V.O.', '').strip()
                    
                    # Map character name to ID
                    char_id = None
                    for cid, cdata in self.characters.items():
                        if cdata.get('name', '').upper() == char_name.upper() or cid.upper() == char_name.upper():
                            char_id = cid
                            break
                    
                    if char_id:
                        lines.append({
                            "idx": len(lines),
                            "character": char_id,
                            "text": text,
                            "is_vo": is_vo,
                            "scene": current_scene
                        })
        
        print(f"   ✓ Parsed {len(lines)} dialogue lines")
        return lines
    
    def generate_audio(self, dialogue_lines):
        """Generate audio using Hume TTS."""
        print("🎤 Step 2: Generating Audio...")
        
        audio_dir = self.production_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        # Save dialogue lines
        save_json(audio_dir / "dialogue_lines.json", dialogue_lines)
        
        hume_key = get_api_key("hume")
        if not hume_key:
            raise ValueError("Hume API key not found!")
        
        generated = []
        
        for line in dialogue_lines:
            idx = line["idx"]
            char_id = line["character"]
            text = line["text"]
            
            output_path = audio_dir / f"{idx:03d}_{char_id}.mp3"
            
            if output_path.exists() and output_path.stat().st_size > 1000:
                print(f"   [{idx:03d}] {char_id}: exists")
                generated.append(output_path)
                continue
            
            char = self.characters.get(char_id, {})
            voice_id = char.get("voice_id")
            
            if not voice_id:
                print(f"   [{idx:03d}] {char_id}: no voice ID, skipping")
                continue
            
            print(f"   [{idx:03d}] {char_id}: {text[:40]}...")
            
            # Call Hume TTS API
            try:
                response = requests.post(
                    "https://api.hume.ai/v0/tts",
                    headers={
                        "X-Hume-Api-Key": hume_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "voice": {"id": voice_id},
                        "text": text
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    # Response is base64 audio
                    import base64
                    audio_data = response.json().get("audio")
                    if audio_data:
                        with open(output_path, "wb") as f:
                            f.write(base64.b64decode(audio_data))
                        generated.append(output_path)
                        print(f"         ✓ Saved")
                else:
                    print(f"         ✗ Error: {response.status_code}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"         ✗ Exception: {e}")
        
        print(f"   ✓ Generated {len(generated)} audio files")
        
        # Combine audio
        if generated:
            self.combine_audio(generated, audio_dir / "combined.mp3")
        
        return audio_dir
    
    def combine_audio(self, audio_files, output_path):
        """Combine audio files with small gaps."""
        print("   Combining audio...")
        
        concat_file = output_path.parent / "concat_list.txt"
        silence_file = output_path.parent / "silence.mp3"
        
        # Create short silence
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
            "-t", "0.3", "-q:a", "9", str(silence_file)
        ], capture_output=True)
        
        with open(concat_file, "w") as f:
            for i, audio in enumerate(sorted(audio_files)):
                f.write(f"file '{audio.absolute()}'\n")
                if i < len(audio_files) - 1:
                    f.write(f"file '{silence_file.absolute()}'\n")
        
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c:a", "libmp3lame", "-q:a", "2",
            str(output_path)
        ], capture_output=True)
        
        concat_file.unlink()
        silence_file.unlink()
        
        print(f"   ✓ Combined audio: {output_path}")
    
    def generate_video(self, audio_path):
        """Generate video using LTX (Forge pipeline)."""
        print("🎥 Step 3: Generating Video...")
        
        video_dir = self.production_dir / "video"
        video_dir.mkdir(exist_ok=True)
        
        # Use Forge pipeline
        # This would normally call the forge_generate.py script
        print("   Running Forge video generation...")
        print("   (This is a placeholder - full implementation would use LTX API)")
        
        # For now, just note that video generation would happen here
        print("   ⚠️ Video generation requires running Forge externally")
        print(f"   Command: python forge_generate.py {audio_path} {self.production_id}")
        
        return video_dir
    
    def create_clips(self, video_path):
        """Create social media clips."""
        print("✂️ Step 4: Creating Clips...")
        
        clips_dir = self.production_dir / "clips"
        clips_dir.mkdir(exist_ok=True)
        
        # This would create clips for TikTok/Instagram
        print("   ⚠️ Clip generation would happen here")
        
        return clips_dir
    
    def run(self):
        """Run the full production pipeline."""
        print("=" * 60)
        print("🎬 THE SHOW RUNNER - Production Pipeline")
        print("=" * 60)
        print()
        
        # Step 1: Generate script
        script_path = self.generate_script()
        print()
        
        # Parse script
        dialogue_lines = self.parse_script(script_path)
        print()
        
        # Step 2: Generate audio
        audio_dir = self.generate_audio(dialogue_lines)
        print()
        
        # Step 3: Generate video
        video_dir = self.generate_video(audio_dir / "combined.mp3")
        print()
        
        # Step 4: Create clips
        clips_dir = self.create_clips(video_dir / "final.mp4")
        print()
        
        print("=" * 60)
        print("✅ Production Complete!")
        print("=" * 60)
        print(f"Output: {self.production_dir}")

def main():
    parser = argparse.ArgumentParser(description="The Show Runner - Production Pipeline")
    parser.add_argument("--show", help="Show ID")
    parser.add_argument("--episode", type=int, default=0, help="Episode index")
    parser.add_argument("--config", help="Production config JSON file")
    parser.add_argument("--list", action="store_true", help="List available shows")
    
    args = parser.parse_args()
    
    if args.list:
        shows = load_json(DATA_DIR / "shows.json", {})
        print("Available shows:")
        for sid, show in shows.items():
            print(f"  {sid}: {show.get('title')} ({len(show.get('episodes', []))} episodes)")
        return
    
    if args.config:
        config = load_json(Path(args.config))
        args.show = config.get("show_id")
        args.episode = config.get("episode_idx", 0)
    
    if not args.show:
        print("Error: --show or --config required")
        parser.print_help()
        sys.exit(1)
    
    runner = ShowRunner(args.show, args.episode)
    runner.run()

if __name__ == "__main__":
    main()
