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
import pytz
from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip, AudioArrayClip, AudioFileClip, CompositeAudioClip
from moviepy.audio import fx as afx
import google.generativeai as genai

# --- 0. GEMINI API SETUP ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
TIKTOK_ID = os.getenv("BUFFER_PROFILE_ID")
INSTA_ID = os.getenv("BUFFER_INSTAGRAM_PROFILE_ID")
YOUTUBE_ID = os.getenv("BUFFER_YOUTUBE_PROFILE_ID")

CHANNEL_IDS = [TIKTOK_ID, INSTA_ID, YOUTUBE_ID]
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
AUDIO_LIB_DIR = "audio_library"
os.makedirs(AUDIO_LIB_DIR, exist_ok=True)

# --- TIMEZONE SCHEDULING HELPER (OTTAWA / AMERICA/TORONTO) ---
def get_scheduled_at_iso(slot_time_str):
    """
    Calculates exact ISO timestamp targeting Ottawa local time (America/Toronto).
    Prevents cron UTC skew and eliminates 36+ hour queue overflows.
    """
    tz = pytz.timezone('America/Toronto')
    now_est = datetime.now(tz)
    
    hour_est, min_est = map(int, slot_time_str.split(':'))
    
    # Target specified slot time for today in Ottawa
    target_local = now_est.replace(hour=hour_est, minute=min_est, second=0, microsecond=0)
    
    # If this slot time has already passed today, target tomorrow
    if now_est >= target_local:
        target_local += timedelta(days=1)
        
    return target_local.isoformat()

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

