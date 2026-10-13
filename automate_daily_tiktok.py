import os
import random
import subprocess
import time
import requests
from datetime import datetime, timedelta
from moviepy import TextClip, CompositeVideoClip, ColorClip

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID")
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 2. MASSIVE EXPANDED CONTENT LIBRARIES ---

THOUGHT_SUBJECTS = [
    "Your brain", "Every mirror you look into", "If animals could talk", 
    "If you clean a vacuum cleaner", "What if birds", "Is cereal technically",
    "If Cinderella's shoe fit perfectly", "Water isn't wet", "Your future self",
    "If you choke a smurf", "What was the best thing", "If tomato is a fruit",
    "Why do we say 'sleep like a baby'", "If a bald person works in a restaurant",
    "Does a straw have one hole", "If money doesn't grow on trees",
    "Why do we press harder on a remote", "If you drop soap on the floor",
    "Your shadow", "If fish get thirsty", "Wifi signals", "GPS voices",
    "The person who invented the alarm clock", "If doors could scream",
    "An ant carrying a potato chip", "Your skeleton", "Pigeons in parking lots",
    "The concept of time zones", "If statues blinked", "Refrigerators at 3 AM"
]

THOUGHT_TWISTS = [
    "named itself without your explicit consent.",
    "is slightly outdated by the speed of light.",
    "which one would be the most obnoxious?",
    "you instantly become a vacuum cleaner.",
    "are government drones charging on power lines?",
    "a cold soup served in a bowl of despair?",
    "why did it fall off her foot?",
    "wetness is just a condition water causes to other things.",
    "is watching you right now through your memories.",
    "what color does it turn under pressure?",
    "before sliced bread was invented?",
    "then ketchup is technically a smoothie.",
    "when babies wake up crying every two hours?",
    "do they still wear a hairnet?",
    "or does it technically have two holes?",
    "why do banks have branches?",
    "when the batteries are clearly dead?",
    "is the floor clean or is the soap dirty?",
    "is plotting your exact daily routine.",
    "do they drink the ocean or ignore it?",
    "are just invisible ghosts whispering to your phone.",
    "knows every wrong turn you've ever taken.",
    "must have been universally hated by humanity.",
    "when someone tries to slam them shut.",
    "is legally moving furniture without a permit.",
    "is trapped inside you wearing a meat suit.",
    "are plotting a hostile takeover of urban areas.",
    "was entirely made up to confuse travelers.",
    "only when nobody is looking directly at them.",
    "humming songs you forgot you even knew."
]

DARK_JOKES = [
    "My grandfather has the heart of a lion... and a lifetime ban from the local zoo.",
    "Give a man a match, and he’ll be warm for a few hours. Set a man on fire, and he will be warm for the rest of his life.",
    "I was digging in our garden and found a chest full of gold coins. I was about to run inside to tell my wife, but then I remembered why I was digging in the garden.",
    "Even people who are hard to get along with bring a lot of joy to the room... whenever they leave it.",
    "As I get older, I remember all the people I've lost along the way. Maybe a career as a tour guide wasn't for me.",
    "My wife told me to stop impersonating a flamingo. I had to put my foot down.",
    "Building a puzzle is all fun and games until you lose the last piece and realize the box art lied.",
    "A man walks into a library and asks the librarian, 'Do you have any books on paranoia?' She leans in close and whispers, 'They're right behind you.'",
    "I broke my hand playing poker last night. Turns out, holding a royal flush doesn't stop someone from hitting you with a folding chair.",
    "My boss told me to have a good day... so I went home.",
    "Never test the depth of the water with both feet. Unless you're already sinking, then it doesn't matter.",
    "Parallel lines have so much in common. It’s a shame they’ll never meet."
]

PROMO_HOOKS = [
    f"Tired of boring weather apps & fake news?\nCheck out The Doomscroll Daily 🌤️\n\n{PROMO_LINK}",
    f"Your daily dose of brain-rot & local reality.\nThe Doomscroll Daily dashboard is live! 🧠\n\n{PROMO_LINK}",
    f"Need a distraction from reality?\nExplore live streams, unhinged weather & memes:\n\n{PROMO_LINK}",
    f"Stop scrolling blindly. Get your daily dose of chaos at:\n\n{PROMO_LINK}",
    f"Why check 5 different apps when you can get your unhinged updates in one place?\n\n{PROMO_LINK}",
    f"The internet is getting boring. We fixed it.\nExplore the chaos feed live:\n\n{PROMO_LINK}",
    f"Weather reports, live feeds, and certified digital nonsense.\nCheck out the hub:\n\n{PROMO_LINK}",
    f"Your screen time is already ruined. Might as well make it count:\n\n{PROMO_LINK}"
]

