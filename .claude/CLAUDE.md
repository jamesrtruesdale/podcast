# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project: lambdapodcast

## Overview

Self-hosted podcast generator. Combine MP3 files into episodes, generate cover art, and publish via RSS.

**Architecture:**
- MP3s + cover art hosted on Dropbox (direct file links)
- RSS feed hosted on GitHub Pages (public repo)
- Subscribe directly via URL in Apple Podcasts

## Skills

### /createepisode

**Use this skill to create a new podcast episode.** It guides through the full workflow:
1. Combine MP3 files
2. Generate cover art
3. Get Dropbox links
4. Update feed and push

## Tech Stack

- Python 3.x (stdlib only, no dependencies)
- ffmpeg for audio combining
- GitHub Pages for RSS hosting
- Dropbox for media hosting (direct file links)

## Build & Run

```bash
# Build an episode (combines MP3s, updates feed)
python build_episode.py "<folder-name>" --title "Episode Title" --description "..."

# Just regenerate the feed
python generate_feed.py

# Validate feed
python -c "import xml.etree.ElementTree as ET; ET.parse('docs/feed.xml'); print('Valid')"
```

## Architecture

```
lambdapodcast/
├── episodes/
│   └── Episode Name/
│       ├── part1.mp3, part2.mp3...  (raw files you drop in)
│       ├── episode.mp3              (combined output)
│       └── cover.jpg                (generated via /nano-b)
├── config.yaml          # Podcast metadata
├── episodes.yaml        # Episode list with Dropbox URLs
├── build_episode.py     # Combine MP3s
├── generate_feed.py     # Generate RSS from config
└── docs/
    ├── feed.xml         # RSS feed (GitHub Pages serves this)
    └── robots.txt       # Block search indexing
```

## Episode Workflow (Manual)

1. Create folder: `mkdir episodes/"Episode Name"`
2. Drop MP3 files into the folder
3. Build: `python build_episode.py "Episode Name" --title "Title" --description "..."`
4. Generate cover: `/nano-b` → save as `episodes/Episode Name/cover.jpg`
5. Copy episode folder to Dropbox
6. Get direct share links for `episode.mp3` and `cover.jpg`
7. Add `file_url` and `cover_url` to episodes.yaml
8. `python generate_feed.py && git add -A && git commit -m "Add episode" && git push`

## Dropbox URL Format

Dropbox share links must be converted to direct download URLs:

```
Share link:  https://www.dropbox.com/scl/fi/xxxxx/file.mp3?rlkey=yyy&st=zzz&dl=0
Direct URL:  https://dl.dropboxusercontent.com/scl/fi/xxxxx/file.mp3?rlkey=yyy&dl=1
```

- Change `www.dropbox.com` → `dl.dropboxusercontent.com`
- Remove `st=` parameter
- Change `dl=0` → `dl=1`

## Feed URL

```
https://jamesrtruesdale.github.io/podcast/feed.xml
```

## Issue Tracking

See @AGENTS.md for beads workflow commands.