# --- 2.5 DYNAMIC GEMINI CAPTION & HASHTAG GENERATOR ---
def generate_smart_caption(content_topic):
    """
    Dynamically generates a witty joke hook, link-in-bio CTA, and a balanced mix 
    of niche topic tags and rotated trending tags via Gemini API.
    """
    prompt = f"""
    You are managing the social media captions for 'The Doomscroll Daily', an edgy internet meme dashboard.
    The current content/topic is about: "{content_topic}"

    Write a high-converting short-form post caption following these EXACT rules:
    1. JOKE & HOOK: Write a brief, sarcastic, or hilarious 1-2 sentence reaction/joke about the topic.
    2. CALL TO ACTION (CTA): Include a witty line leading them to click the link in bio to visit the site (e.g., "Full daily dose of chaos linked in bio 🔗", "Don't click the link in my bio unless you like unhinged stuff 💀", "Link in bio for more daily brain rot 👇").
    3. HASHTAGS: Include 5 to 7 hashtags total. 
       - 2-3 specific tags relevant to the topic
       - 2-3 rotated high-traffic/trending tags (#FYP, #DankMemes, #Relatable, #Viral, #ForYouPage)
       - Do NOT use risky, controversial, or banned words.

    Return ONLY the final caption text ready to paste, with line breaks.
    """

    try:
        model = genai.GenerativeModel('gemini-3.8-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Gemini Caption Generation Error: {e}. Using fallback caption.")
        return f"{content_topic}\n\nLink in bio for more 👇\n\n#DankMemes #FYP #Viral #Relatable #DoomscrollDaily"

# --- 3. FILTERED MEME & BACKGROUND FETCH ENGINE ---
def fetch_random_reddit_image():
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

# --- 4. CURATED AUDIO LIBRARY ENGINE ---
def generate_upgraded_dark_beat(duration=7):
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sub_bass = np.sin(2 * np.pi * 55.0 * t) * np.exp(-1.5 * t) * 0.7
    stereo_data = np.vstack([sub_bass, sub_bass]).T
    return AudioArrayClip(stereo_data, fps=sample_rate).with_duration(duration)

def get_curated_audio_track(duration=7):
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

# --- 7. MULTI-PROVIDER FALLBACK UPLOAD ENGINE ---
def upload_to_catbox(video_path):
    url = "https://catbox.moe/user/api.php"
    with open(video_path, "rb") as f:
        files = {"fileToUpload": f}
        data = {"reqtype": "fileupload"}
        res = requests.post(url, data=data, files=files, timeout=60)
    if res.status_code == 200 and res.text.strip().startswith("http"):
        return res.text.strip()
    raise Exception(f"Catbox failed with status {res.status_code}: {res.text[:100]}")

def upload_to_litterbox(video_path):
    url = "https://litterbox.catbox.moe/resources/internals/api.php"
    with open(video_path, "rb") as f:
        files = {"fileToUpload": f}
        data = {"reqtype": "fileupload", "time": "24h"}
        res = requests.post(url, data=data, files=files, timeout=60)
    if res.status_code == 200 and res.text.strip().startswith("http"):
        return res.text.strip()
    raise Exception(f"Litterbox failed with status {res.status_code}: {res.text[:100]}")

def upload_to_tmpfile(video_path):
    url = "https://tmpfile.link/api/upload"
    with open(video_path, "rb") as f:
        files = {"file": f}
        res = requests.post(url, files=files, timeout=60)
    if res.status_code == 200:
        res_json = res.json()
        direct_url = res_json.get("downloadLink") or res_json.get("downloadLinkEncoded")
        if direct_url:
            return direct_url
    raise Exception(f"Tmpfile failed with status {res.status_code}: {res.text[:100]}")

def upload_video(video_path, attempts_per_host=3, backoff_factor=3):
    providers = [
        ("Catbox.moe", upload_to_catbox),
        ("Litterbox (24h)", upload_to_litterbox),
        ("tmpfile.link", upload_to_tmpfile)
    ]

    for provider_name, provider_func in providers:
        print(f"☁️ Attempting uploads using {provider_name}...")
        for attempt in range(1, attempts_per_host + 1):
            try:
                direct_url = provider_func(video_path)
                print(f"✅ Upload succeeded via {provider_name}: {direct_url}")
                time.sleep(3)
                return direct_url
            except Exception as e:
                print(f"⚠️ [{provider_name}] Attempt {attempt}/{attempts_per_host} failed: {e}")
                if attempt < attempts_per_host:
                    time.sleep(backoff_factor * attempt)

        print(f"❌ All {attempts_per_host} attempts failed for {provider_name}. Switching to next host...\n")

    raise Exception("❌ Critical Failure: Video upload failed across all fallback file hosts.")

# --- 8. BUFFER GRAPHQL API SCHEDULER (MULTI-PLATFORM WITH METADATA) ---
def schedule_to_buffer(video_url, caption, scheduled_at_iso):
    url = "https://api.buffer.com"
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for channel_id in CHANNEL_IDS:
        if not channel_id:
            print("⚠️ Skipping empty channel ID.")
            continue

        # Attach network-specific required metadata
        metadata = {}
        if channel_id == INSTA_ID:
            metadata = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
        elif channel_id == YOUTUBE_ID:
            video_title = caption.split('\n')[0][:80] if caption else "The Doomscroll Daily"
            metadata = {"youtube": {"title": video_title, "categoryId": "24"}}

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
        
        input_payload = {
            "text": caption,
            "channelId": channel_id,
            "schedulingType": "automatic",
            "mode": "customScheduled",
            "dueAt": scheduled_at_iso,
            "assets": {
                "video": {"url": video_url}
            }
        }
        
        if metadata:
            input_payload["metadata"] = metadata

        variables = {"input": input_payload}

        try:
            response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
            res_data = response.json()
            
            data_payload = res_data.get("data", {}).get("createPost", {})
            mutation_error = data_payload.get("message")
            
            if response.status_code == 200 and "errors" not in res_data and not mutation_error:
                post_id = data_payload.get("post", {}).get("id", "Unknown ID")
                print(f"✅ Successfully scheduled for channel {channel_id} at {scheduled_at_iso} (Post ID: {post_id})")
            else:
                print(f"❌ Buffer API Error for channel {channel_id}: {response.status_code} - Full Response: {res_data}")
        except Exception as e:
            print(f"❌ Exception while scheduling for channel {channel_id}: {e}")

# --- 9. MAIN PIPELINE ---
if __name__ == "__main__":
    tz_ottawa = pytz.timezone('America/Toronto')
    current_ottawa_time = datetime.now(tz_ottawa).strftime('%Y-%m-%d %H:%M:%S %Z')
    print(f"🚀 Starting daily batch execution. Current Ottawa Local Time: {current_ottawa_time}...\n")

    slots = generate_daily_batch()

    print("\n📅 Rendering, hosting, and sending schedule requests to Buffer...")
    for idx, slot in enumerate(slots, start=1):
        file_name = f"multichannel_slot_{idx}.mp4"
        
        video_path = render_video(slot, file_name)
        public_url = upload_video(video_path)
        
        # Calculates precise Ottawa ISO timestamp for slot (08:00, 11:00, 13:00, 16:00, 19:00, 21:30)
        scheduled_datetime_iso = get_scheduled_at_iso(slot['time'])
        
        # Extract raw topic text to pass into Gemini generator
        if slot["type"] == "reddit":
            raw_topic_text = f"Reddit {slot['content']['sub']}: {slot['content']['text']}"
        elif slot["type"] == "promo":
            raw_topic_text = f"Promo: {slot['content']}"
        else:
            raw_topic_text = slot['content']
            
        print(f"🤖 Generating smart dynamic caption via Gemini for slot {idx}...")
        caption = generate_smart_caption(raw_topic_text)
        
        schedule_to_buffer(public_url, caption, scheduled_datetime_iso)

    print("\n🎉 All videos rendered, hosted, and successfully queued across TikTok, Instagram, and YouTube via Buffer with dynamic AI captions!")
