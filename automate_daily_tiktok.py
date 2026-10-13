import os
import random
import subprocess
import requests
from datetime import datetime, timedelta
from moviepy import TextClip, CompositeVideoClip, ColorClip

# --- 1. CONFIGURATION ---
BUFFER_ACCESS_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_PROFILE_ID = os.getenv("BUFFER_PROFILE_ID")
PROMO_LINK = "https://tinyurl.com/DoomscrollDaily"

OUTPUT_DIR = "daily_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 2. INFINITE PROCEDURAL THOUGHT ENGINE ---
THOUGHT_SUBJECTS = [
    "Your brain", "Every mirror you look into", "If animals could talk", 
    "If you clean a vacuum cleaner", "What if birds", "Is cereal technically",
    "If Cinderella's shoe fit perfectly", "Water isn't wet", "Your future self",
    "If you choke a smurf", "What was the best thing", "If tomato is a fruit",
    "Why do we say 'sleep like a baby'", "If a bald person works in a restaurant",
    "Does a straw have one hole", "If money doesn't grow on trees",
    "Why do we press harder on a remote", "If you drop soap on the floor"
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
    "is the floor clean or is the soap dirty?"
]

PROMO_HOOKS = [
    f"Tired of boring weather apps & fake news?\nCheck out The Doomscroll Daily 🌤️\n\n{PROMO_LINK}",
    f"Your daily dose of brain-rot & local reality.\nThe Doomscroll Daily dashboard is live! 🧠\n\n{PROMO_LINK}",
    f"Need a distraction from reality?\nExplore live streams, unhinged weather & memes:\n\n{PROMO_LINK}",
    f"Stop scrolling blindly. Get your daily dose of chaos at:\n\n{PROMO_LINK}"
]

def generate_daily_batch():
    day_seed = int(datetime.now().strftime('%j')) + datetime.now().year
    random.seed(day_seed)
    
    thoughts = []
    used_indices = set()
    while len(thoughts) < 4:
        subj_idx = random.randint(0, len(THOUGHT_SUBJECTS) - 1)
        twist_idx = random.randint(0, len(THOUGHT_TWISTS) - 1)
        pair = (subj_idx, twist_idx)
        if pair not in used_indices:
            used_indices.add(pair)
            thoughts.append(f"{THOUGHT_SUBJECTS[subj_idx]} {THOUGHT_TWISTS[twist_idx]}")
            
    promos = random.sample(PROMO_HOOKS, 2)
    
    return [
        {"type": "thought", "time": "08:00", "content": thoughts[0]},
        {"type": "thought", "time": "11:00", "content": thoughts[1]},
        {"type": "promo",   "time": "13:00", "content": promos[0]},
        {"type": "thought", "time": "16:00", "content": thoughts[2]},
        {"type": "thought", "time": "19:00", "content": thoughts[3]},
        {"type": "promo",   "time": "21:30", "content": promos[1]}
    ]

# --- 3. VIDEO RENDERING ENGINE ---
def render_video(text, filename, is_promo=False, duration=7):
    bg_color = (255, 51, 75) if is_promo else (18, 22, 31)
    bg = ColorClip(size=(1080, 1920), color=bg_color, duration=duration)
    
    prefix = "🚨 SITE ALERT:\n\n" if is_promo else "🧠 2 AM THOUGHT:\n\n"
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

# --- 4. AUTO-COMMIT TO REPO ---
def commit_and_push_videos():
    """Commits and pushes generated videos back to GitHub so they have permanent public URLs."""
    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", OUTPUT_DIR], check=True)
    subprocess.run(["git", "commit", "-m", "🤖 Add daily automated TikTok video batch"], check=True)
    subprocess.run(["git", "push"], check=True)

# --- 5. BUFFER GRAPHQL API SCHEDULER ---
def schedule_to_buffer(video_url, caption, scheduled_at_iso):
    url = "https://api.buffer.com"
    headers = {
        "Authorization": f"Bearer {BUFFER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    mutation = """
    mutation CreatePost($input: PostInput!) {
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
                "videos": [{"url": video_url}]
            }
        }
    }

    response = requests.post(url, json={"query": mutation, "variables": variables}, headers=headers)
    res_data = response.json()
    
    if response.status_code == 200 and "errors" not in res_data:
        print(f"✅ Successfully scheduled for {scheduled_at_iso}")
    else:
        print(f"❌ Buffer API Error: {response.status_code} - {res_data}")

# --- 6. MAIN PIPELINE ---
if __name__ == "__main__":
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"🚀 Generating procedural batch for {tomorrow}...\n")

    slots = generate_daily_batch()
    rendered_slots = []

    for idx, slot in enumerate(slots, start=1):
        file_name = f"tiktok_slot_{idx}.mp4"
        is_promo = slot["type"] == "promo"
        
        video_path = render_video(slot["content"], file_name, is_promo=is_promo)
        rendered_slots.append((video_path, slot))
        print(f"Slot #{idx} ({slot['time']}) created successfully.")

    # Push videos to GitHub to generate public raw URLs
    print("\n📦 Committing videos to repository for public URLs...")
    commit_and_push_videos()

    # Get repository name dynamically from git remote or hardcode your username/repo
    repo_owner_repo = "tyyyyy/doomscroll-daily" 

    print("\n📅 Sending schedule requests to Buffer...")
    for video_path, slot in rendered_slots:
        file_name = os.path.basename(video_path)
        public_url = f"https://raw.githubusercontent.com/{repo_owner_repo}/main/{OUTPUT_DIR}/{file_name}"
        scheduled_datetime = f"{tomorrow}T{slot['time']}:00.000Z"
        caption = f"{slot['content']}\n\n#doomscrolldaily #brainrot #funny #weather #fyp"
        
        schedule_to_buffer(public_url, caption, scheduled_datetime)

    print("\n🎉 All videos rendered, pushed, and queued in Buffer!")
