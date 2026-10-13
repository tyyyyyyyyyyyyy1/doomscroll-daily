import os
import glob
import random
import subprocess
import time
import requests
from io import BytesIO
from PIL import Image
from datetime import datetime, timedelta
from moviepy import ImageClip, TextClip, CompositeVideoClip, ColorClip

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID")
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Subreddits combining your exact index.js meme sources[span_1](start_span)[span_1](end_span) with visual background categories
BACKGROUND_SUBREDDITS = [
    # Original index.js meme sources[span_2](start_span)[span_2](end_span)
    "dankmemes",
    "me_irl",
    "PrequelMemes",
    "wholesomememes",
    "eyebleach",
    
    # Additional atmospheric/meme backdrop communities
    "memes",
    "liminalspace",
    "shitposting",
    "blursedimages",
    "outrun",
    "natureisfuckinglit"
]

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

# --- 3. REDDIT LIVE IMAGE BACKGROUND FETCH ENGINE ---
def fetch_random_reddit_image():
    """Fetches a direct image URL from Reddit JSON API, pulling from index.js and backdrop subreddits[span_3](start_span)[span_3](end_span)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    sub = random.choice(BACKGROUND_SUBREDDITS)
    url = f"https://www.reddit.com/r/{sub}/hot.json?limit=50"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            posts = res.json().get("data", {}).get("children", [])
            valid_images = []
            
            for post in posts:
                post_data = post.get("data", {})
                img_url = post_data.get("url", "")
                
                # Check for direct image URLs, excluding stickied and NSFW posts
                if (img_url.endswith(".jpg") or img_url.endswith(".png") or img_url.endswith(".jpeg")) \
                   and not post_data.get("stickied") \
                   and not post_data.get("over_18"):
                    valid_images.append(img_url)
            
            if valid_images:
                selected_url = random.choice(valid_images)
                img_res = requests.get(selected_url, headers=headers, timeout=10)
                if img_res.status_code == 200:
                    temp_path = "temp_bg.jpg"
                    img = Image.open(BytesIO(img_res.content)).convert("RGB")
                    img.save(temp_path)
                    return temp_path
    except Exception as e:
        print(f"⚠️ Failed to fetch Reddit background image: {e}")
    
    return None

# --- 4. GENERATION ENGINE ---
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

# --- 5. VIDEO RENDERING ENGINE ---
def render_video(slot_data, filename, duration=7):
    is_promo = slot_data["type"] == "promo"
    is_reddit = slot_data["type"] == "reddit"
    
    # Fetch live Reddit background image
    bg_image_path = fetch_random_reddit_image()
    
    if bg_image_path and os.path.exists(bg_image_path):
        bg = ImageClip(bg_image_path).with_duration(duration).resized(new_size=(1080, 1920))
    else:
        # Fallback dark color if image fetch fails
        bg_color = (255, 51, 75) if is_promo else (18, 22, 31)
        bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    
    # Format text overlay
    if is_reddit:
        r_data = slot_data["content"]
        full_text = f"[REDDIT WISDOM]\n\n{r_data['sub']} • Posted by {r_data['user']}\n⬆️ {r_data['upvotes']} Upvotes\n\n{r_data['text']}"
    else:
        content = slot_data["content"]
        prefix = slot_data["prefix"]
        full_text = f"{prefix}\"{content}\"" if not is_promo else f"{prefix}{content}"

    # Expanded dark backing shield to guarantee text readability over meme images
    text_bg = ColorClip(size=(1000, 1200), color=(0, 0, 0), duration=duration).with_opacity(0.75).with_position('center')

    # Expanded width (960px) and adjusted font size (32/36pt) to prevent text clipping
    txt_clip = TextClip(
        text=full_text, 
        font_size=32 if is_reddit else 36, 
        color='white', 
        method='caption', 
        size=(960, None)
    ).with_duration(duration).with_position('center')
    
    video = CompositeVideoClip([bg, text_bg, txt_clip])
    output_path = os.path.join(OUTPUT_DIR, filename)
    video.write_videofile(output_path, fps=24, codec="libx264")
    
    # Clean up temporary background image file
    if bg_image_path and os.path.exists(bg_image_path):
        try:
            os.remove(bg_image_path)
        except Exception:
            pass
            
    return output_path

# --- 6. UPLOAD TO LITTERBOX WITH USER-AGENT & DELAY ---
def upload_to_litterbox(video_path):
    print(f"☁️ Uploading {video_path} to Litterbox host...")
    with open(video_path, "rb") as f:
        data = {
            "reqtype": "fileupload",
            "time": "24h"
        }
        files = {
            "fileToUpload": f
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.post("https://litterbox.catbox.moe/resources/internals/api.php", data=data, files=files, headers=headers)
    
    if response.status_code == 200 and response.text.startswith("http"):
        direct_url = response.text.strip()
        print(f"✅ Upload complete: {direct_url}")
        print("⏳ Waiting 5 seconds for host propagation before sending to Buffer...")
        time.sleep(5)
        return direct_url
    else:
        raise Exception(f"Failed to upload video to Litterbox: Status {response.status_code} - {response.text}")

# --- 7. BUFFER GRAPHQL API SCHEDULER ---
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

# --- 8. MAIN PIPELINE ---
if __name__ == "__main__":
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"🚀 Generating daily batch for {tomorrow}...\n")

    slots = generate_daily_batch()

    print("\n📅 Rendering, hosting, and sending schedule requests to Buffer...")
    for idx, slot in enumerate(slots, start=1):
        file_name = f"tiktok_slot_{idx}.mp4"
        
        # 1. Render local video (fetches dynamic Reddit meme image + applies text margins)
        video_path = render_video(slot, file_name)
        
        # 2. Upload to Litterbox host
        public_url = upload_to_litterbox(video_path)
        
        # 3. Schedule post via Buffer GraphQL API
        scheduled_datetime = f"{tomorrow}T{slot['time']}:00.000Z"
        
        if slot["type"] == "reddit":
            caption_text = f"{slot['content']['sub']}: {slot['content']['text']}"
        elif slot["type"] == "promo":
            caption_text = slot["content"]
        else:
            caption_text = slot["content"]
            
        caption = f"{caption_text}\n\n#doomscrolldaily #brainrot #darkhumor #reddit #weather #fyp"
        
        schedule_to_buffer(public_url, caption, scheduled_datetime)

    print("\n🎉 All videos rendered, hosted via Litterbox, and queued in Buffer!")
