import requests
import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

# Source URLs from epgshare01
SOURCES = [
    "https://epgshare01.online/epgshare01/epg_ripper_NZ1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_SG1.xml.gz"
]

def process_epg():
    # TIP: Ensure IDs in channels.txt exactly match the source (e.g., SkySport1.nz)
    wanted_channels = set()
    try:
        with open('channels.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    wanted_channels.add(line)
    except FileNotFoundError:
        print("Error: channels.txt not found. Please create it first.")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_root = ET.Element("tv")
    new_root.set("generator-info-name", f"Sports-EPG Updated: {now}")

    # TIP: XMLTV requires all <channel> tags before all <programme> tags.
    # Mixing them causes TiviMate to only see the first country found.
    all_channels = []
    all_programmes = []

    for url in SOURCES:
        print(f"Downloading and filtering: {url}")
        try:
            response = requests.get(url, timeout=60)
            content = gzip.decompress(response.content)
            tree = ET.fromstring(content)
            
            for child in tree:
                if child.tag == 'channel':
                    cid = child.get('id')
                    if cid in wanted_channels:
                        all_channels.append(child)
                elif child.tag == 'programme':
                    cid = child.get('channel')
                    if cid in wanted_channels:
                        all_programmes.append(child)
        except Exception as e:
            print(f"Skipping {url} due to error: {e}")

    # TIP: Consolidate all channels at the top to fix parsing issues.
    for channel in all_channels:
        new_root.append(channel)
    for programme in all_programmes:
        new_root.append(programme)
                
    # Save standard XML
    tree = ET.ElementTree(new_root)
    ET.indent(tree, space="  ", level=0)
    tree.write("my_guide.xml", encoding="utf-8", xml_declaration=True)
    
    # TIP: TiviMate prefers .gz files—they load faster and save bandwidth.
    with gzip.open("my_guide.xml.gz", "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
        
    print(f"Done! Updated at {now}.")
    # TIP: If TiviMate doesn't update, use 'Clear EPG' in settings to flush cache.
    # TIP: Append ?1 to your URL in TiviMate to force a server-side refresh.

if __name__ == "__main__":
    process_epg()
