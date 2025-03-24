from flask import Flask, request, jsonify
from collections import defaultdict
import yt_dlp
import os

app = Flask(__name__)

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

trie = Trie()

def fetch_and_index(video_url):
    print(f"Starting yt-dlp for {video_url}")
    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True,
        'subtitlesformat': 'vtt',
        'outtmpl': '%(id)s.%(ext)s'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video_id = info.get('id', '')
            caption_file = f"{video_id}.en.vtt"

            if not os.path.exists(caption_file):
                print(f"No captions downloaded for video ID: {video_id}")
                return "No captions found or subtitles unavailable.", []

            with open(caption_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip() and "-->":
                        continue
                    words = line.strip().lower().split()
                    if words:
                        trie.insert(words, video_id)

            os.remove(caption_file)
            print(f"Indexed video ID: {video_id}")
            return "Successfully indexed.", video_id
    except Exception as e:
        print(f"Error during yt-dlp execution: {e}")
        return f"Failed to index due to error: {e}", []

@app.route('/')
def root():
    return jsonify({"message": "Trie Search API is live!"}), 200

@app.route('/index', methods=['POST'])
def index_caption():
    data = request.json
    video_url = data.get('video_url')
    print(f"Received index request for URL: {video_url}")
    message, vid = fetch_and_index(video_url)
    return jsonify({"message": message, "video_id": vid})

@app.route('/search', methods=['GET'])
def search_phrase():
    raw_phrase = request.args.get('phrase', '')
    print(f"Search request received for phrase: '{raw_phrase}'")
    phrase = raw_phrase.lower().split()
    matches = trie.search(phrase)
    print(f"Search matches found: {matches}")
    return jsonify({"matches": matches})

def index_debug():
    return jsonify({"message": "GET on /index hit successfully"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)

