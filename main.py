from flask import Flask, request, jsonify
from youtubesearchpython import VideosSearch
import yt_dlp

app = Flask(__name__)
ytdl = yt_dlp.YoutubeDL({
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
})


@app.route('/search', methods=['GET'])
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


@app.route('/download/id', methods=['GET'])
def download():
    id = request.args.get('id')

    results = VideosSearch(id, limit=1)
    result = results.result().get('result', [])
    url = result[0].get('link', '') if results != [] else f'ytsearch1:{id}'

    data = ytdl.extract_info(url, download=False)

    return jsonify({
        'url': (
            data['entries'][0]['url']
            if url.startswith('ytsearch1:')
            else data['url']
        ),
        'codec': 'mp3',
    })


@app.route('/download/url', methods=['GET'])
def download_url():
    url = request.args.get('url')
    data = ytdl.extract_info(url, download=False)

    return jsonify({
        'id': data['id'],
        'title': data['title'],
        'url': data['url'],
        'codec': 'mp3',
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0')
