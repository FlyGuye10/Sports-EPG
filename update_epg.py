import requests
import gzip
import xml.etree.ElementTree as ET

# Add the source URLs you need from epgshare01
SOURCES = [
    "https://epgshare01.online/epgshare01/epg_ripper_US1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_MY1.xml.gz"
]

def process_epg():
    # Load your desired channel IDs, skipping comments (#) and empty lines
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

    new_root = ET.Element("tv")
    
    for url in SOURCES:
        print(f"Downloading and filtering: {url}")
        try:
            response = requests.get(url, timeout=60)
            content = gzip.decompress(response.content)
            tree = ET.fromstring(content)
            
            # Filter <channel> and <programme> elements
            for child in tree:
                # 'id' is for channel tags; 'channel' is the attribute for programme tags
                cid = child.get('id') if child.tag == 'channel' else child.get('channel')
                if cid in wanted_channels:
                    new_root.append(child)
        except Exception as e:
            print(f"Skipping {url} due to error: {e}")
                
    # Save the filtered output
    tree = ET.ElementTree(new_root)
    ET.indent(tree, space="  ", level=0) # Makes the file structured and readable
    tree.write("my_guide.xml", encoding="utf-8", xml_declaration=True)
    print("Done! 'my_guide.xml' has been updated.")

if __name__ == "__main__":
    process_epg()
