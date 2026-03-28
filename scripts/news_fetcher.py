#!/usr/bin/env python3
"""ARIA LIVE THREAT FEED — RSS news fetcher for game piracy intelligence."""
import urllib.request, json, re, time, os
from datetime import datetime

RSS_FEEDS = [
    ('https://torrentfreak.com/feed/', 'TorrentFreak'),
    ('https://www.gamesindustry.biz/feed', 'GamesIndustry'),
    ('https://www.ipwatchdog.com/feed/', 'IPWatchdog'),
    ('https://krebsonsecurity.com/feed/', 'KrebsOnSecurity'),
]

def fetch_rss(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 ARIA-Bot/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [WARN] {url}: {e}")
        return None

def parse_rss(xml, source):
    items = []
    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', xml, re.DOTALL)
    links = re.findall(r'<link>(.*?)</link>|<link[^>]+href="([^"]+)"', xml)
    descs = re.findall(r'<description><!\[CDATA\[(.*?)\]\]></description>|<description>(.*?)</description>|<summary>(.*?)</summary>', xml, re.DOTALL)
    dates = re.findall(r'<pubDate>(.*?)</pubDate>|<published>(.*?)</published>|<updated>(.*?)</updated>', xml)
    for i, tm in enumerate(titles[1:], 0):
        title = (tm[0] or tm[1]).strip()
        if not title or len(title) < 5: continue
        link = (links[min(i,len(links)-1)][0] or links[min(i,len(links)-1)][1]).strip() if i < len(links) else ''
        desc = re.sub(r'<[^>]+>', '', (descs[i][0] or descs[i][1] or (descs[i][2] if len(descs[i])>2 else '') if i < len(descs) else '')).strip()[:300]
        date = (dates[i][0] or dates[i][1] or dates[i][2]).strip() if i < len(dates) else ''
        items.append({'title': title, 'link': link, 'description': desc, 'date': date, 'source': source})
    return items[:20]

HIGH_KW = ['piracy','pirate','crack','dmca','denuvo','warez','takedown','seized','arrested']
MID_KW = ['copyright','torrent','drm','rom','emulator','intellectual property']
GAME_KW = ['game','gaming','video game','console','pc game','steam','nintendo','playstation','xbox']

def score(item):
    text = (item['title'] + ' ' + item['description']).lower()
    s = 0; matched = []
    for kw in HIGH_KW:
        if kw in text: s += 3; matched.append(kw)
    for kw in MID_KW:
        if kw in text: s += 1; matched.append(kw)
    for kw in GAME_KW:
        if kw in text: s += 2; break
    item['relevance_score'] = s
    item['matched_keywords'] = list(set(matched))
    return s

def main():
    print(f"ARIA News Fetcher — {datetime.now().isoformat()}")
    all_items = []
    for url, name in RSS_FEEDS:
        print(f"  Fetching {name}...")
        content = fetch_rss(url)
        if content:
            items = parse_rss(content, name)
            all_items.extend(items)
            print(f"    {len(items)} items")
        time.sleep(1)

    print(f"Total: {len(all_items)} items")
    for item in all_items:
        score(item)

    relevant = sorted([i for i in all_items if i['relevance_score'] >= 2], key=lambda x: -x['relevance_score'])
    seen = set(); deduped = []
    for item in relevant:
        key = item['title'][:30].lower()
        if key not in seen: seen.add(key); deduped.append(item)

    final = deduped[:30]
    print(f"Relevant (score 2+): {len(final)} items")

    # Write JS data file
    output_path = os.path.join(os.path.dirname(__file__), '..', 'news_data.js')
    output = f"""// [LIVE DATA] Game piracy news — auto-fetched {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
const ARIA_NEWS = {{
  fetched_at: "{datetime.now().isoformat()}",
  item_count: {len(final)},
  items: {json.dumps(final, ensure_ascii=False, indent=2)}
}};
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
    print(f"Saved to {output_path} ({len(final)} items)")

if __name__ == '__main__':
    main()
