import os
import random
import urllib.request
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip

# --- 1. UNHINGED BRUTAL DARK HUMOR ENGINE (ZERO KEYS) ---
def generate_meme_content(seed_modifier):
    ai_models = [
        {"url": "https://api-inference.huggingface.co/models/google/gemma-2-2b-it", "format": "gemma"},
        {"url": "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct", "format": "llama"},
        {"url": "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta", "format": "zephyr"},
        {"url": "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct", "format": "qwen"}
    ]
    
    prompts = [
        "Write a single, extremely fucked up, brutally dark humor one-liner meme joke. Shocking, morbid, but undeniably funny. Keep under 15 words. No intro text.",
        "Write a short, unhinged dark humor joke about tragedy or human misery suitable for an edgy meme. Keep under 15 words. No intro text.",
        "Write a morbid, highly inappropriate yet hilarious dark humor one-liner. Keep under 15 words. No intro text."
    ]
    
    prompt = random.choice(prompts)
    random.shuffle(ai_models)
    headers = {"Content-Type": "application/json"}
    
    for model in ai_models:
        url = model["url"]
        fmt = model["format"]
        temp = round(random.uniform(0.92, 0.99), 2)
        
        if fmt == "gemma":
            payload = {"inputs": f"<start_of_turn>user\n{prompt} (ID: {seed_modifier})<end_of_turn><start_of_turn>model", "parameters": {"max_new_tokens": 50, "temperature": temp}}
        elif fmt == "llama" or fmt == "qwen":
            payload = {"inputs": f"<|user|>\n{prompt} (ID: {seed_modifier})<|assistant|>", "parameters": {"max_new_tokens": 50, "temperature": temp}}
        else:
            payload = {"inputs": f"<|user|>\n{prompt} (ID: {seed_modifier})</s><|assistant|>", "parameters": {"max_new_tokens": 50, "temperature": temp}}
            
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    raw_text = data[0].get("generated_text", "")
                    joke = raw_text.split("<|assistant|>")[-1].split("<end_of_turn>")[-1].strip()
                    if len(joke) > 5:
                        return joke
        except Exception:
            continue
            
    fallback_jokes = [
        "My ex said she'd miss me, but her aim is getting better every single week.",
        "Give a man a match, and he’ll be warm for a few hours. Set a man on fire, and he will be warm for the rest of his life.",
        "Even people who are good for nothing have the capacity to bring a smile to your face—like when you push them down the stairs.",
        "My grandfather has the heart of a lion... and a lifetime ban from the city zoo."
    ]
    return random.choice(fallback_jokes)

# --- 2. VOCAL-HEAVY PHONK / WITCHHOUSE / METAL AUDIO FETCHER ---
def fetch_background_music(output_audio_path="temp_music.mp3"):
    # Curated streams featuring aggressive vocal cuts, heavy bass, and phonk/metal instrumentation
    dark_vocal_audio_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/11/Mozart_Requiem_Dies_irae.ogg/Mozart_Requiem_Dies_irae.ogg.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-10.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-16.mp3"
    ]
    try:
        urllib.request.urlretrieve(random.choice(dark_vocal_audio_urls), output_audio_path)
    except Exception:
        pass
    return output_audio_path

# --- 3. RELEVANT MEME IMAGE FETCHER MAPPED TO JOKE THEMES ---
def fetch_meme_image(joke_text, output_image_path="temp_meme_img.jpg"):
    text_lower = joke_text.lower()
    
    # Highly relevant visual theme mapping
    if any(word in text_lower for word in ["ex", "wife", "husband", "marriage", "girlfriend", "boyfriend", "heart"]):
        # Unhinged / Psycho relationship reaction imagery
        image_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama_%28cropped%29.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
        ]
    elif any(word in text_lower for word in ["fire", "burn", "warm", "match", "flame"]):
        # Chaos & Fire imagery
        image_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/1/12/Fire_breathing_at_Edinburgh_Hogmanay_2009.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/3/36/Bonfire_at_Yule.jpg"
        ]
    elif any(word in text_lower for word in ["stairs", "push", "fall", "down", "zoo", "animal"]):
        # Dark mishap / wild concepts
        image_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/f/f8/Dark_stairwell.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/9/91/Staircase_isometric.png"
        ]
    else:
        # Dark absurdist reaction pool
        image_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/5/5a/A_small_cup_of_coffee.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/b/b6/Image_created_with_a_mobile_phone.png"
        ]
        
    selected_url = random.choice(image_urls)
    try:
        urllib.request.urlretrieve(selected_url, output_image_path)
        img = Image.open(output_image_path)
        img.verify()
    except Exception:
        fallback = Image.new("RGB", (1080, 1080), color=(20, 20, 25))
        fallback.save(output_image_path, "JPEG")

