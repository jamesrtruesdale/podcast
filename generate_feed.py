#!/usr/bin/env python3
"""
Generate an Apple Podcasts-compatible RSS feed from YAML config files.
No external dependencies - uses Python stdlib only.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

# Simple YAML parser for our limited use case (no external deps)
def parse_yaml(filepath):
    """Parse simple YAML files (supports strings, lists of dicts, booleans)."""
    content = Path(filepath).read_text()
    lines = content.split('\n')

    # Check if it's a list (starts with -)
    is_list = any(line.strip().startswith('- ') for line in lines if line.strip() and not line.strip().startswith('#'))

    if is_list:
        return _parse_yaml_list(lines)
    else:
        return _parse_yaml_dict(lines)

def _parse_yaml_dict(lines):
    """Parse YAML as a simple key-value dict."""
    result = {}
    for line in lines:
        line = line.split('#')[0].rstrip()  # Remove comments
        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            if value != '':
                result[key] = value
    return result

def _parse_yaml_list(lines):
    """Parse YAML as a list of dicts."""
    result = []
    current_item = None

    for line in lines:
        line_content = line.split('#')[0].rstrip()  # Remove comments
        if not line_content.strip():
            continue

        if line_content.strip().startswith('- '):
            if current_item:
                result.append(current_item)
            current_item = {}
            # Handle inline key after -
            rest = line_content.strip()[2:]
            if ':' in rest:
                key, value = rest.split(':', 1)
                current_item[key.strip()] = value.strip().strip('"').strip("'")
        elif current_item is not None and ':' in line_content:
            key, value = line_content.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                current_item[key] = value

    if current_item:
        result.append(current_item)

    return result

def format_rfc2822(date_str):
    """Convert YYYY-MM-DD to RFC 2822 format for RSS."""
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return dt.strftime('%a, %d %b %Y 12:00:00 +0000')

def format_duration(duration_str):
    """Ensure duration is in HH:MM:SS format."""
    if not duration_str:
        return None
    parts = duration_str.split(':')
    if len(parts) == 2:
        return f"00:{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    elif len(parts) == 3:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
    return duration_str

def build_dropbox_url(base_url, folder, filename):
    """Build a direct Dropbox URL for a file in a shared folder.

    Handles both old format (sh) and new format (scl/fo):
    - Old: https://www.dropbox.com/sh/abc123/def456?dl=1
    - New: https://www.dropbox.com/scl/fo/abc123/def456?rlkey=xxx&dl=1
    """
    from urllib.parse import urlparse, parse_qs, urlencode

    parsed = urlparse(base_url)
    query_params = parse_qs(parsed.query)

    # Build path with subfolder and file
    base_path = parsed.path.rstrip('/')
    new_path = f"{base_path}/{folder}/{filename}"

    # Keep rlkey if present, set dl=1
    new_params = {}
    if 'rlkey' in query_params:
        new_params['rlkey'] = query_params['rlkey'][0]
    new_params['dl'] = '1'

    # Use direct download domain
    host = 'dl.dropboxusercontent.com'

    return f"https://{host}{new_path}?{urlencode(new_params)}"

def generate_feed():
    """Generate the podcast RSS feed."""
    # Load config
    config = parse_yaml('config.yaml')
    episodes = parse_yaml('episodes.yaml')

    # Register namespaces for cleaner output
    ET.register_namespace('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')

    # Create RSS structure
    rss = ET.Element('rss')
    rss.set('version', '2.0')

    channel = ET.SubElement(rss, 'channel')

    # Required channel elements
    ET.SubElement(channel, 'title').text = config.get('title', 'My Podcast')
    ET.SubElement(channel, 'description').text = config.get('description', '')
    ET.SubElement(channel, 'language').text = config.get('language', 'en-us')

    site_url = config.get('site_url', '')
    feed_filename = config.get('feed_filename', 'feed.xml')
    feed_url = f"{site_url}/{feed_filename}"

    ET.SubElement(channel, 'link').text = site_url

    # Atom self-link (recommended)
    atom_link = ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link')
    atom_link.set('href', feed_url)
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    # iTunes-specific elements
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = config.get('author', '')
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = config.get('description', '')
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'yes' if config.get('explicit', False) else 'no'

    # Owner
    owner = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner')
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}name').text = config.get('author', '')
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}email').text = config.get('email', '')

    # Category
    category = config.get('category', 'Society & Culture')
    cat_elem = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category')
    cat_elem.set('text', category)

    # Cover art
    cover_url = config.get('cover_art_url', '')
    if cover_url:
        image = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
        image.set('href', cover_url)

        # Standard RSS image
        rss_image = ET.SubElement(channel, 'image')
        ET.SubElement(rss_image, 'url').text = cover_url
        ET.SubElement(rss_image, 'title').text = config.get('title', 'My Podcast')
        ET.SubElement(rss_image, 'link').text = site_url

    # Dropbox base URL for building file links
    dropbox_base = config.get('dropbox_base_url', '')

    # Episodes
    for ep in episodes:
        folder = ep.get('folder')
        if not folder:
            continue

        # Build URLs from Dropbox base + folder
        file_url = build_dropbox_url(dropbox_base, folder, 'episode.mp3')
        episode_cover_url = build_dropbox_url(dropbox_base, folder, 'cover.jpg')

        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = ep.get('title', 'Untitled Episode')
        ET.SubElement(item, 'description').text = ep.get('description', '')
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = ep.get('description', '')

        # Episode-specific cover art
        ep_image = ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image')
        ep_image.set('href', episode_cover_url)

        # Pub date
        if ep.get('pub_date'):
            ET.SubElement(item, 'pubDate').text = format_rfc2822(ep['pub_date'])

        # Enclosure (the actual MP3)
        enclosure = ET.SubElement(item, 'enclosure')
        enclosure.set('url', file_url)
        enclosure.set('type', 'audio/mpeg')
        enclosure.set('length', '0')  # Dropbox doesn't give us file size easily

        # Duration
        duration = format_duration(ep.get('duration'))
        if duration:
            ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text = duration

        # GUID (unique identifier)
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'false')
        guid.text = file_url

        # Explicit
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'no'

    # Pretty print using indent (Python 3.9+)
    try:
        ET.indent(rss, space='  ')
    except AttributeError:
        pass  # Python < 3.9, skip indentation

    xml_str = ET.tostring(rss, encoding='unicode')

    # Add XML declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_str

    # Write to docs/
    output_path = Path('docs') / feed_filename
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(xml_str)

    print(f"Generated: {output_path}")
    print(f"Feed URL will be: {feed_url}")

if __name__ == '__main__':
    generate_feed()
