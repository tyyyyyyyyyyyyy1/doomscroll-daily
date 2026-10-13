import os
import glob
import random
import subprocess
import time
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioArrayClip

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID")
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 2. SAFE JSON LOADER ---
def load_json_file(filepath, fallback_data):
    if os.path.exists(filepath):
        try:
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}. Using fallback data.")
    return fallback_data

FALLBACK_THOUGHTS = ["Your brain named itself without your explicit consent."]
FALLBACK_JOKES = ["My grandfather has the heart of a lion... and a lifetime ban from the zoo."]
FALLBACK_REDDIT = [{"sub": "r/AskReddit", "user": "u/DoomScroller99", "upvotes": "42.5k", "text": "\"I also choose this guy's dead wife.\""}]
FALLBACK_PROMOS = [f"Tired of boring weather apps & fake news?\nCheck out The Doomscroll Daily 🌤️\n\n{PROMO_LINK}"]

# --- 3. FILTERED MEME & BACKGROUND FETCH ENGINE ---
def fetch_random_reddit_image():
    """Fetches high-quality meme images while filtering out NSFW, sexual, and explicit terms for TikTok safety."""
    target_subs = "dankmemes+me_irl+PrequelMemes+wholesomememes+eyebleach+memes+shitposting+blursedimages"
    url = f"https://meme-api.com/gimme/{target_subs}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.6; Win64; x64) AppleWebKit/537.36"
    }
    
    blocked_keywords = [
        "nsfw", "porn", "sex", "boobs", "ass", "dick", "cock", "pussy", 
        "horny", "erection", "naked", "nude", "onlyfans", "cum", "penis", "vagina"
    ]
    
    for attempt in range(5):
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                img_url = data.get("url")
                title = data.get("title", "").lower()
                subreddit = data.get("subreddit", "unknown")
                
                if any(word in title for word in blocked_keywords):
                    print(f"🛡️ Filtered out NSFW/explicit meme from r/{subreddit}: '{title[:30]}...'")
                    continue
                
                if img_url and img_url.startswith("http"):
                    print(f"📥 Downloading clean background image from r/{subreddit}")
                    img_res = requests.get(img_url, headers=headers, timeout=8)
                    
                    if img_res.status_code == 200:
                        temp_path = "temp_bg.jpg"
                        img = Image.open(BytesIO(img_res.content)).convert("RGB")
                        img.save(temp_path)
                        print(f"✅ Successfully set clean background image!")
                        return temp_path
        except Exception as e:
            print(f"⚠️ Error fetching background image attempt {attempt+1}: {e}")
            
    print("⚠️ Using fallback visual color background.")
    return None

