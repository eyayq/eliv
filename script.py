import os
import urllib.request
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from unidecode import unidecode

# Configuration (Tetap sesuai bawaan)
M3U_PERMANENT_DIR = "m3u_permanent"
SOURCES = [
    "https://raw.githubusercontent.com/eyayq/eliv/refs/heads/main/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/live2.m3u",
    "https://raw.githubusercontent.com/eyayq/eliv/refs/heads/main/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/live0.m3u",
    "https://raw.githubusercontent.com/eyayq/eliv/refs/heads/main/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/live1.m3u"
]
SOURCE_GROUPS = {
    SOURCES[0]: "👍🏻DONASI 085795119808👍🏻",
    SOURCES[1]: "👍🏻DONASI 085795119808👍🏻",
}
FINAL_M3U = "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/w/x/y/z/live1.m3u"
METADATA_JSON = "a/jeson.json"
DOWNLOAD_TIMEOUT = 15
DEFAULT_LOGO = ""

logging.basicConfig(filename='generate.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_dirs():
    os.makedirs(M3U_PERMANENT_DIR, exist_ok=True)

def fetch_m3u_urls(m3u_url):
    if not m3u_url: return []
    
    try:
        req = urllib.request.Request(m3u_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            urls = []
            lines = content.splitlines()
            
            current_group = SOURCE_GROUPS.get(m3u_url, "")
            temp_kodiprops = []
            temp_extvlcopts = []
            temp_inf = None

            for line in lines:
                line = line.strip()
                if not line or line.startswith('#EXTM3U'):
                    continue

                if line.startswith('#EXTGRP'):
                    current_group = line.split(':', 1)[1].strip() if ':' in line else current_group
                elif line.startswith('#KODIPROP'):
                    temp_kodiprops.append(line.split(':', 1)[1].strip() if ':' in line else "")
                elif line.startswith('#EXTVLCOPT'):
                    temp_extvlcopts.append(line.split(':', 1)[1].strip() if ':' in line else "")
                elif line.startswith('#EXTINF'):
                    # Simpan info metadata sementara
                    title = line.split(',', 1)[1].strip() if ',' in line else f"Video_{len(urls)+1}"
                    logo_match = re.search(r'tvg-logo\s*=\s*"([^"]+)"', line)
                    group_match = re.search(r'group-title\s*=\s*"([^"]+)"', line)
                    
                    temp_inf = {
                        "title": unidecode(title),
                        "logo": logo_match.group(1) if logo_match else DEFAULT_LOGO,
                        "group": group_match.group(1) if group_match else current_group
                    }
                elif not line.startswith('#'):
                    # Ini adalah baris URL
                    if temp_inf:
                        # Filter ekstensi (Tetap sesuai filter kamu)
                        if any(line.lower().split('?')[0].endswith(ext) for ext in ['.m3u8', '.php', '.mpd', '.flv', '.hls', '.ts', '.mp3', '.m3u', '.mkv', '.avc']):
                            urls.append({
                                "url": line,
                                "title": temp_inf["title"],
                                "logo": temp_inf["logo"],
                                "group": temp_inf["group"],
                                "kodiprops": list(temp_kodiprops),
                                "extvlcopts": list(temp_extvlcopts)
                            })
                    # Reset semua penampung setelah URL ditemukan
                    temp_inf = None
                    temp_kodiprops = []
                    temp_extvlcopts = []
            return urls
    except Exception as e:
        logging.error(f"Error fetching {m3u_url}: {e}")
        return []

def main():
    create_dirs()
    all_videos = []
    metadata = {}
    idn_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for source_idx, source_url in enumerate(SOURCES):
        video_data_list = fetch_m3u_urls(source_url)
        for idx, data in enumerate(video_data_list):
            video_id = f"video_{source_idx+1}_{idx+1}"
            data["source"] = f"source_{source_idx+1}"
            all_videos.append(data)
            metadata[video_id] = data

    try:
        with open(FINAL_M3U, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"# ⏰ Latest Updated: {idn_time}\n")
            f.write(f"# 🔄 Total Channels: {len(all_videos)}\n")
            f.write(f"# ❤️ Donate: https://trakteer.id/mybhianesse0\n")
            f.write(f"# ☕ Donate: https://sociabuzz.com/mybhianesse0/tribe\n")
            f.write(f"# 🌐 Web Drama: https://mmkywo.vercel.app\n")
            f.write(f"# 🌐 Web Animeversary: https://animeversary.vercel.app\n\n")
            
            # Header Donasi Permanen
            f.write('#EXTINF:-1 tvg-logo="https://viiip.kitashinsaku.com//0.php" group-title="❤️DONASI❤️",DANA OVO GOPAY 085795119808 \n')
            f.write('https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php\n')
            f.write('#EXTINF:-1 tvg-logo="https://viiip.kitashinsaku.com//0.php" group-title="❤️085795119808❤️",DANA OVO GOPAY \n')
            f.write('https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php\n\n')
            f.write('#EXTINF:-1 tvg-logo="https://viiip.kitashinsaku.com//0.php" group-title="☕JIKA ERROR☕",DANA OVO GOPAY 085795119808 \n')
            f.write('https://bhns.bhns.workers.dev/?url=http://tvq.tvx.org:80/CC///CC.php\n\n')            
            f.write('#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/apistech/project/refs/heads/main/logo/image_ch_rtv.png" group-title="☕JIKA ERROR☕",⚠️RTV⚠️ \n')
            f.write('#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha\n')
            f.write('#KODIPROP:inputstream.adaptive.license_key=https://terson.treshold.workers.dev/\n')
            f.write('#KODIPROP:inputstreamaddon=inputstream.adaptive\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36\n')
            f.write('https://cdnjkt913.transvision.co.id:1000/live/master/5/4028c68572841ba301729ce4a1343c17/manifest.mpd\n')
            f.write('#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/apistech/project/refs/heads/main/logo/imageCir_GTV-180x180_2025_11_06_13_07_56.jpg" group-title="☕JIKA ERROR☕",⚠️GTV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00k/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_sctv.png" group-title="☕JIKA ERROR☕",⚠️SCTV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00z/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_rcti.png" group-title="☕JIKA ERROR☕",⚠️RCTI⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00v/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_transtv.png" group-title="☕JIKA ERROR☕",⚠️TRANS TV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00x/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_antv.png" group-title="☕JIKA ERROR☕",⚠️ANTV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00d/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/apistech/project/refs/heads/main/logo/image_ch_indosiar.png" group-title="☕JIKA ERROR☕",⚠️INDOSIAR⚠️ \n')
            f.write('#KODIPROP:inputstream.adaptive.license_type=com.widevine.alpha\n')
            f.write('#KODIPROP:inputstream.adaptive.license_key=https://terson.treshold.workers.dev/\n')
            f.write('#KODIPROP:inputstreamaddon=inputstream.adaptive\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36\n')
            f.write('https://cdnjkt913.transvision.co.id:1000/live/master/1/4028c6856c3db2cc016cd6e773b02392/manifest.mpd\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_trans7.png" group-title="☕JIKA ERROR☕",⚠️TRANS 7⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00u/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://raw.githubusercontent.com/apistech/project/refs/heads/main/logo/imageCir_MNC-180x180_2025_11_06_13_06_02.jpg" group-title="☕JIKA ERROR☕",⚠️MNC TV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00y/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/imageCir_MDTV-180x180-CL_2025_10_08_13_01_28.jpg" group-title="☕JIKA ERROR☕",⚠️MDTV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a047/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTLSm75uUXEv7lK_uF9ud4R3M7i43j-j2mpLxXaZv_v4nF0cVRo1RB_MiY&s=10" group-title="☕JIKA ERROR☕",⚠️TVRI SPORT⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00n/index.m3u8\n')
            f.write('#EXTINF:-1 tvg-logo="https://images.indihometv.com/images/channels/image_ch_moji.png" group-title="☕JIKA ERROR☕",⚠️MOJI TV⚠️ \n')
            f.write('http://103.66.62.83:8000/play/a00i/index.m3u8\n')

            
            for v in all_videos:
                f.write(f"#EXTINF:-1 tvg-logo=\"{v['logo']}\" group-title=\"{v['group']}\",{v['title']}\n")
                for prop in v['kodiprops']:
                    f.write(f"#KODIPROP:{prop}\n")
                for opt in v['extvlcopts']:
                    f.write(f"#EXTVLCOPT:{opt}\n")
                f.write(f"{v['url']}\n")
                
        logging.info(f"Wrote {len(all_videos)} videos to {FINAL_M3U}")
    except Exception as e:
        logging.error(f"Error writing M3U: {e}")

    try:
        with open(METADATA_JSON, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving JSON: {e}")

if __name__ == "__main__":
    main()
