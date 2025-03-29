from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'vtt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Trie Node and Trie structure for indexing class
class TrieNode:
    def __init__(self):
        self.children = {}
        self.video_ids = set()

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, video_id):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.video_ids.add(video_id)

    def search(self, word):
        node = self.root
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                return []
        return list(node.video_ids)

# Global trie instance
trie = Trie()

# Utils

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_vtt_and_index(filepath, video_id):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        
    text_lines = [line.strip() for line in lines if re.match(r'^[a-zA-Z]', line.strip())]
    for line in text_lines:
        words = re.findall(r'\w+', line.lower())
        for word in words:
            trie.insert(word, video_id)

# Routes

@app.route("/ping")
def ping():
    return jsonify({"pong": True})

@app.route("/upload", methods=['POST'])
def upload_caption():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    
    file = request.files['file']
    video_id = request.form.get('video_id', None)

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename) and video_id:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        parse_vtt_and_index(filepath, video_id)
        return jsonify({"message": "File uploaded and indexed successfully."})
    else:
        return jsonify({"error": "Invalid file or missing video ID."}), 400

@app.route("/search")
def search():
    raw_phrase = request.args.get("phrase", "")
    words = raw_phrase.lower().split()

    if not words:
        return jsonify({"matches": []})

    result_sets = [set(trie.search(word)) for word in words]
    matches = list(set.intersection(*result_sets)) if result_sets else []

    return jsonify({"matches": matches})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