# --- 4. HEAVY PHONK & HARMONIC PRODUCTION ENGINE ---
def generate_heavy_phonk_audio(duration=7):
    """Generates a club-heavy phonk beat featuring thick 808 sub-bass, harmonic minor synth chords, and trap percussion."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    tempo_bpm = random.randint(132, 148) # Driving phonk tempo
    beat_interval = 60.0 / tempo_bpm
    
    # Deep club roots (F#, G, A minor variants common in heavy phonk)
    root_freq = random.choice([46.25, 49.00, 55.00]) # F#1, G1, A1
    
    sub_bass_track = np.zeros_like(t)
    chord_track = np.zeros_like(t)
    perc_track = np.zeros_like(t)
    
    # 1. Heavy 808 Sub-Bass Layer with Pitch Slides & Saturation
    current_beat = 0.0
    while current_beat < duration:
        hit_idx = int(current_beat * sample_rate)
        hit_len = int(0.35 * sample_rate) # Long sustaining heavy bass tail
        if hit_idx + hit_len < len(t):
            t_hit = np.linspace(0, 0.35, hit_len)
            # Characteristic phonk 808 pitch drop envelope
            freq_env = root_freq * (1 + 1.5 * np.exp(-12 * t_hit))
            # Rich sine + harmonic wave for sub-bass weight
            bass_wave = np.sin(2 * np.pi * freq_env * t_hit) + 0.3 * np.sin(2 * np.pi * (freq_env * 2) * t_hit)
            # Volume envelope with punchy attack and smooth release
            amp_env = np.exp(-4 * t_hit) * (1 - np.exp(-80 * t_hit))
            sub_bass_track[hit_idx:hit_idx+hit_len] += bass_wave * amp_env * 0.7
        current_beat += beat_interval # Four-on-the-floor / heavy downbeat bounce
        
    # 2. Harmonic Synth Chords (Minor Triads for Atmospheric Width)
    # Minor chord ratios: Root (1.0), Minor Third (1.189), Fifth (1.498)
    chord_ratios = [1.0, 1.189, 1.498]
    chord_duration = beat_interval * 2 # Changes every 2 beats
    curr_time = 0.0
    while curr_time < duration:
        chord_idx = int(curr_time * sample_rate)
        chord_len = int(chord_duration * sample_rate)
        if chord_idx + chord_len < len(t):
            t_chord = np.linspace(0, chord_duration, chord_len)
            chord_mix = np.zeros_like(t_chord)
            
            # Pick a harmonic progression offset
            offset = random.choice([1.0, 0.84, 0.75])
            for ratio in chord_ratios:
                f = root_freq * 4 * ratio * offset # Octave up for pad/synth texture
                # Rich saw-like approximation using harmonic summation to avoid arcade sound
                synth_tone = (np.sin(2 * np.pi * f * t_chord) + 
                              0.5 * np.sin(2 * np.pi * (f * 2) * t_chord) + 
                              0.25 * np.sin(2 * np.pi * (f * 3) * t_chord))
                chord_mix += synth_tone * 0.1
                
            # Slow warm filter/volume envelope
            envelope = np.sin(np.pi * t_chord / chord_duration) * 0.3
            chord_track[chord_idx:chord_idx+chord_len] += chord_mix * envelope
        curr_time += chord_duration

    # 3. Trap Percussion, Snare & Fast Hi-Hat Rolls
    current_beat = 0.0
    beat_count = 0
    while current_beat < duration:
        hit_idx = int(current_beat * sample_rate)
        hit_len = int(0.15 * sample_rate)
        
        if hit_idx + hit_len < len(t):
            t_hit = np.linspace(0, 0.15, hit_len)
            
            if beat_count % 4 == 2: # Heavy Phonk Snare/Clap on 2 and 4
                snare_noise = np.random.uniform(-1, 1, hit_len) * np.exp(-18 * t_hit) * 0.4
                snare_body = np.sin(2 * np.pi * 220 * t_hit) * np.exp(-25 * t_hit) * 0.3
                perc_track[hit_idx:hit_idx+hit_len] += snare_noise + snare_body
            else: # Crisp Hi-Hat ticks
                hat = np.random.uniform(-0.5, 0.5, int(hit_len/2)) * np.exp(-50 * t_hit[:int(hit_len/2)]) * 0.15
                perc_track[hit_idx:int(hit_idx + hit_len/2)] += hat
                
        # Add fast triplet hi-hat rolls between beats for that modern phonk texture
        if random.random() > 0.4:
            roll_idx = int((current_beat + beat_interval * 0.75) * sample_rate)
            roll_len = int(0.05 * sample_rate)
            if roll_idx + roll_len < len(t):
                t_roll = np.linspace(0, 0.05, roll_len)
                roll = np.random.uniform(-0.4, 0.4, roll_len) * np.exp(-60 * t_roll) * 0.12
                perc_track[roll_idx:roll_idx+roll_len] += roll

        current_beat += beat_interval / 2
        beat_count += 1

    # Master Bus Mixing, Saturation, and Limiting
    master_mix = sub_bass_track + chord_track + perc_track
    # Warm analog-style soft clipping to give it that heavy distorted tape crunch without digital harshness
    master_mix = np.tanh(master_mix * 1.3) * 0.85
    
    stereo_data = np.vstack([master_mix, master_mix]).T
    print(f"🔊 Produced heavy club phonk track (BPM: {tempo_bpm}, Root: {root_freq}Hz)")
    return AudioArrayClip(stereo_data, fps=sample_rate)

# --- 5. GENERATION ENGINE ---
def generate_daily_batch():
    day_seed = int(datetime.now().strftime('%j')) + (datetime.now().year * 100)
    random.seed(day_seed)
    
    thoughts_pool = load_json_file("thoughts.json", FALLBACK_THOUGHTS)
    jokes_pool = load_json_file("jokes.json", FALLBACK_JOKES)
    reddit_pool = load_json_file("reddit.json", FALLBACK_REDDIT)
    promos_pool = load_json_file("promos.json", FALLBACK_PROMOS)
    
    selected_thoughts = random.sample(thoughts_pool, min(3, len(thoughts_pool)))
    selected_joke = random.choice(jokes_pool)
    selected_reddit = random.choice(reddit_pool)
    selected_promos = random.sample(promos_pool, min(2, len(promos_pool)))
    
    return [
        {"type": "thought", "prefix": "[2 AM THOUGHT]\n\n", "time": "08:00", "content": selected_thoughts[0]},
        {"type": "thought", "prefix": "[DARK HUMOR]\n\n",    "time": "11:00", "content": selected_joke},
        {"type": "promo",   "prefix": "[SITE ALERT]\n\n",    "time": "13:00", "content": selected_promos[0]},
        {"type": "reddit",  "prefix": "[REDDIT WISDOM]\n\n", "time": "16:00", "content": selected_reddit},
        {"type": "thought", "prefix": "[2 AM THOUGHT]\n\n", "time": "19:00", "content": selected_thoughts[1]},
        {"type": "promo",   "prefix": "[SITE ALERT]\n\n",    "time": "21:30", "content": selected_promos[1]}
    ]

# --- 6. VIDEO RENDERING ENGINE ---
def render_video(slot_data, filename, duration=7):
    is_promo = slot_data["type"] == "promo"
    is_reddit = slot_data["type"] == "reddit"
    
    bg_image_path = fetch_random_reddit_image()
    
    if bg_image_path and os.path.exists(bg_image_path):
        bg = ImageClip(bg_image_path).with_duration(duration).resized(new_size=(1080, 1920))
    else:
        bg_color = (255, 51, 75) if is_promo else (18, 22, 31)
        bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    
    if is_reddit:
        r_data = slot_data["content"]
        full_text = f"[REDDIT WISDOM]\n\n{r_data['sub']} • Posted by {r_data['user']}\n⬆️ {r_data['upvotes']} Upvotes\n\n{r_data['text']}"
    else:
        content = slot_data["content"]
        prefix = slot_data["prefix"]
        full_text = f"{prefix}\"{content}\"" if not is_promo else f"{prefix}{content}"

    text_bg = ColorClip(size=(1000, 1500), color=(0, 0, 0), duration=duration).with_opacity(0.75).with_position('center')

    txt_clip = TextClip(
        text=full_text, 
        font_size=32 if is_reddit else 36, 
        color='white', 
        method='caption', 
        size=(960, 1400)
    ).with_duration(duration).with_position('center')
    
    video = CompositeVideoClip([bg, text_bg, txt_clip])
    
    # --- ATTACH HEAVY PHONK PRODUCTION AUDIO ---
    try:
        audio_clip = generate_heavy_phonk_audio(duration)
        video = video.with_audio(audio_clip)
    except Exception as e:
        print(f"⚠️ Error generating heavy phonk audio: {e}")

    output_path = os.path.join(OUTPUT_DIR, filename)
    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            os.remove(bg_image_path)
        except Exception:
            pass
            
    return output_path

# --- 7. UPLOAD TO LITTERBOX WITH RETRIES ---
def upload_to_litterbox(video_path, retries=3, backoff_factor=5):
    print(f"☁️ Uploading {video_path} to Litterbox host...")
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(1, retries + 1):
        try:
            with open(video_path, "rb") as f:
                data = {
                    "reqtype": "fileupload",
                    "time": "24h"
                }
                files = {
                    "fileToUpload": f
                }
                response = requests.post(url, data=data, files=files, headers=headers, timeout=60)
            
            if response.status_code == 200 and response.text.startswith("http"):
                direct_url = response.text.strip()
                print(f"✅ Upload complete: {direct_url}")
                print("⏳ Waiting 5 seconds for host propagation before sending to Buffer...")
                time.sleep(5)
                return direct_url
            else:
                print(f"⚠️ Attempt {attempt}/{retries} failed: Status {response.status_code} - {response.text.strip()}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt}/{retries} exception: {e}")
        
        if attempt < retries:
            sleep_time = backoff_factor * attempt
            print(f"🔄 Retrying upload in {sleep_time} seconds...")
            time.sleep(sleep_time)
            
    raise Exception("❌ Failed to upload video to Litterbox after multiple retry attempts.")

# --- 8. BUFFER GRAPHQL API SCHEDULER ---
def schedule_to_buffer(video_url, caption, scheduled_at_iso):
    url = "https://api.buffer.com"
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    mutation = """
    mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
            ... on PostActionSuccess {
                post { id dueAt }
            }
            ... on MutationError {
                message
            }
        }
    }
    """
    
    variables = {
        "input": {
            "text": caption,
            "channelId": BUFFER_PROFILE_ID,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": scheduled_at_iso,
            "assets": {
                "video": {"url": video_url}
            }
        }
    }

    response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
    res_data = response.json()
    
    data_payload = res_data.get("data", {}).get("createPost", {})
    mutation_error = data_payload.get("message")
    
    if response.status_code == 200 and "errors" not in res_data and not mutation_error:
        post_id = data_payload.get("post", {}).get("id", "Unknown ID")
        print(f"✅ Successfully scheduled for {scheduled_at_iso} (Post ID: {post_id})")
    else:
        print(f"❌ Buffer API Error: {response.status_code} - Full Response: {res_data}")

# --- 9. MAIN PIPELINE ---
if __name__ == "__main__":
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"🚀 Generating daily batch for {tomorrow}...\n")

    slots = generate_daily_batch()

    print("\n📅 Rendering, hosting, and sending schedule requests to Buffer...")
    for idx, slot in enumerate(slots, start=1):
        file_name = f"tiktok_slot_{idx}.mp4"
        
        video_path = render_video(slot, file_name)
        public_url = upload_to_litterbox(video_path)
        
        scheduled_datetime = f"{tomorrow}T{slot['time']}:00.000Z"
        
        if slot["type"] == "reddit":
            caption_text = f"{slot['content']['sub']}: {slot['content']['text']}"
        elif slot["type"] == "promo":
            caption_text = slot["content"]
        else:
            caption_text = slot["content"]
            
        caption = f"{caption_text}\n\n#doomscrolldaily #brainrot #darkhumor #reddit #weather #fyp"
        
        schedule_to_buffer(public_url, caption, scheduled_datetime)

    print("\n🎉 All videos rendered with heavy club phonk production, hosted via Litterbox, and queued in Buffer!")
