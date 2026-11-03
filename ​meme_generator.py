import os
import random
import urllib.request
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

# --- 1. MULTI-AI CASCADING DARK HUMOR ENGINE (ZERO KEYS) ---
def generate_meme_content():
    ai_models = [
        {"url": "https://api-inference.huggingface.co/models/google/gemma-2-2b-it", "format": "gemma"},
        {"url": "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct", "format": "llama"},
        {"url": "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta", "format": "zephyr"},
        {"url": "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct", "format": "qwen"}
    ]
    
    prompt = (
        "Write a single, extremely funny, brutally dark humor one-liner meme joke. "
        "Must be fully compliant with TikTok and YouTube community guidelines (no hate speech, slurs, or graphic self-harm, "
        "just clever, shocking, morbid dark humor). Keep it under 15 words. No intro text, just the joke."
    )
    
    random.shuffle(ai_models)
    headers = {"Content-Type": "application/json"}
    
    for model in ai_models:
        url = model["url"]
        fmt = model["format"]
        
        if fmt == "gemma":
            payload = {"inputs": f"<start_of_turn>user\n{prompt}<end_of_turn><start_of_turn>model", "parameters": {"max_new_tokens": 50, "temperature": 0.95}}
        elif fmt == "llama" or fmt == "qwen":
            payload = {"inputs": f"<|user|>\n{prompt}<|assistant|>", "parameters": {"max_new_tokens": 50, "temperature": 0.95}}
        else:
            payload = {"inputs": f"<|user|>\n{prompt}</s><|assistant|>", "parameters": {"max_new_tokens": 50, "temperature": 0.95}}
            
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
        "Even people who are good for nothing have the capacity to bring a smile to your face—like when you push them down the stairs."
    ]
    return random.choice(fallback_jokes)

# --- 2. DARK WITCHHOUSE & INDUSTRIAL METAL AUDIO FETCHER ---
def fetch_background_music(output_audio_path="temp_music.mp3"):
    # Curated heavy bass, phonk, industrial, and dark synth instrumental samples
    dark_audio_urls = [
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/1/11/Mozart_Requiem_Dies_irae.ogg/Mozart_Requiem_Dies_irae.ogg.mp3", # Dramatic dark choir/orchestral
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-15.mp3", # Heavy driving rhythm bass
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"  # Deep aggressive atmospheric synth
    ]
    try:
        urllib.request.urlretrieve(random.choice(dark_audio_urls), output_audio_path)
    except Exception:
        pass
    return output_audio_path

# --- 3. CONTEXT-MATCHED MEME VISUAL SELECTOR ---
def fetch_contextual_meme_image(joke_text, output_image_path="temp_meme_base.jpg"):
    text_lower = joke_text.lower()
    
    if any(word in text_lower for word in ["ex", "wife", "husband", "marriage", "girlfriend", "boyfriend"]):
        image_urls = [
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=1080&q=80",
            "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=1080&q=80"
        ]
    elif any(word in text_lower for word in ["fire", "burn", "warm", "match", "flame"]):
        image_urls = [
            "https://images.unsplash.com/photo-1508873696983-2df5c92063c7?w=1080&q=80",
            "https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=1080&q=80"
        ]
    elif any(word in text_lower for word in ["stairs", "push", "fall", "down", "stairs"]):
        image_urls = [
            "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=1080&q=80",
            "https://images.unsplash.com/photo-1516726817505-f5ed825624d8?w=1080&q=80"
        ]
    else:
        image_urls = [
            "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=1080&q=80",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1080&q=80"
        ]
    
    selected_url = random.choice(image_urls)
    try:
        urllib.request.urlretrieve(selected_url, output_image_path)
        img = Image.open(output_image_path)
        img.verify()
    except Exception:
        fallback = Image.new("RGB", (1080, 1920), color=(10, 10, 10))
        fallback.save(output_image_path, "JPEG")

# --- 4. VIDEO COMPILER WITH VISUALS & DARK AUDIO ---
def create_meme_video(text, output_video_path="meme_output.mp4"):
    width, height = 1080, 1920
    
    base_image_path = "temp_base.jpg"
    fetch_contextual_meme_image(text, base_image_path)
    
    try:
        base_img = Image.open(base_image_path).convert("RGB")
    except Exception:
        base_img = Image.new("RGB", (width, height), color=(10, 10, 10))
        
    base_img = base_img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Heavy cinematic dark gradient overlay
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 160))
    base_img.paste(Image.alpha_composite(base_img.convert("RGBA"), overlay).convert("RGB"))

    draw = ImageDraw.Draw(base_img)

    # Classic high-contrast white meme caption panel
    panel_box = [60, 200, width - 60, 700]
    draw.rounded_rectangle(panel_box, radius=24, fill=(255, 255, 255), outline=(0, 0, 0), width=6)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    margin = 100
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
    y = 450 - (total_text_height / 2)
    for line in lines:
        bbox = font.getbbox(line)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=font, fill=(0, 0, 0))
        y += 80

    final_img_path = "temp_final_meme.png"
    base_img.save(final_img_path, "PNG")

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
    
    for p in [base_image_path, final_img_path, audio_path]:
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
    print(f"Starting dark atmospheric multi-AI batch execution at {datetime.now()}")
    for i in range(1, 3):
        meme_text = generate_meme_content()
        video_filename = f"meme_video_{i}.mp4"
        
        print(f"AI Unique Context-Matched Joke #{i}: {meme_text}")
        create_meme_video(meme_text, video_filename)
        
        caption = f"{meme_text} 💀 #darkhumor #witchhouse #phonk #metal #shorts #reels"
        send_to_buffer(video_filename, caption, meme_text)
