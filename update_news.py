import os
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from google import genai

# Initialize the Gemini client (It reads your free API key from GitHub Secrets automatically)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

WORLD_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"
]

LOCAL_FEEDS = [
    "https://www.cbc.ca/cmlink/rss-news-canada-ottawa",
    "https://ottawacitizen.com/feed/"
]

def make_funny_and_snarky(title, original_summary):
    """Uses free Gemini model to add a funny, sarcastic twist to the news."""
    prompt = f"""
    You are a cynical, darkly funny, sarcastic internet comedian writing for a satirical automated news site called 'The Doomscroll Daily'.
    
    Take this news item and rewrite the summary into 1 or 2 short sentences. Make it funny, humorous, slightly mocking of humanity or the situation, but still clear on what actually happened. Keep it punchy.
    
    Headline: {title}
    Original Text: {original_summary}
    
    Funny Rewrite:
    """
    try:
        # Using gemini-3.8-flash which is fast and supports the free tier
        response = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI Humor Error: {e}")
        return original_summary # Fallback if API fails

def fetch_and_roast_feeds(feed_urls, limit=3):
    items = []
    for url in feed_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                title = entry.get('title', 'No Title')
                raw_summary = BeautifulSoup(entry.get('summary', ''), "html.parser").get_text()
                
                print(f"Roasting: {title[:40]}...")
                funny_summary = make_funny_and_snarky(title, raw_summary)
                
                items.append({
                    'title': title,
                    'link': entry.get('link', '#'),
                    'published': entry.get('published', datetime.now().strftime('%b %d, %Y')),
                    'summary': funny_summary
                })
        except Exception as e:
            print(f"Error parsing {url}: {e}")
    return items

def generate_html_cards(items):
    html_output = ""
    for item in items:
        html_output += f"""
        <div class="news-card">
            <span class="news-date">{item['published']}</span>
            <h3><a href="{item['link']}" target="_blank">{item['title']}</a></h3>
            <p>{item['summary']}</p>
        </div>
        """
    return html_output if html_output else "<p>The robots are currently on a coffee break. Check back soon.</p>"

if __name__ == "__main__":
    print("Fetching and roasting world news...")
    world_items = fetch_and_roast_feeds(WORLD_FEEDS, limit=3)
    
    print("Fetching and roasting local Ottawa news...")
    local_items = fetch_and_roast_feeds(LOCAL_FEEDS, limit=3)
    
    world_html = generate_html_cards(world_items)
    local_html = generate_html_cards(local_items)
    
    with open("index.html", "r", encoding="utf-8") as f:
        template = f.read()
        
    updated_html = template.replace('<!-- PYTHON SCRIPT INJECTS WORLD NEWS HERE -->', world_html)
    updated_html = updated_html.replace('<!-- PYTHON SCRIPT INJECTS LOCAL NEWS HERE -->', local_html)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(updated_html)
    
    print("Successfully updated index.html with roasted news!")
