import feedparser
from bs4 import BeautifulSoup
from datetime import datetime

WORLD_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/?best-topics=world&post_type=best"
]

LOCAL_FEEDS = [
    "https://www.cbc.ca/cmlink/rss-news-canada-ottawa",
    "https://ottawacitizen.com/feed/"
]

def make_funny_and_snarky(title, original_summary):
    """Adds automated sarcastic commentary without external API hanging."""
    # Clean up summary text
    if not original_summary:
        original_summary = "No details provided, which is probably for the best."
        
    # Add a funny procedural twist based on keywords or just a cynical wrapper
    snarky_prefixes = [
        "In events everyone will completely forget by tomorrow: ",
        "Surprising absolutely no one, ",
        "Local timeline takes another weird turn: ",
        "Experts are baffled, but mostly just tired: "
    ]
    
    # Simple deterministic humor twist using the title length to pick a prefix
    chosen_prefix = snarky_prefixes[len(title) % len(snarky_prefixes)]
    return f"{chosen_prefix}{original_summary}"

def fetch_and_roast_feeds(feed_urls, limit=3):
    items = []
    for url in feed_urls:
        try:
            print(f"Reading feed: {url}")
            feed = feedparser.parse(url)
            for entry in feed.entries[:limit]:
                title = entry.get('title', 'No Title')
                raw_summary = BeautifulSoup(entry.get('summary', ''), "html.parser").get_text()
                if len(raw_summary) > 140:
                    raw_summary = raw_summary[:137] + "..."
                
                funny_summary = make_funny_and_snarky(title, raw_summary)
                
                items.append({
                    'title': title,
                    'link': entry.get('link', '#'),
                    'published': entry.get('published', datetime.now().strftime('%b %d, %Y')),
                    'summary': funny_summary
                })
        except Exception as e:
            print(f"Error parsing feed {url}: {e}")
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
    return html_output if html_output else "<p>The robots are currently taking a nap. Check back soon.</p>"

if __name__ == "__main__":
    print("Starting fast news scraper...")
    world_items = fetch_and_roast_feeds(WORLD_FEEDS, limit=3)
    local_items = fetch_and_roast_feeds(LOCAL_FEEDS, limit=3)
    
    world_html = generate_html_cards(world_items)
    local_html = generate_html_cards(local_items)
    
    print("Reading index.html template...")
    with open("index.html", "r", encoding="utf-8") as f:
        template = f.read()
        
    updated_html = template.replace('<!-- PYTHON SCRIPT INJECTS WORLD NEWS HERE -->', world_html)
    updated_html = updated_html.replace('<!-- PYTHON SCRIPT INJECTS LOCAL NEWS HERE -->', local_html)
    
    print("Writing updates to index.html...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(updated_html)
    
    print("Done! index.html successfully generated.")
