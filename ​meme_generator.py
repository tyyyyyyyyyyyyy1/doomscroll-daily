import os
import random
import subprocess
import urllib.request
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy.editor import ImageClip, AudioFileClip

# --- 1. UNHINGED DARK HUMOR ENGINE (ZERO KEYS, HIGH-UPTIME PUBLIC ENDPOINTS) ---
def generate_meme_content(seed_modifier):
    # Free public AI generation endpoints that don't suffer from HF cold-start timeouts
    ai_endpoints = [
        "https://text.pollinations.ai/prompt/Write%20a%20single,%20extremely%20fucked%20up,%20brutally%20dark%20humor%20one-liner%20meme%20joke.%20Shocking,%20morbid,%20but%20funny.%20Keep%20under%15%20words.%20No%20intro.",
        "https://text.pollinations.ai/prompt/Write%20a%20short,%20unhinged%20dark%20humor%20joke%20about%20human%20misery%20for%20an%20edgy%20meme.%20Keep%20under%2015%20words."
    ]
    
    headers = {"Content-Type": "application/json"}
    random.shuffle(ai_endpoints)
    
    for url in ai_endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                joke = response.text.strip().replace('"', '')
                if len(joke) > 5:
                    return joke
        except Exception:
            continue
            
    # Fallback to Hugging Face API if Pollinations is busy
    hf_models = [
        "https://api-inference.huggingface.co/models/google/gemma-2-2b-it",
        "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct",
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
    ]
    prompt = "Write a single, extremely fucked up, brutally dark humor one-liner meme joke under 15 words. No intro."
    
    for model_url in hf_models:
        try:
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 40, "temperature": 0.95}}
            response = requests.post(model_url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    joke = data[0].get("generated_text", "").replace(prompt, "").strip()
                    if len(joke) > 5:
                        return joke
        except Exception:
            continue
            
    raise Exception("All public AI text generation sources failed or timed out.")

# --- 2. CASCADING AI IMAGE GENERATOR (AI SOURCES ONLY) ---
def generate_ai_meme_image(joke_text, output_image_path="temp_meme_img.jpg"):
    image_models = [
        "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell",
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0",
        "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
        "https://api-inference.huggingface.co/models/prompthero/openjourney"
    ]
    
    image_prompt = f"Dark humor visual meme about: {joke_text}. Cinematic, gritty lighting, highly detailed."
    random.shuffle(image_models)
    headers = {"Content-Type": "application/json"}
    
    for model_url in image_models:
        try:
            response = requests.post(model_url, headers=headers, json={"inputs": image_prompt}, timeout=12)
            if response.status_code == 200 and len(response.content) > 2000:
                with open(output_image_path, "wb") as f:
                    f.write(response.content)
                img = Image.open(output_image_path)
                img.verify()
                return output_image_path
        except Exception:
            continue
            
    raise Exception("All public AI image generation model sources failed or timed out.")

# --- 3. VOCAL-HEAVY PHONK / WITCHHOUSE / METAL AUDIO FETCHER ---
def fetch_background_music(output_audio_path="temp_music.mp3"):
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

# --- 4. TRUE MEME FORMAT VIDEO COMPILER ---
def create_meme_video(text, output_video_path="meme_output.mp4"):
    width, height = 1080, 1920
    
    canvas = Image.new("RGB", (width, height), color=(10, 10, 15))
    draw = ImageDraw.Draw(canvas)
    
    img_path = generate_ai_meme_image(text, "temp_meme_img.jpg")
    try:
        meme_img = Image.open(img_path).convert("RGB")
        meme_img = meme_img.resize((960, 960), Image.Resampling.LANCZOS)
        canvas.paste(meme_img, (60, 150))
    except Exception:
        pass

    draw.rectangle([60, 150, 1020, 1110], outline=(255, 255, 255), width=6)

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

# --- 5. GIT AUTO-COMMIT & PUSH HELPER ---
def git_commit_and_push(video_filename):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", video_filename], check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-upload generated meme {video_filename} [skip ci]"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Successfully committed and pushed {video_filename} to GitHub.")
    except Exception as e:
        print(f"Git commit/push failed: {e}")

# --- 6. BUFFER API SENDER ---
def send_to_buffer(video_filename, video_caption):
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
                    "title": video_caption[:90],
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
            "text": video_caption,
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
    print(f"Starting meme batch execution at {run_timestamp}")
    
    engaging_hooks = [
        "Unfiltered thoughts at 3 AM 💀",
        "We're going straight to hell for laughing at this...",
        "Tell me I'm wrong...",
        "Peak dark humor right here 🪦",
        "A little bit of morning trauma for your feed."
    ]
    
    for i in range(1, 3):
        meme_text = generate_meme_content(f"{run_timestamp}_{i}")
        video_filename = f"meme_{run_timestamp}_{i}.mp4"
        
        print(f"AI Unique Joke #{i}: {meme_text}")
        create_meme_video(meme_text, video_filename)
        
        git_commit_and_push(video_filename)
        
        hook = random.choice(engaging_hooks)
        tags = "#darkhumor #witchhouse #phonk #metal #trending"
        caption = f"{hook}\n\n{tags}"
        
        send_to_buffer(video_filename, caption)
