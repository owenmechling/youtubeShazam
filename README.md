# youtubeShazam
# a project by mercato

# YouTube Caption Trie Search API

## Overview

This is a Flask-based microservice that uses a Trie (Prefix Tree) 
data structure to index YouTube video captions. 

It allows users to search for exact phrases within captions across multiple videos.

## Features

- Fetch captions automatically from YouTube using `yt-dlp`
- Insert caption phrases into a word-level Trie
- Search for exact multi-word phrases via a REST API
- Returns matched video IDs where the phrase appears

## Endpoints

### POST `/index`

- **Body JSON:** `{ "video_url": "https://www.youtube.com/watch?v=VIDEO_ID" }`
- **Function:** Downloads captions for the provided YouTube URL and indexes them into the Trie.

### GET `/search`

- **Query param:** `phrase=your+search+query`
- **Function:** Searches the indexed Trie for the given phrase.

## Requirements

- Python 3.8+
- Flask
- yt-dlp

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install flask yt-dlp
python app.py
```

## Deployment

This app is ready to deploy on Render.com using the included `render.yaml` file.

---

## Notes

- Make sure to handle YouTube’s caption availability (not all videos have captions).
- The search functionality currently supports exact phrase matches.

---

## License

MIT License


