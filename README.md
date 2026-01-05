# lambdapodcast

Self-hosted podcast from curated MP3 files. Host media on Dropbox, serve RSS via GitHub Pages, subscribe in Apple Podcasts.

## Quick Start

1. **Configure your podcast** - Edit `config.yaml` with your podcast details
2. **Add episodes** - Edit `episodes.yaml` with your MP3 links
3. **Generate feed** - Run `python generate_feed.py`
4. **Deploy** - Push to GitHub, enable Pages
5. **Subscribe** - Add feed URL to Apple Podcasts

## Setup

### 1. Dropbox Setup

Create a folder for your podcast files (e.g., `Apps/lambdapodcast/`).

**For each file (MP3s and cover art):**
1. Upload to Dropbox
2. Click "Share" → "Copy link"
3. Change `?dl=0` to `?dl=1` in the URL

Example:
```
Before: https://www.dropbox.com/s/abc123/episode1.mp3?dl=0
After:  https://www.dropbox.com/s/abc123/episode1.mp3?dl=1
```

### 2. Cover Art

Apple Podcasts requires cover art:
- Square image (1400×1400 to 3000×3000 pixels)
- JPG or PNG format
- Upload to Dropbox, get direct link (`?dl=1`)

### 3. GitHub Pages Setup

1. Create a new **private** GitHub repo (e.g., `lambdapodcast`)
2. Push this project to it
3. Go to Settings → Pages
4. Source: "Deploy from a branch"
5. Branch: `main`, folder: `/docs`
6. Save

Your feed will be at: `https://yourusername.github.io/lambdapodcast/feed.xml`

### 4. Apple Podcasts

1. Go to [podcastsconnect.apple.com](https://podcastsconnect.apple.com)
2. Sign in with your Apple ID
3. Click "+" → Add a show with RSS
4. Enter your feed URL
5. Submit for review (usually approved within 24-48 hours)

**Privacy tip:** Select "Do not list" if you want the podcast unlisted.

## Usage

### Adding Episodes

1. Upload MP3 to Dropbox
2. Get the share link, change `?dl=0` to `?dl=1`
3. Add entry to `episodes.yaml`:

```yaml
- title: "Episode Title"
  description: "What this episode is about"
  file_url: "https://www.dropbox.com/s/xxxxx/episode.mp3?dl=1"
  pub_date: "2025-01-05"
  duration: "45:30"  # optional, format: HH:MM:SS or MM:SS
```

4. Generate and deploy:

```bash
python generate_feed.py
git add -A && git commit -m "Add episode" && git push
```

Apple Podcasts checks for updates every few hours to 24 hours.

## File Structure

```
lambdapodcast/
├── config.yaml          # Podcast metadata
├── episodes.yaml        # Episode list
├── generate_feed.py     # Feed generator
├── docs/
│   ├── feed.xml         # Generated RSS (served by GitHub Pages)
│   └── robots.txt       # Blocks search engines
└── README.md
```

## Troubleshooting

**Feed not updating in Apple Podcasts?**
- Check that your GitHub Pages is deployed (green checkmark in Actions)
- Verify feed.xml is accessible at your URL
- Apple can take up to 24 hours to refresh

**Invalid feed errors?**
- Validate your feed at [castfeedvalidator.com](https://castfeedvalidator.com)
- Check that all Dropbox URLs end with `?dl=1`
- Ensure pub_date is in YYYY-MM-DD format

**Cover art not showing?**
- Must be square, 1400-3000px
- Must be JPG or PNG
- Dropbox link must end with `?dl=1`