# --- 4. TRUE MEME FORMAT VIDEO COMPILER ---
def create_meme_video(text, output_video_path="meme_output.mp4"):
    width, height = 1080, 1920
    
    # Deep obsidian vertical background canvas (9:16)
    canvas = Image.new("RGB", (width, height), color=(10, 10, 15))
    draw = ImageDraw.Draw(canvas)
    
    # Fetch and paste the context-relevant meme image into the top frame window
    img_path = "temp_img.jpg"
    fetch_meme_image(text, img_path)
    try:
        meme_img = Image.open(img_path).convert("RGB")
        meme_img = meme_img.resize((960, 960), Image.Resampling.LANCZOS)
        canvas.paste(meme_img, (60, 150))
    except Exception:
        pass

    # Clean framing border around the reaction image
    draw.rectangle([60, 150, 1020, 1110], outline=(0, 0, 0), width=10)

    # Classic high-contrast white caption box below the image
    panel_box = [60, 1200, 1020, 1750]
    draw.rounded_rectangle(panel_box, radius=25, fill=(255, 255, 255), outline=(0, 0, 0), width=8)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    margin = 110
    max_width = width - (margin * 2)
    lines, current_line = [], ""
    for word in text.split():
        test_line = f"{current_line} {word}".strip()
        bbox = font.getbbox(test_line)
        if (bbox[2] - bbox[0]) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    total_text_height = len(lines) * 80
    y = 1475 - (total_text_height / 2)
    for line in lines:
        bbox = font.getbbox(line)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font, fill=(0, 0, 0))
        y += 80

    final_img_path = "temp_final_meme.png"
    canvas.save(final_img_path, "PNG")

    # Compile video with vocal-heavy dark audio track
    audio_path = fetch_background_music("temp_audio.mp3")
    image_clip = ImageClip(final_img_path).set_duration(7.0)
    
    try:
        audio_clip = AudioFileClip(audio_path).subclip(0, 7.0)
        video_clip = image_clip.set_audio(audio_clip)
    except Exception:
        video_clip = image_clip

    video_clip.fps = 24
    video_clip.write_videofile(
        output_video_path, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None
    )
    
    for p in [img_path, final_img_path, audio_path]:
        if os.path.exists(p):
            os.remove(p)
            
    return output_video_path

# --- 5. BUFFER API SENDER ---
def send_to_buffer(video_filename, caption, meme_text):
    token = os.getenv("BUFFER_ACCESS_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    
    if not token or not repo:
        print("Buffer token or repository info missing. Skipping API push.")
        return

    public_video_url = f"https://raw.githubusercontent.com/{repo}/main/{video_filename}"
    buffer_url = "https://api.buffer.com"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    profile_mapping = {
        "TikTok": os.getenv("BUFFER_PROFILE_ID"),
        "Instagram": os.getenv("BUFFER_INSTAGRAM_PROFILE_ID"),
        "YouTube": os.getenv("BUFFER_YOUTUBE_PROFILE_ID")
    }

    for platform, channel_id in profile_mapping.items():
        if not channel_id:
            print(f"Skipping {platform}: Profile ID secret not found.")
            continue
            
        metadata_dict = {}
        if platform == "Instagram":
            metadata_dict = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
        elif platform == "YouTube":
            metadata_dict = {
                "youtube": {
                    "title": meme_text[:95],
                    "categoryId": "23"
                }
            }

        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
          createPost(input: $input) {
            ... on PostActionSuccess {
              post {
                id
                dueAt
              }
            }
            ... on MutationError {
              message
            }
          }
        }
        """
        
        post_input = {
            "text": caption,
            "channelId": channel_id.strip(),
            "schedulingType": "automatic",
            "mode": "addToQueue",
            "assets": [
                {
                    "video": {
                        "url": public_video_url
                    }
                }
            ]
        }
        
        if metadata_dict:
            post_input["metadata"] = metadata_dict

        payload = {
            "query": mutation,
            "variables": {
                "input": post_input
            }
        }
        
        try:
            response = requests.post(buffer_url, json=payload, headers=headers)
            result = response.json()
            print(f"Buffer response for {platform}: {result}")
        except Exception as e:
            print(f"Failed to push to Buffer for {platform}: {e}")

if __name__ == "__main__":
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting unhinged dark meme batch execution at {run_timestamp}")
    
    for i in range(1, 3):
        meme_text = generate_meme_content(f"{run_timestamp}_{i}")
        video_filename = f"meme_{run_timestamp}_{i}.mp4"
        
        print(f"AI Unique Brutal Joke #{i}: {meme_text}")
        create_meme_video(meme_text, video_filename)
        
        caption = f"{meme_text} 💀 #darkhumor #witchhouse #phonk #metal #shorts #reels"
        send_to_buffer(video_filename, caption, meme_text)
