from flask import Flask, request, redirect, session, jsonify, render_template
import requests
import base64
import webbrowser
import os
from dotenv import load_dotenv
from langdetect import detect, LangDetectException

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')


@app.route('/')
def index():
    if 'access_token' not in session:
        return redirect('/login')
    return render_template('index.html')


@app.route('/login')
def login():
    scopes = 'playlist-modify-public playlist-modify-private'
    auth_url = (
        f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}'
        f'&scope={scopes}&redirect_uri={redirect_uri}'
    )
    return redirect(auth_url)


@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    access_token = get_access_token(client_id, client_secret, redirect_uri, auth_code)
    if not access_token:
        return "Failed to get access token.", 400
    session['access_token'] = access_token
    user_profile = get_user_profile(access_token)
    session['user_id'] = user_profile['id']
    session['display_name'] = user_profile.get('display_name', user_profile['id'])
    return redirect('/')


@app.route('/api/playlists')
def api_playlists():
    access_token = session.get('access_token')
    if not access_token:
        return jsonify({'error': 'Not authenticated'}), 401
    playlists = get_user_playlists(access_token)
    items = [
        {'id': p['id'], 'name': p['name'], 'tracks': p['tracks']['total']}
        for p in playlists.get('items', [])
        if p
    ]
    return jsonify({'playlists': items, 'display_name': session.get('display_name')})


@app.route('/filter', methods=['POST'])
def filter_playlist():
    access_token = session.get('access_token')
    user_id = session.get('user_id')
    if not access_token or not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    body = request.get_json()
    playlist_id = body.get('playlist_id')
    mode = body.get('mode')          # 'r' or 'k'
    language = body.get('language')  # 'en', 'es', 'hi', 'ja'
    start_index = int(body.get('start_index', 0))
    new_name = body.get('new_name', '').strip()

    if not all([playlist_id, mode, language, new_name]):
        return jsonify({'error': 'Missing required fields'}), 400

    offset = 0 if start_index == 0 else start_index - (start_index % 100)

    tracks = get_playlist_tracks(playlist_id, access_token, offset=offset)

    songs = []
    matched_tracks = []
    for track in tracks:
        if not track:
            continue
        trackname = track['name']
        artist = track['artists'][0]['name']
        lang_trackname = detector(trackname)
        lang_artist = detector(artist)

        include = False
        if mode == 'r':
            include = (lang_trackname != language) and (lang_artist != language)
        elif mode == 'k':
            include = (lang_trackname == language) and (lang_artist == language)

        if include:
            songs.append(track['uri'])
            matched_tracks.append({'name': trackname, 'artist': artist})

    new_playlist_id = create_playlist(access_token, user_id, new_name)
    if not new_playlist_id:
        return jsonify({'error': 'Failed to create new playlist'}), 500

    if songs:
        add_tracks_to_playlist(access_token, new_playlist_id, songs)

    return jsonify({
        'success': True,
        'new_playlist_name': new_name,
        'tracks_added': len(songs),
        'tracks': matched_tracks,
    })


# --- Spotify API helpers ---

def get_access_token(client_id, client_secret, redirect_uri, auth_code):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    auth_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
    }
    response = requests.post(auth_url, headers={'Authorization': f'Basic {auth_header}'}, data=auth_data)
    return response.json().get('access_token')


def get_user_profile(access_token):
    url = 'https://api.spotify.com/v1/me'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json()


def get_user_playlists(access_token):
    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    return response.json()


def get_playlist_tracks(playlist_id, access_token, offset=0):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers, params={'offset': offset})
    tracks_data = response.json().get('items', [])
    return [song['track'] for song in tracks_data if song.get('track')]


def create_playlist(access_token, user_id, playlist_name, public=True):
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    data = {'name': playlist_name, 'public': public}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()['id']
    return None


def add_tracks_to_playlist(access_token, playlist_id, track_uris):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json={'uris': track_uris})
    return response.status_code == 201


def detector(string):
    try:
        if not string.strip():
            return None
        return detect(string)
    except (LangDetectException, ValueError):
        return None


if __name__ == "__main__":
    webbrowser.open('http://127.0.0.1:4000/login')
    app.run(port=4000)
