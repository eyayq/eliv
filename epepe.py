import requests
import time
import base64
import hashlib
import os
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor

# ===============================
# API CONFIG
# ===============================

BASE_URL = "https://api-ls.cdnokvip.com/api/get-livestream-group"
DETAIL_URL = "https://api-ls.cdnokvip.com/api/match-detail-slug?slug="
SCORE_API = "https://www.thesportsdb.com/api/v1/json/3/livescore.php?s=Soccer"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://cd.okvip.com/"
}

WIB = timezone(timedelta(hours=7))

# ===============================
# 🔐 ENCRYPT CONFIG
# ===============================

SECRET_KEY = "VIP_SECRET_2026"
PLAY_ROUTE = "https://viiip.kitashinsaku.com/play.php"

def encrypt_url(url):
    if ".m3u8" in url.lower():
        return url

    current_time = int(time.time())
    expire_time = current_time + 3600  # 1 jam

    random_salt = os.urandom(8).hex()
    encoded_url = base64.urlsafe_b64encode(url.encode()).decode()

    raw = f"{encoded_url}{expire_time}{random_salt}{SECRET_KEY}"
    signature = hashlib.sha256(raw.encode()).hexdigest()

    return (
        f"{PLAY_ROUTE}"
        f"?data={encoded_url}"
        f"&expire={expire_time}"
        f"&salt={random_salt}"
        f"&sig={signature}"
    )

# ===============================
# UTIL
# ===============================

def fetch_json(url, params=None):
    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=8)
            if r.status_code == 200:
                return r.json()
        except:
            time.sleep(1)
    return None


def get_match_state(timestamp):
    now = datetime.now(WIB).timestamp()
    diff = timestamp - now

    if diff > 0:
        return "UPCOMING"
    if -7200 <= diff <= 0:
        return "LIVE"
    return "FINISHED"


def format_match_timer(timestamp):
    now = datetime.now(WIB).timestamp()
    diff = int(timestamp - now)

    if diff > 0:
        h = diff // 3600
        m = (diff % 3600) // 60
        s = diff % 60
        return f"⏳ {h:02d}h {m:02d}m {s:02d}s"

    if -7200 <= diff <= 0:
        return "🔴 LIVE"

    return "✅ Finished"


def get_upcoming_label(timestamp):
    match_dt = datetime.fromtimestamp(timestamp, WIB)
    now = datetime.now(WIB)

    if match_dt.date() == now.date():
        return "🗓 TODAY"
    if match_dt.date() == (now + timedelta(days=1)).date():
        return "🗓 TOMORROW"

    return f"🗓 {match_dt.strftime('%d-%m-%Y')}"

# ===============================
# LIVE SCORE
# ===============================

def get_live_scores():
    data = fetch_json(SCORE_API)
    scores = {}

    if not data or "events" not in data:
        return scores

    for e in data["events"]:
        home = e.get("strHomeTeam")
        hs = e.get("intHomeScore")
        aw = e.get("intAwayScore")

        if home and hs is not None:
            scores[home.lower()] = f"⚽ {hs}-{aw}"

    return scores

# ===============================
# STREAM EXTRACTION
# ===============================

def extract_stream_links(obj):
    allowed = (".m3u8", ".flv", ".mp4", ".ts")
    links = []

    def walk(data):
        if isinstance(data, dict):
            for v in data.values():
                walk(v)
        elif isinstance(data, list):
            for i in data:
                walk(i)
        elif isinstance(data, str):
            u = data.strip()
            if u.lower().startswith("http") and any(ext in u.lower() for ext in allowed):
                links.append(u.replace("\\/", "/"))

    walk(obj)
    return list(dict.fromkeys(links))

# ===============================
# FETCH MATCH LIST
# ===============================

def get_all_matches():
    offset = 0
    limit = 8
    max_channels = 50
    matches = []
    seen = set()

    while len(matches) < max_channels:
        params = {
            "offset": offset,
            "limit": limit,
            "isHot": "false",
            "isLive": "false",
            "isToday": "false",
            "isTomorrow": "false"
        }

        data = fetch_json(BASE_URL, params)
        if not data:
            break

        datas = data.get("value", {}).get("datas", [])
        if not datas:
            break

        for m in datas:
            slug = m.get("slugUrl")
            if slug and slug not in seen:
                seen.add(slug)
                matches.append(m)

                if len(matches) >= max_channels:
                    break

        offset += limit

    return matches


def get_detail(slug):
    data = fetch_json(DETAIL_URL + slug)
    if not data:
        return None

    if data.get("value", {}).get("success") is not True:
        return None

    return data.get("value", {}).get("datas")

# ===============================
# BUILD M3U
# ===============================

def build_m3u(matches):
    output = ["#EXTM3U"]
    grouped = {}
    live_scores = get_live_scores()

    slug_list = [m.get("slugUrl") for m in matches if m.get("slugUrl")]

    with ThreadPoolExecutor(max_workers=10) as executor:
        detail_results = list(executor.map(get_detail, slug_list))

    for detail in detail_results:
        if not detail:
            continue

        match_time = detail.get("matchTime")
        if not isinstance(match_time, (int, float)):
            continue

        state = get_match_state(match_time)
        if state == "FINISHED":
            continue

        home = detail.get("homeName", "Home")
        away = detail.get("awayName", "Away")
        logo = detail.get("homeLogo", "")

        score = ""
        for team_key in live_scores:
            if home.lower() in team_key:
                score = live_scores[team_key]
                break

        timer = format_match_timer(match_time)
        title = f"{home} vs {away} | {score} | {timer}" if score else f"{home} vs {away} | {timer}"

        group_name = "😈LIVE-NOW😈" if state == "LIVE" else get_upcoming_label(match_time)

        links = extract_stream_links(detail)
        if not links:
            continue

        for i, link in enumerate(links, 1):
            entry = [
                f'#EXTINF:-1 group-title="{group_name}" tvg-logo="{logo}",{title} [Stream {i}]',
                encrypt_url(link)
            ]
            grouped.setdefault(group_name, []).append(
                ("\n".join(entry), match_time)
            )

    for g in grouped:
        if "🗓" in g:
            grouped[g] = sorted(grouped[g], key=lambda x: x[1])

    for group in sorted(
        grouped.keys(),
        key=lambda x: (
            0 if "LIVE-NOW" in x else
            1 if "🗓 TODAY" in x else
            2 if "🗓 TOMORROW" in x else
            3,
            x
        )
    ):
        if "LIVE-NOW" in group:
            donation = (
                f'#EXTINF:-1 group-title="{group}" '
                f'tvg-logo="https://viiip.kitashinsaku.com/0.php",'
                f'😎 DONASI DANA OVO GOPAY 085795119808 😎\n'
                f'https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php'
            )
            output.append(donation)

        for item in grouped[group]:
            output.append(item[0])

    return "\n".join(output)

# ===============================
# RUN
# ===============================

def scrape_once():
    matches = get_all_matches()
    m3u = build_m3u(matches)

    with open("bhns0.m3u", "w", encoding="utf-8") as f:
        f.write(m3u)


if __name__ == "__main__":
    scrape_once()
