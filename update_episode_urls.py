#!/usr/bin/env python3
"""
Update episode URLs in episodes.yaml with Dropbox direct download links.

Usage:
    python update_episode_urls.py <episode-folder> --file-url <url> --cover-url <url>
"""

import argparse
import re
from pathlib import Path


def convert_dropbox_url(share_url):
    """Convert Dropbox share URL to direct download URL."""
    # Remove st= parameter
    url = re.sub(r'&st=[^&]*', '', share_url)
    # Change domain
    url = url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
    # Change dl=0 to dl=1
    url = url.replace('dl=0', 'dl=1')
    return url


def update_episodes_yaml(folder, file_url, cover_url):
    """Update episodes.yaml with the URLs for a specific episode."""
    yaml_path = Path('episodes.yaml')
    content = yaml_path.read_text()
    lines = content.split('\n')

    # Convert URLs to direct download format
    file_url = convert_dropbox_url(file_url)
    cover_url = convert_dropbox_url(cover_url)

    # Find the episode entry and add URLs
    new_lines = []
    found_episode = False
    i = 0

    while i < len(lines):
        line = lines[i]
        new_lines.append(line)

        # Check if this is the folder line for our episode
        if f'folder: "{folder}"' in line or f"folder: '{folder}'" in line:
            found_episode = True
            # Look ahead to find where to insert URLs (after duration)
            i += 1
            while i < len(lines):
                current = lines[i]
                new_lines.append(current)

                # If we hit the duration line, add URLs after it
                if current.strip().startswith('duration:'):
                    # Check if file_url already exists
                    if i + 1 < len(lines) and 'file_url:' in lines[i + 1]:
                        # Skip existing file_url and cover_url
                        i += 1
                        while i < len(lines) and (lines[i].strip().startswith('file_url:') or lines[i].strip().startswith('cover_url:')):
                            i += 1
                        i -= 1  # Back up one since we'll increment at end of loop

                    # Add the new URLs
                    new_lines.append(f'  file_url: "{file_url}"')
                    new_lines.append(f'  cover_url: "{cover_url}"')
                    break

                # If we hit the next episode or end, stop
                if current.strip().startswith('- folder:'):
                    break
                i += 1
        i += 1

    if not found_episode:
        print(f"Error: Episode '{folder}' not found in episodes.yaml")
        return False

    # Write back
    yaml_path.write_text('\n'.join(new_lines))
    print(f"Updated episodes.yaml with URLs for '{folder}'")
    print(f"  file_url: {file_url}")
    print(f"  cover_url: {cover_url}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Update episode URLs in episodes.yaml')
    parser.add_argument('folder', help='Episode folder name')
    parser.add_argument('--file-url', '-f', required=True, help='Dropbox share URL for episode.mp3')
    parser.add_argument('--cover-url', '-c', required=True, help='Dropbox share URL for cover.jpg')
    args = parser.parse_args()

    if update_episodes_yaml(args.folder, args.file_url, args.cover_url):
        print("\nNow run:")
        print("  python generate_feed.py")
        print("  git add -A && git commit -m \"Add episode URLs\" && git push")


if __name__ == '__main__':
    main()
