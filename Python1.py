import base64
import requests
from langdetect import detect
import webbrowser

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'

auth_url = 'https://accounts.spotify.com/api/token'
auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
auth_data = {'grant_type': 'client_credentials'}

response = requests.post(auth_url, headers={'Authorization': f'Basic {auth_header}'}, data=auth_data)
token = response.json().get('access_token')

headers = {'Authorization': f'Bearer {token}'}

# Example: Get details of a track
track_id = '3n3Ppam7vgaVa1iaRUc9Lp'
track_url = f'https://api.spotify.com/v1/tracks/{track_id}'

track_response = requests.get(track_url, headers=headers)
track_data = track_response.json()

print(f"Track Name: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
print(f"Album: {track_data['album']['name']}")

# Define the endpoint URL
track_id = '3n3Ppam7vgaVa1iaRUc9Lp'  # Replace with your track ID
url = f'https://api.spotify.com/v1/tracks/{track_id}'

# Define the headers with your access token
headers = {
    'Authorization': 'Bearer YOUR_ACCESS_TOKEN'
}

# Make a GET request to the endpoint
response = requests.get(url, headers=headers)
track_data = response.json()

# Print the track details
print(f"Track Name: {track_data['name']}")
print(f"Artist: {track_data['artists'][0]['name']}")
print(f"Album: {track_data['album']['name']}")
print(f"Release Date: {track_data['album']['release_date']}")

playlist = str(input("Please enter the name of the playlist you want to parse through:"))

def classification(song):


# Define the endpoint URL and parameters
#track_id = '15445219'  # Replace with your Musixmatch track ID
api_key = 'YOUR_API_KEY'
url = f'http://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={api_key}'

# Make a GET request to the endpoint
response = requests.get(url)
lyrics_data = response.json()

# Extract the lyrics
if lyrics_data['message']['header']['status_code'] == 200:
    lyrics = lyrics_data['message']['body']['lyrics']['lyrics_body']
    # Detect the language of the lyrics
    language = detect(lyrics)
    print(f"Lyrics Language: {language}")
else:
    print("Error fetching lyrics")




#need to flesh out classification
# I see two main functions needed
#1: song classification function
# Artist name, song name, lyrics, genre if possible
#2: final function that somehow takes in a playlist, runs classification function on all songs, 
#and adds only desired songs into a new playlist that will be returned


# Step 1: Get the access token (OAuth 2.0 Authorization Code flow)

client_id = 'YOUR_CLIENT_ID'
redirect_uri = 'YOUR_REDIRECT_URI'
scopes = 'playlist-read-private playlist-read-collaborative user-library-read'

auth_url = (
    f'https://accounts.spotify.com/authorize'
    f'?response_type=code&client_id={client_id}'
    f'&scope={scopes}&redirect_uri={redirect_uri}'
)

webbrowser.open(auth_url)

#Step 2
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = str(input("YOUR_REDIRECT_URI:"))
authorization_code = 'AUTHORIZATION_CODE_FROM_REDIRECT'

def get_access_token(client_id, client_secret, redirect_uri, authorization_code):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    auth_data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(auth_url, headers={'Authorization': f'Basic {auth_header}'}, data=auth_data)
    return response.json().get('access_token')

client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
redirect_uri = 'YOUR_REDIRECT_URI'
auth_code = 'AUTHORIZATION_CODE_FROM_USER'

def get_access_token(client_id, client_secret, redirect_uri, auth_code):
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    auth_data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(auth_url, headers={'Authorization': f'Basic {auth_header}'}, data=auth_data)
    return response.json().get('access_token')
# Get the access token
access_token = get_access_token(client_id, client_secret, redirect_uri, authorization_code)
# Step 2: Get the user's playlists
def get_user_playlists(access_token):
    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    return response.json()

# Get the playlists
playlists = get_user_playlists(access_token)

# Print the playlists
for playlist in playlists['items']:
    print(f"Playlist Name: {playlist['name']}")
    print(f"Playlist ID: {playlist['id']}")
    print(f"Total Tracks: {playlist['tracks']['total']}")
    print()

