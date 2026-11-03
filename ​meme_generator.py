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
            
    return "My ex said she'd miss me, but her aim is getting better every single week."

# --- 2. HIGH-ENERGY TRACK AUTO-FETCHER ---
def fetch_background_music(output_audio_path="temp_music.mp3"):
    track_urls = [
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "https://upload.wikimedia.org/wikipedia/commons/transcoded/c/c4/Beethoven_Moonlight_1st_movement.ogg/Beethoven_Moonlight_1st_movement.ogg.mp3"
    ]
    try:
        urllib.request.urlretrieve(random.choice(track_urls), output_audio_path)
    except Exception:
        pass
    return output_audio_path

# --- 3. VIDEO COMPILER ---
def create_meme_video(text, output_video_path="meme_output.mp4"):
    width, height = 1080, 1920
    bg_color = (random.randint(2, 12), random.randint(2, 12), random.randint(2, 12))
    image = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(image)
    
    for _ in range(60):
        draw.point((random.randint(0, width), random.randint(0, height)), fill=(random.randint(0, 30),)*3)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except IOError:
        font = ImageFont.load_default()

    margin = 80
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

    total_height = len(lines) * 80
    y = (height - total_height) / 2
    for line in lines:
        bbox = font.getbbox(line)
        x = (width - (bbox[2] - bbox[0])) / 2
        draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += 80

    temp_img_path = "temp_meme.png"
    image.save(temp_img_path, "PNG")

    audio_path = fetch_background_music("temp_audio.mp3")
    image_clip = ImageClip(temp_img_path).set_duration(7.0)
    try:
        audio_clip = AudioFileClip(audio_path).subclip(0, 7.0)
        video_clip = image_clip.set_audio(audio_clip)
    except Exception:
        video_clip = image_clip

    video_clip.fps = 24
    video_clip.write_videofile(
        output_video_path, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None
    )
    
    for p in [temp_img_path, audio_path]:
        if os.path.exists(p):
            os.remove(p)
            
    return output_video_path

# --- 4. BUFFER API SENDER (MAPPED TO YOUR EXACT SECRETS) ---
def send_to_buffer(video_filename, caption):
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

    # Maps directly to your labeled GitHub secrets
    profile_mapping = {
        "TikTok": os.getenv("BUFFER_PROFILE_ID"),
        "Instagram": os.getenv("BUFFER_INSTAGRAM_PROFILE_ID"),
        "YouTube": os.getenv("BUFFER_YOUTUBE_PROFILE_ID")
    }

    for platform, channel_id in profile_mapping.items():
        if not channel_id:
            print(f"Skipping {platform}: Profile ID secret not found.")
            continue
            
        mutation = """
        mutation CreatePost($input: PostInput!) {
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
        
        payload = {
            "query": mutation,
            "variables": {
                "input": {
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
            }
        }
        
        try:
            response = requests.post(buffer_url, json=payload, headers=headers)
            result = response.json()
            print(f"Buffer response for {platform}: {result}")
        except Exception as e:
            print(f"Failed to push to Buffer for {platform}: {e}")

if __name__ == "__main__":
    print(f"Starting multi-AI batch execution at {datetime.now()}")
    for i in range(1, 3):
        meme_text = generate_meme_content()
        video_filename = f"meme_video_{i}.mp4"
        
        print(f"AI Joke #{i}: {meme_text}")
        create_meme_video(meme_text, video_filename)
        
        caption = f"{meme_text} 💀 #darkhumor #shorts #reels #trending"
        
        # Pushes to TikTok, Instagram, and YouTube queues via Buffer using your exact secrets
        send_to_buffer(video_filename, caption)
