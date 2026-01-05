# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: lambdapodcast

## Overview

Self-hosted podcast generator. Combine MP3 files into episodes, generate cover art, and publish via RSS.

**Architecture:**
- MP3s + cover art hosted on Dropbox (shared folder)
- RSS feed hosted on GitHub Pages (private repo)
- Subscribe directly via URL in Apple Podcasts

## Tech Stack

- Python 3.x (stdlib only, no dependencies)
- ffmpeg for audio combining
- GitHub Pages for RSS hosting
- Dropbox for media hosting

## Build & Run

```bash
# Build an episode (combines MP3s, updates feed)
python build_episode.py <folder-name> --title "Episode Title" --description "..."

# Just regenerate the feed
python generate_feed.py

# Validate feed
python -c "import xml.etree.ElementTree as ET; ET.parse('docs/feed.xml'); print('Valid')"
```

## Architecture

```
lambdapodcast/
├── episodes/
│   └── 01-episode-name/
│       ├── part1.mp3, part2.mp3...  (raw files you drop in)
│       ├── episode.mp3              (combined output)
│       └── cover.jpg                (generated via /nano-b)
├── config.yaml          # Podcast metadata + Dropbox base URL
├── episodes.yaml        # Episode list (auto-updated by build script)
├── build_episode.py     # Combine MP3s, update feed
├── generate_feed.py     # Generate RSS from config
└── docs/
    ├── feed.xml         # RSS feed (GitHub Pages serves this)
    └── robots.txt       # Block search indexing
```

## Episode Workflow

1. Create folder: `mkdir episodes/01-my-episode`
2. Drop MP3 files into the folder
3. Build: `python build_episode.py 01-my-episode --title "My Episode"`
4. Generate cover: `/nano-b` → save as `episodes/01-my-episode/cover.jpg`
5. Copy episode folder to Dropbox podcast folder
6. Commit and push to GitHub

## Dropbox Setup

Share your podcast folder once, save the base URL in `config.yaml`:
```yaml
dropbox_base_url: "https://www.dropbox.com/sh/abc123/def456?dl=1"
```

Files are accessed via: `dl.dropboxusercontent.com/sh/abc123/def456/{folder}/episode.mp3`

## Issue Tracking

See @AGENTS.md for beads workflow commands.
