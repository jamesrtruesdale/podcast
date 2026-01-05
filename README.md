# lambdapodcast

Self-hosted podcast from curated MP3 files. Combine audio, generate artwork, host on Dropbox, serve RSS via GitHub Pages.

## Quick Start

1. **One-time setup**: Configure Dropbox folder + GitHub Pages
2. **Per episode**: Drop MP3s → build → generate art → copy to Dropbox → push

## Setup

### 1. Dropbox Folder

1. Create folder in Dropbox (e.g., `Apps/lambdapodcast/`)
2. Right-click → Share → Copy link
3. You'll get: `https://www.dropbox.com/sh/abc123/def456?dl=0`
4. Save in `config.yaml` as `dropbox_base_url` (change `dl=0` to `dl=1`)

### 2. GitHub Repository

1. Create a **private** GitHub repo
2. Push this project to it
3. Go to Settings → Pages
4. Source: Deploy from branch, `main`, `/docs`
5. Update `site_url` in `config.yaml` with your Pages URL

### 3. Podcast Metadata

Edit `config.yaml`:
- `title`, `description`, `author`
- `dropbox_base_url` (from step 1)
- `site_url` (from step 2)
- `cover_art_url` (main podcast cover, upload to Dropbox root)

## Adding Episodes

### 1. Create Episode Folder

```bash
mkdir episodes/01-intro
```

### 2. Add MP3 Files

Drop your MP3 files into the folder. They'll be combined in alphabetical order:
```
episodes/01-intro/
├── part1.mp3
├── part2.mp3
└── part3.mp3
```

### 3. Build Episode

```bash
python build_episode.py 01-intro --title "Introduction" --description "Welcome to the show"
```

This:
- Combines MP3s into `episode.mp3`
- Updates `episodes.yaml`
- Regenerates `docs/feed.xml`

### 4. Generate Cover Art

Use the `/nano-b` skill to generate artwork:
```
/nano-b podcast cover art for an episode about [topic], square format
```

Save the image as `episodes/01-intro/cover.jpg`

### 5. Copy to Dropbox

Copy the episode folder to your Dropbox podcast folder:
```
Dropbox/Apps/lambdapodcast/01-intro/
├── episode.mp3
└── cover.jpg
```

### 6. Push to GitHub

```bash
git add -A && git commit -m "Add episode: Introduction" && git push
```

## Subscribe

In Apple Podcasts (or any podcast app):
1. Add show by URL
2. Enter: `https://yourusername.github.io/lambdapodcast/feed.xml`

No need to submit to Apple's directory - direct URL subscription works.

## File Structure

```
lambdapodcast/
├── episodes/           # Your episode folders
│   └── 01-intro/
│       ├── *.mp3       # Raw audio files
│       ├── episode.mp3 # Combined (generated)
│       └── cover.jpg   # Cover art (generated)
├── config.yaml         # Podcast settings
├── episodes.yaml       # Episode list (auto-updated)
├── build_episode.py    # Build script
├── generate_feed.py    # Feed generator
└── docs/
    ├── feed.xml        # RSS feed
    └── robots.txt      # Block indexing
```

## Troubleshooting

**Audio not combining?**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check MP3 files are valid

**Feed not updating?**
- Verify GitHub Pages is deployed (Actions tab)
- Check `docs/feed.xml` was committed

**Dropbox links not working?**
- Ensure base URL uses `?dl=1` not `?dl=0`
- Verify folder is shared (not just individual files)
