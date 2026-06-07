# Playlist Filter

A Flask web app that connects to your Spotify account and creates a new playlist by filtering an existing playlist's tracks based on detected language.

## How it works

1. Sign in with your Spotify account via OAuth.
2. Choose a playlist from your library.
3. Pick a mode (remove or keep) and a target language (English, Spanish, Hindi, or Japanese).
4. The app scans the playlist's tracks, detects the language of each track name and artist, and builds a new playlist containing only the matching (or non-matching) tracks.

## Setup

1. Create a Spotify app at the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and add `http://127.0.0.1:4000/callback` as a redirect URI.

2. Create a `.env` file in the project root with the following values:

   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:4000/callback
   FLASK_SECRET_KEY=a_long_random_string
   ```

3. Install dependencies into the virtual environment:

   ```
   venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

## Running the app

```
venv\Scripts\python.exe spotify_playlist_filter.py
```

This opens `http://127.0.0.1:4000/login` in your browser, where you can authorize the app with your Spotify account. After authorizing, you'll be taken to the playlist filter UI.

## Project structure

- `spotify_playlist_filter.py` - Flask backend handling OAuth, the Spotify Web API calls, and the filtering logic.
- `templates/index.html` - Frontend UI for selecting a playlist, choosing filter options, and viewing results.
- `requirements.txt` - Python dependencies.

## Notes

- The Spotify API returns playlist tracks in pages of up to 100. Use the starting index field to jump to a later page if your playlist is larger.
- Language detection is powered by `langdetect` and works best on track names and artist names with enough text to analyze; short or ambiguous strings may not be detected reliably.
