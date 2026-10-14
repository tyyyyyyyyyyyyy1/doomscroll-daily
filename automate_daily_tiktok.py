import os
import glob
import random
import re
import subprocess
import time
import requests
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioArrayClip, AudioFileClip, CompositeAudioClip
from moviepy.audio import fx as afx

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID")
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_LIB_DIR = "audio_library"
os.makedirs(AUDIO_LIB_DIR, exist_ok=True)

# --- 2. SAFE JSON LOADER & CLEANER ---
def load_json_file(filepath, fallback_data, is_promo=False):
    if os.path.exists(filepath):
        try:
            import json
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    if is_promo:
                        cleaned_data = []
                        for item in data:
                            cleaned_item = re.sub(r'\s*#\d+\s*$', '', item)
                            cleaned_data.append(cleaned_item)
                        return cleaned_data
                    return data
        except Exception as e:
            print(f"⚠️ Error loading {filepath}: {e}. Using fallback data.")
    return fallback_data

FALLBACK_THOUGHTS = ["Your brain named itself without your explicit consent."]
FALLBACK_JOKES = ["My grandfather has the heart of a lion... and a lifetime ban from the zoo."]
FALLBACK_REDDIT = [{"sub": "r/AskReddit", "user": "u/DoomScroller99", "upvotes": "42.5k", "text": "\"I also choose this guy's dead wife.\""}]
FALLBACK_PROMOS = [f"Tired of boring weather apps & fake news?\nCheck out The Doomscroll Daily 🌤️\n\n{PROMO_LINK}"]

# --- 3. FILTERED MEME & BACKGROUND FETCH ENGINE (20 UNHINGED/DARK & SAFE SUBS) ---
def fetch_random_reddit_image():
    """Fetches images from a 20-subreddit pool of dark/unhinged humor while strictly blocking NSFW content."""
    target_subs = (
        "me_irl+wholesomememes+eyebleach+blursedimages+shitposting+"
        "meirl+2meirl4meirl+depression_memes+darkhumorjokes+HolUp+"
        "BlackHumor_101+ImFinnaGoToHell+me_irlgbt+NonPoliticalTwitter+"
        "me_irl4meirl+TrollXChromosomes+memes+dankmemes+PrequelMemes+meirl"
    )
    url = f"https://meme-api.com/gimme/{target_subs}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    blocked_keywords = [
        "nsfw", "porn", "sex", "boobs", "ass", "dick", "cock", "pussy", 
        "horny", "erection", "naked", "nude", "onlyfans", "cum", "penis", 
        "vagina", "slut", "whore", "tits", "milf", "hentai", "ankha"
    ]
    
    for attempt in range(10):
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                img_url = data.get("url")
                title = data.get("title", "").lower()
                subreddit = data.get("subreddit", "unknown")
                is_nsfw = data.get("nsfw", False)
                
                # Double-check API safety flag and title keywords
                if is_nsfw or any(word in title for word in blocked_keywords):
                    print(f"🛡️ Filtered out NSFW post from r/{subreddit}: '{title[:30]}...'")
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

# --- 4. CURATED AUDIO LIBRARY ENGINE (PURE MUSIC) ---
def generate_upgraded_dark_beat(duration=7):
    """Fallback deep bass generator if audio_library is empty."""
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sub_bass = np.sin(2 * np.pi * 55.0 * t) * np.exp(-1.5 * t) * 0.7
    stereo_data = np.vstack([sub_bass, sub_bass]).T
    return AudioArrayClip(stereo_data, fps=sample_rate).with_duration(duration)

def get_curated_audio_track(duration=7):
    """Pulls a clean pro studio track (.mp3, .wav, or .m4a) from the local audio_library/ folder without any background voice."""
    audio_files = (
        glob.glob(os.path.join(AUDIO_LIB_DIR, "*.mp3")) + 
        glob.glob(os.path.join(AUDIO_LIB_DIR, "*.wav")) + 
        glob.glob(os.path.join(AUDIO_LIB_DIR, "*.m4a"))
    )
    
    track_clip = None
    if audio_files:
        selected_track = random.choice(audio_files)
        print(f"🎵 Mixing studio track: {os.path.basename(selected_track)}")
        try:
            raw_clip = AudioFileClip(selected_track)
            if raw_clip.duration > duration + 2:
                max_start = raw_clip.duration - duration - 1
                start_time = random.uniform(0, max_start)
                track_clip = raw_clip.subclipped(start_time, start_time + duration)
            else:
                track_clip = raw_clip.subclipped(0, min(duration, raw_clip.duration))
            track_clip = track_clip.with_effects([afx.AudioFadeIn(0.2), afx.AudioFadeOut(0.4)])
        except Exception as e:
            print(f"⚠️ Error loading audio file {selected_track}: {e}")

    if not track_clip:
        print("⚠️ audio_library/ is empty. Add .mp3 or .m4a files to your repo's audio_library folder for studio sound.")
        track_clip = generate_upgraded_dark_beat(duration)

    return track_clip

# --- 5. GENERATION ENGINE ---
def generate_daily_batch():
    day_seed = int(datetime.now().strftime('%j')) + (datetime.now().year * 100)
    random.seed(day_seed)
    
    thoughts_pool = load_json_file("thoughts.json", FALLBACK_THOUGHTS)
    jokes_pool = load_json_file("jokes.json", FALLBACK_JOKES)
    reddit_pool = load_json_file("reddit.json", FALLBACK_REDDIT)
    promos_pool = load_json_file("promos.json", FALLBACK_PROMOS, is_promo=True)
    
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
    
    # --- ATTACH PURE CURATED STUDIO AUDIO ---
    try:
        audio_clip = get_curated_audio_track(duration)
        video = video.with_audio(audio_clip)
    except Exception as e:
        print(f"⚠️ Error attaching audio track: {e}")

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

    print("\n🎉 All videos rendered with strict 20-source dark meme filtering, pure studio tracks, hosted via Litterbox, and queued in Buffer!")
