#!/usr/bin/env python3
"""
Build an episode: combine MP3 files and update the podcast feed.

Usage:
    python build_episode.py <episode-folder-name> [--title "Episode Title"] [--description "..."]

Example:
    python build_episode.py 01-intro --title "Introduction" --description "Welcome to the show"
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

def parse_yaml_simple(filepath):
    """Parse simple YAML key-value pairs."""
    result = {}
    if not Path(filepath).exists():
        return result
    for line in Path(filepath).read_text().split('\n'):
        line = line.split('#')[0].rstrip()
        if ':' in line and not line.startswith(' ') and not line.startswith('\t'):
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                result[key] = value
    return result

def get_mp3_files(episode_dir):
    """Get all MP3 files in directory, sorted by name."""
    mp3s = sorted(episode_dir.glob('*.mp3'))
    # Exclude the output file if it exists
    mp3s = [f for f in mp3s if f.name != 'episode.mp3']
    return mp3s

def combine_mp3s(episode_dir, mp3_files):
    """Combine multiple MP3 files into episode.mp3 using ffmpeg."""
    output_file = episode_dir / 'episode.mp3'

    if len(mp3_files) == 0:
        print("Error: No MP3 files found in episode directory")
        sys.exit(1)

    if len(mp3_files) == 1:
        # Just copy/rename the single file
        import shutil
        shutil.copy(mp3_files[0], output_file)
        print(f"Copied single file to {output_file}")
        return output_file

    # Create concat file for ffmpeg
    concat_file = episode_dir / 'concat.txt'
    with open(concat_file, 'w') as f:
        for mp3 in mp3_files:
            # Escape single quotes in filename
            escaped = str(mp3.absolute()).replace("'", "'\\''")
            f.write(f"file '{escaped}'\n")

    # Run ffmpeg
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(output_file)
    ]

    print(f"Combining {len(mp3_files)} files...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up concat file
    concat_file.unlink()

    if result.returncode != 0:
        print(f"ffmpeg error: {result.stderr}")
        sys.exit(1)

    print(f"Created: {output_file}")
    return output_file

def get_duration(mp3_file):
    """Get duration of MP3 file using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(mp3_file)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        seconds = float(result.stdout.strip())
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    return None

def update_episodes_yaml(episode_name, title, description, duration):
    """Add or update episode in episodes.yaml."""
    yaml_path = Path('episodes.yaml')

    # Read existing content
    if yaml_path.exists():
        content = yaml_path.read_text()
    else:
        content = "# Episodes - newest first\n"

    # Check if episode already exists
    if f"folder: \"{episode_name}\"" in content or f"folder: '{episode_name}'" in content:
        print(f"Episode '{episode_name}' already in episodes.yaml - skipping")
        return

    # Create new episode entry
    today = datetime.now().strftime('%Y-%m-%d')
    new_entry = f'''
- folder: "{episode_name}"
  title: "{title}"
  description: "{description}"
  pub_date: "{today}"
  duration: "{duration or '00:00'}"
'''

    # Add after the header comment (newest first)
    lines = content.split('\n')
    insert_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('#') or line.strip() == '':
            insert_idx = i + 1
        else:
            break

    lines.insert(insert_idx, new_entry.strip())
    yaml_path.write_text('\n'.join(lines))
    print(f"Added episode to episodes.yaml")

def main():
    parser = argparse.ArgumentParser(description='Build a podcast episode')
    parser.add_argument('episode', help='Episode folder name (e.g., 01-intro)')
    parser.add_argument('--title', '-t', help='Episode title', default=None)
    parser.add_argument('--description', '-d', help='Episode description', default='')
    parser.add_argument('--skip-feed', action='store_true', help='Skip feed generation')
    args = parser.parse_args()

    episode_dir = Path('episodes') / args.episode

    if not episode_dir.exists():
        print(f"Error: Episode directory not found: {episode_dir}")
        sys.exit(1)

    # Get MP3 files
    mp3_files = get_mp3_files(episode_dir)
    print(f"Found {len(mp3_files)} MP3 file(s): {[f.name for f in mp3_files]}")

    # Combine MP3s
    output_file = combine_mp3s(episode_dir, mp3_files)

    # Get duration
    duration = get_duration(output_file)
    print(f"Duration: {duration}")

    # Default title from folder name
    title = args.title or args.episode.replace('-', ' ').title()

    # Update episodes.yaml
    update_episodes_yaml(args.episode, title, args.description, duration)

    # Generate feed
    if not args.skip_feed:
        print("\nGenerating feed...")
        subprocess.run([sys.executable, 'generate_feed.py'])

    print(f"\n✓ Episode built: {args.episode}")
    print(f"  Audio: {output_file}")
    print(f"  Cover: {episode_dir}/cover.jpg (generate with /nano-b)")
    print(f"\nNext: Copy '{episode_dir}' to your Dropbox podcast folder")

if __name__ == '__main__':
    main()
