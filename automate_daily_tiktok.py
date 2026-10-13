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
from gtts import gTTS
from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioArrayClip, AudioFileClip, concatenate_audioclips, CompositeAudioClip

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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
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

# --- 4. DRIFT PHONK AUDIO & VOICE SAMPLE GENERATOR ---
def generate_voice_sample(duration=7):
    """Programmatically generates an eerie spoken-word voice snippet to layer into the track like Brutus."""
    phrases = [
        "Everyone is talking about it.",
        "I must watch closely.",
        "Another day, another scroll.",
        "Can you hear them coming?",
        "Check the feed."
    ]
    selected_text = random.choice(phrases)
    temp_speech_path = "temp_voice.mp3"
    try:
        tts = gTTS(text=selected_text, lang='en', slow=True)
        tts.save(temp_speech_path)
        voice_clip = AudioFileClip(temp_speech_path)
        if voice_clip.duration > duration:
            voice_clip = voice_clip.subclipped(0, duration)
        return voice_clip
    except Exception as e:
        print(f"⚠️ Could not generate voice sample: {e}")
        return None

def generate_drift_phonk_audio(duration=7):
    """Generates a heavy drift phonk track with metallic cowbells, rolling 808s, tape distortion, and spoken voice."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    tempo_bpm = 132
    beat_interval = 60.0 / tempo_bpm
    
    root_freq = random.choice([51.91, 55.00, 61.74])
    scale_offsets = [1.0, 1.189, 1.335, 1.498, 1.782]
    
    sub_bass = np.zeros_like(t)
    cowbell_melody = np.zeros_like(t)
    percussion = np.zeros_like(t)
    
    # 1. Rolling 808 Sub-Bass
    current_beat = 0.0
    while current_beat < duration:
        hit_idx = int(current_beat * sample_rate)
        hit_len = int(0.4 * sample_rate)
        if hit_idx + hit_len < len(t):
            t_hit = np.linspace(0, 0.4, hit_len)
            freq_env = root_freq * (1 + 2.0 * np.exp(-15 * t_hit))
            bass_wave = np.sin(2 * np.pi * freq_env * t_hit) + 0.4 * np.sin(2 * np.pi * (freq_env * 2) * t_hit)
            envelope = np.exp(-3 * t_hit) * (1 - np.exp(-50 * t_hit))
            sub_bass[hit_idx:hit_idx+hit_len] += bass_wave * envelope * 0.8
        current_beat += beat_interval

    # 2. Aggressive Cowbell Melody
    melody_notes = [0, 3, 5, 3, 7, 5, 3, 0]
    step_duration = beat_interval / 2
    curr_time = 0.0
    note_pointer = random.randint(0, len(melody_notes) - 1)
    
    while curr_time < duration:
        note_idx = int(curr_time * sample_rate)
        note_len = int(0.18 * sample_rate)
        if note_idx + note_len < len(t):
            scale_step = scale_offsets[melody_notes[note_pointer] % len(scale_offsets)]
            cowbell_freq = root_freq * 8 * scale_step
            
            t_note = np.linspace(0, 0.18, note_len)
            glide_freq = cowbell_freq * (1 + 1.5 * np.exp(-30 * t_note))
            bell_wave = (np.sin(2 * np.pi * glide_freq * t_note) + 
                         0.5 * np.sin(2 * np.pi * (glide_freq * 1.5) * t_note) +
                         0.3 * np.sin(2 * np.pi * (glide_freq * 2.0) * t_note))
            
            bell_env = np.exp(-12 * t_note)
            cowbell_melody[note_idx:note_idx+note_len] += bell_wave * bell_env * 0.35
            
        note_pointer = (note_pointer + 1) % len(melody_notes)
        curr_time += step_duration

    # 3. Trap Percussion & Hi-Hats
    current_beat = 0.0
    beat_count = 0
    while current_beat < duration:
        hit_idx = int(current_beat * sample_rate)
        hit_len = int(0.12 * sample_rate)
        if hit_idx + hit_len < len(t):
            t_hit = np.linspace(0, 0.12, hit_len)
            if beat_count % 4 == 2:
                snare = np.random.uniform(-1, 1, hit_len) * np.exp(-20 * t_hit) * 0.4
                percussion[hit_idx:hit_idx+hit_len] += snare
            else:
                hat = np.random.uniform(-0.5, 0.5, int(hit_len/2)) * np.exp(-60 * t_hit[:int(hit_len/2)]) * 0.12
                percussion[hit_idx:int(hit_idx + hit_len/2)] += hat
        current_beat += beat_interval / 2
        beat_count += 1

    master_mix = sub_bass + cowbell_melody + percussion
    master_mix = np.tanh(master_mix * 2.2) * 0.8
    stereo_data = np.vstack([master_mix, master_mix]).T
    beat_audio = AudioArrayClip(stereo_data, fps=sample_rate)
    
    # Layer with synthesized eerie voice sample
    voice_audio = generate_voice_sample(duration)
    if voice_audio:
        # Mix the voice quietly over the driving beat
        final_audio = CompositeAudioClip([beat_audio, voice_audio.with_volume_scaled(0.6)])
        return final_audio
    
    return beat_audio

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
    
    # --- ATTACH DRIFT PHONK AUDIO WITH VOCALS ---
    try:
        audio_clip = generate_drift_phonk_audio(duration)
        video = video.with_audio(audio_clip)
    except Exception as e:
        print(f"⚠️ Error generating drift phonk audio: {e}")

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

    print("\n🎉 All videos rendered with drift phonk & eerie voice samples, hosted via Litterbox, and queued in Buffer!")
