from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from youtubesearchpython import VideosSearch
import yt_dlp
import shutil

FORMAT = 'mp3'
PATH_TO_WORLDS = '/worlds'
MUSIC_DIR = 'music'

app = Flask(__name__)
cors = CORS(app)
ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': FORMAT,
        'preferredquality': '192',
    }],
    'outtmpl': '%(title)s.%(ext)s',
})


@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    query = request.args.get('q')
    limit = request.args.get('limit', 5)

    results = VideosSearch(query, limit=limit)
    results = results.result().get('result', [])

    videos = []
    for r in results:
        videos.append({
            'id': r['id'],
            'title': r['title'],
            'channel': r['channel']['name'],
            'duration': r['duration'],
            'thumbnail': r['thumbnails'][-1]['url'],
            'url': r['link'],
        })

    return jsonify(videos)

@app.route('/download', methods=['GET'])
@cross_origin()
def download():
    url = request.args.get('url')
    world = request.args.get('world')

    if not url or not world:
        return 'Bad Request: Missing args', 400

    data = ytdl.extract_info(url, download=True)

    title = data['title']
    file = f'{title}.{FORMAT}'
    shutil.move(file, f'{PATH_TO_WORLDS}/{world}/{MUSIC_DIR}/{file}')

    return jsonify({
        'id': data['id'],
        'title': title,
        'codec': FORMAT,
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0')
