from flask import Flask, request, jsonify
from collections import defaultdict
import yt_dlp
import os

app = Flask(__name__)

# -----------------------
# Trie Implementation
# -----------------------
class TrieNode:
    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.video_ids = set()
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, words, video_id):
        node = self.root
        for word in words:
            node = node.children[word]
        node.is_end = True
        node.video_ids.add(video_id)

    def search(self, words):
        node = self.root
        for word in words:
            if word not in node.children:
                return []
            node = node.children[word]
        return list(node.video_ids) if node.is_end else []

# -----------------------
# Initialize Trie
# -----------------------
trie = Trie()

# -----------------------
# Caption Fetcher & Indexer
# -----------------------
def fetch_and_index(video_url):
    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True,
        'subtitlesformat': 'vtt',
        'outtmpl': '%(id)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        video_id = info.get('id', '')
        caption_file = f"{video_id}.en.vtt"

        if not os.path.exists(caption_file):
            return f"No captions found for {video_url}", []

        with open(caption_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and "-->":
                    continue
                words = line.strip().lower().split()
                if words:
                    trie.insert(words, video_id)

        os.remove(caption_file)
        return f"Indexed {video_url}", video_id

# -----------------------
# API Endpoints
# -----------------------
@app.route('/index', methods=['POST'])
def index_caption():
    data = request.json
    video_url = data.get('video_url')
    message, vid = fetch_and_index(video_url)
    return jsonify({"message": message, "video_id": vid})

@app.route('/search', methods=['GET'])
def search_phrase():
    phrase = request.args.get('phrase', '').lower().split()
    matches = trie.search(phrase)
    return jsonify({"matches": matches})

# -----------------------
# Run Server (local dev)
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)

