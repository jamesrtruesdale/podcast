---
name: createepisode
description: Create a new podcast episode. Use when the user wants to add a new episode to Lambda Podcast. Guides through combining audio, generating cover art, and configuring Dropbox links.
---

# Create Episode Skill

This skill guides the user through creating a new podcast episode for Lambda Podcast.

## Workflow

When invoked, guide the user through these steps:

### Step 1: Identify Episode Folder

First, check what's in the `episodes/` directory:

```bash
ls -la episodes/
```

Ask the user which folder contains their MP3 files, or if they need to create one.

### Step 2: Build the Episode

Run the build script to combine MP3 files:

```bash
python build_episode.py "<folder-name>" --title "<Episode Title>" --description "<Description>"
```

Ask the user for:
- Episode title
- Episode description

The script will:
- Combine all MP3s in the folder into `episode.mp3`
- Calculate duration
- Add entry to `episodes.yaml`

### Step 3: Generate Cover Art

Use the `/nano-b` skill to generate cover art. Suggest a prompt like:

```
/nano-b podcast cover art for Lambda Podcast episode about [topic], featuring the Greek lambda symbol with music elements, neon purple/cyan/pink colors on dark background, square format
```

Save the output as `episodes/<folder-name>/cover.jpg`

### Step 4: Upload to Dropbox

Tell the user to:
1. Copy the episode folder to their Dropbox `lambdapodcast/` folder
2. The folder should contain:
   - `episode.mp3` (the combined audio)
   - `cover.jpg` (the generated cover art)

### Step 5: Get Dropbox Links

Ask the user to get **direct share links** for both files:

1. In Dropbox, right-click `episode.mp3` → Share → Copy link
2. Right-click `cover.jpg` → Share → Copy link

The links will look like:
```
https://www.dropbox.com/scl/fi/xxxxx/episode.mp3?rlkey=xxxxx&dl=0
https://www.dropbox.com/scl/fi/xxxxx/cover.jpg?rlkey=xxxxx&dl=0
```

### Step 6: Update Episodes YAML

Convert the Dropbox links to direct download URLs:
- Change `www.dropbox.com` to `dl.dropboxusercontent.com`
- Change `dl=0` to `dl=1`
- Remove the `st=` parameter if present

Update `episodes.yaml` to add `file_url` and `cover_url` to the episode entry:

```yaml
- folder: "Episode Name"
  title: "Episode Title"
  description: "Description"
  pub_date: "YYYY-MM-DD"
  duration: "HH:MM:SS"
  file_url: "https://dl.dropboxusercontent.com/scl/fi/xxxxx/episode.mp3?rlkey=xxxxx&dl=1"
  cover_url: "https://dl.dropboxusercontent.com/scl/fi/xxxxx/cover.jpg?rlkey=xxxxx&dl=1"
```

### Step 7: Generate Feed and Push

```bash
python generate_feed.py
git add -A
git commit -m "Add episode: <Episode Title>"
git push
```

### Step 8: Verify

Test that the Dropbox URLs work:

```bash
curl -sI "<file_url>" | head -3
```

Should return `HTTP/2 200`.

Confirm the feed is updated:
```bash
curl -s https://jamesrtruesdale.github.io/podcast/feed.xml | grep "<title>"
```

## Helper Function for URL Conversion

To convert a Dropbox share URL to direct download:

```python
def convert_dropbox_url(share_url):
    """Convert Dropbox share URL to direct download URL."""
    import re
    # Remove st= parameter
    url = re.sub(r'&st=[^&]*', '', share_url)
    # Change domain
    url = url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
    # Change dl=0 to dl=1
    url = url.replace('dl=0', 'dl=1')
    return url
```

## Example Session

```
User: /createepisode

Claude: Let me help you create a new episode! First, let me check what's in your episodes folder.
[runs ls episodes/]

Claude: I see you have a folder "Episode 2 - Deep Beats". Is this the episode you want to build?

User: yes

Claude: Great! What would you like the episode title to be?

User: Episode 2: Deep Beats

Claude: And a short description?

User: Groovy deep house vibes

Claude: Building the episode...
[runs build_episode.py]

Claude: Audio combined! Duration: 1:45:32. Now let's generate cover art.
[runs /nano-b with appropriate prompt]

Claude: Cover saved! Now please:
1. Copy the "Episode 2 - Deep Beats" folder to your Dropbox lambdapodcast/ folder
2. Get share links for episode.mp3 and cover.jpg

Paste the episode.mp3 link when ready.

User: https://www.dropbox.com/scl/fi/abc123/episode.mp3?rlkey=xyz&dl=0

Claude: Now paste the cover.jpg link.

User: https://www.dropbox.com/scl/fi/def456/cover.jpg?rlkey=uvw&dl=0

Claude: Updating feed and pushing to GitHub...
[updates episodes.yaml, generates feed, commits, pushes]

Claude: Done! Episode 2: Deep Beats is now live at:
https://jamesrtruesdale.github.io/podcast/feed.xml
```