def generate_daily_batch():
    day_seed = int(datetime.now().strftime('%j')) + (datetime.now().year * 100)
    random.seed(day_seed)
    
    thoughts = []
    used_thought_indices = set()
    while len(thoughts) < 3:
        subj_idx = random.randint(0, len(THOUGHT_SUBJECTS) - 1)
        twist_idx = random.randint(0, len(THOUGHT_TWISTS) - 1)
        pair = (subj_idx, twist_idx)
        if pair not in used_thought_indices:
            used_thought_indices.add(pair)
            thoughts.append(f"{THOUGHT_SUBJECTS[subj_idx]} {THOUGHT_TWISTS[twist_idx]}")
            
    joke = random.choice(DARK_JOKES)
    promos = random.sample(PROMO_HOOKS, 2)
    
    return [
        {"type": "thought", "prefix": "🧠 2 AM THOUGHT:\n\n", "time": "08:00", "content": thoughts[0]},
        {"type": "thought", "prefix": "💀 DARK HUMOR:\n\n",    "time": "11:00", "content": joke},
        {"type": "promo",   "prefix": "🚨 SITE ALERT:\n\n",    "time": "13:00", "content": promos[0]},
        {"type": "thought", "prefix": "🧠 2 AM THOUGHT:\n\n", "time": "16:00", "content": thoughts[1]},
        {"type": "thought", "prefix": "🧠 2 AM THOUGHT:\n\n", "time": "19:00", "content": thoughts[2]},
        {"type": "promo",   "prefix": "🚨 SITE ALERT:\n\n",    "time": "21:30", "content": promos[1]}
    ]

# --- 3. VIDEO RENDERING ENGINE ---
def render_video(text, prefix, filename, is_promo=False, duration=7):
    bg_color = (255, 51, 75) if is_promo else (18, 22, 31)
    bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    
    full_text = f"{prefix}\"{text}\""

    txt_clip = TextClip(
        text=full_text, 
        font_size=46, 
        color='white', 
        method='caption', 
        size=(900, None)
    ).with_duration(duration).with_position('center')
    
    video = CompositeVideoClip([bg, txt_clip])
    output_path = os.path.join(OUTPUT_DIR, filename)
    video.write_videofile(output_path, fps=24, codec="libx264")
    return output_path

# --- 4. UPLOAD TO LITTERBOX WITH CORRECT ENDPOINT ---
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
        # Corrected API endpoint URL with /resources/internals/api.php
        response = requests.post("https://litterbox.catbox.moe/resources/internals/api.php", data=data, files=files, headers=headers)
    
    if response.status_code == 200 and response.text.startswith("http"):
        direct_url = response.text.strip()
        print(f"✅ Upload complete: {direct_url}")
        print("⏳ Waiting 5 seconds for host propagation before sending to Buffer...")
        time.sleep(5)
        return direct_url
    else:
        raise Exception(f"Failed to upload video to Litterbox: Status {response.status_code} - {response.text}")

# --- 5. BUFFER GRAPHQL API SCHEDULER ---
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

# --- 6. MAIN PIPELINE ---
if __name__ == "__main__":
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"🚀 Generating procedural batch for {tomorrow}...\n")

    slots = generate_daily_batch()

    print("\n📅 Rendering, hosting, and sending schedule requests to Buffer...")
    for idx, slot in enumerate(slots, start=1):
        file_name = f"tiktok_slot_{idx}.mp4"
        is_promo = slot["type"] == "promo"
        
        # 1. Render local video
        video_path = render_video(slot["content"], slot["prefix"], file_name, is_promo=is_promo)
        
        # 2. Upload to Litterbox with correct endpoint, User-Agent, and pause 5 seconds
        public_url = upload_to_litterbox(video_path)
        
        # 3. Schedule post via Buffer API
        scheduled_datetime = f"{tomorrow}T{slot['time']}:00.000Z"
        caption = f"{slot['content']}\n\n#doomscrolldaily #brainrot #darkhumor #weather #fyp"
        
        schedule_to_buffer(public_url, caption, scheduled_datetime)

    print("\n🎉 All videos rendered, hosted via Litterbox, and queued in Buffer!")
