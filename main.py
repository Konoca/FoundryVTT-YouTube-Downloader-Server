from flask import Flask, request, jsonify  #, Response
from flask_cors import CORS, cross_origin
from youtubesearchpython import VideosSearch
import yt_dlp
# from urllib.parse import urlparse
# import requests
import shutil

FORMAT = 'mp3'
# FORMAT = 'ogg'
PATH_TO_WORLDS = './worlds/'
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


# @app.route('/download/id', methods=['GET'])
# @cross_origin()
# def download():
#     id = request.args.get('id')
#
#     results = VideosSearch(id, limit=1)
#     result = results.result().get('result', [])
#     url = result[0].get('link', '') if results != [] else f'ytsearch1:{id}'
#
#     data = ytdl.extract_info(url, download=False)
#
#     return jsonify({
#         'url': (
#             data['entries'][0]['url']
#             if url.startswith('ytsearch1:')
#             else data['url']
#         ),
#         'codec': FORMAT,
#     })
#
#
# @app.route('/download/url', methods=['GET'])
# @cross_origin()
# def download_url():
#     url = request.args.get('url')
#     data = ytdl.extract_info(url, download=False)
#
#     return jsonify({
#         'id': data['id'],
#         'title': data['title'],
#         'url': data['url'],
#         'codec': FORMAT,
#     })
#
#
# @app.route('/proxy', methods=['GET'])
# @cross_origin()
# def proxy():
#     url = request.args.get('url')
#     parsed = urlparse(url)
#     domain = parsed.netloc.split('.')
#     if len(domain) < 3 or domain[1] != 'googlevideo' or domain[2] != 'com':
#         return 'Bad Request: Invalid URL', 400
#
#     try:
#         response = requests.get(url, allow_redirects=False, stream=True)
#         def generate():
#             for chunk in response.raw.stream(decode_content=False):
#                 yield chunk
#     except Exception as e:
#         print(e)
#         return f'Error: {e}', 502
#
#     return Response(
#         generate(),
#         status=response.status_code,
#         headers=dict(response.headers)
#     )

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
