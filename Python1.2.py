from flask import Flask, request, redirect
import requests
import base64
import webbrowser
from langdetect import detect, LangDetectException

app = Flask(__name__)

# Credentials
client_id = 'cc226c7567e645d0a811e66cf214128f'
client_secret = '155a2ad652984092a8ecba0357237093'
redirect_uri = 'http://localhost:4000/callback'


# Redirect user to Spotify's authorization page
@app.route('/login')
def login():
    scopes = 'playlist-modify-public playlist-modify-private'
    auth_url = (
        f'https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}'
        f'&scope={scopes}&redirect_uri={redirect_uri}'
    )
    return redirect(auth_url)

# Step 2: Handle the callback from Spotify
@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    access_token = get_access_token(client_id, client_secret, redirect_uri, auth_code)
    playlists = get_user_playlists(access_token)
    user_profile = get_user_profile(access_token) 
    user_id = user_profile["id"]
    ask = str(input("What's the name of the playlist you want to modify:"))
    ask4 = str(input("Do you want to remove or keep songs(choose r or k):"))
    ask2 = str(input("What type of language songs do you want to remove/keep from the playlist (English(en), Spanish(es), Hindi(hi), or Japanese(ja)):"))
    ask5 = int(input("Please give a starting index of song, as Spotify API is limited to parsing through 100 songs(this will go through the 100 songs including the song you choose), if you just want to go through your first hundred songs please enter 99999:"))
    if ask5 == 99999:
        j = 0
    else:
        j = ask5 - (ask5%100)
    #checks through all playlists and selects playlist based on playlist name
    for i in range(0,len(playlists["items"])):
        if ask == (playlists['items'][i]["name"]):
            playlist_id = playlists['items'][i]["id"]
    ask3 = str(input("What would you want to name your new playlist:")) 
    new_playlist = create_playlist(access_token, user_id, ask3) 
    playlist_id_new = create_playlist_get_id(access_token, user_id, ask3, public = True)
    print(ask2)
    print(new_playlist)
    if playlists['items']:
        print(playlist_id)
        tracks = get_playlist_tracks(playlist_id, access_token, offset = j)# starts from "j - j%100" song in playlist
        print(tracks)
        songs = []
        for track in tracks:# iterates through 100 songs at most in playlist
            print(f"Track: {track['name']}") 
            print(f"Artist: {track['artists'][0]['name']}")
            trackname = f"{track['name']}"
            lang_trackname = detector(trackname)
            print(lang_trackname)
            artist = f"{track['artists'][0]['name']}"
            lang_artist = detector(artist)
            print(lang_artist)
            if ask4 == "r":
                if (lang_trackname != ask2) and (lang_artist != ask2):
                    print(track['uri'])
                    songs.append(track['uri'])
                    print("wow!")
            elif ask4 == "k":
                if (lang_trackname == ask2) and (lang_artist == ask2):
                    songs.append(track['uri'])
                    print("wow!")
                #add to new playlist, other wise do not do so
     #       j+=1
     #       if j >= 110:
     #           break
            print()
    add_tracks_to_playlist(access_token, playlist_id_new, songs)
    #add a keep songs of only a certain language feature too
    #
    #code to ask for the playlist user wants to modify and then makes that the playlist to be modified
    #ask = str(input("What's the name of the playlist you want to modify:"))
    #ask2 = str(input("What type of language songs do you want to remove from the playlist (English(en), Spanish(es), Hindi(hi), or Japanese(jp)):"))
    #for i in range(0,len(playlists["items"])):
    #    if ask == (playlists['items'][i]["name"]):
    #     auth_id = playlists['items'][i]["id"]# takes the playlist ID of the playlist the user wants
    #make function that uses lang detect to categorize words to language and classifies song
    #make function that adds desired songs based on language to new playlist
    return "Authorization complete! Check your console for playlist details."

def get_access_token(client_id, client_secret, redirect_uri, auth_code): 
    auth_url = 'https://accounts.spotify.com/api/token' 
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode() 
    auth_data = {'grant_type': 'authorization_code', 
                 'code': auth_code, 'redirect_uri': redirect_uri, 
                 'scope': 'playlist-modify-private' 
                 # Add the necessary scope here 
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
    print("worked")
    return response.json()

def get_playlist_tracks(playlist_id, access_token, offset = 0):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {
        "offset": offset
            }
    
    response = requests.get(url, headers=headers, params=data) 
    tracks_data = response.json()['items'] 
    tracks = []

    for song in tracks_data:
        tracks.append(song["track"])
    print(tracks)
   # for track in tracks:
   #     print(track["name"])
    
    return tracks




# Example: Create a new playlist 
def create_playlist(access_token, user_id, name): 
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists' 
    headers = { 
        'Authorization': f'Bearer {access_token}', 
        'Content-Type': 'application/json' 
        } 
    data = { 
        'name': name, 
        'public': True 
        } 
    response = requests.post(url, headers=headers, json=data) 
    new_playlist = response.json() 
    return new_playlist['id']

def add_tracks_to_playlist(access_token, playlist_id, track_uris): 
    add_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks' 
    headers = { 
        'Authorization': f'Bearer {access_token}', 
        'Content-Type': 'application/json', 
        } 
    data = { 'uris': track_uris } 
    response = requests.post(add_tracks_url, headers=headers, json=data) 
    if response.status_code == 201: 
        print("Tracks added successfully!") 
    else: 
        print("Error adding tracks:", response.json())

def create_playlist_get_id(access_token, user_id, playlist_name, public=True): 
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists' 
    headers = { 'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json' } 
    data = { 'name': playlist_name, 'public': public } 
    response = requests.post(url, headers=headers, json=data) 
    if response.status_code == 201: 
        new_playlist = response.json() 
        return new_playlist['id'] 
    # Return the playlist ID 
    else: 
        print("Error creating playlist:", response.json()) 
        return None


#def detector(string):
#    language = detect(string)
#    return language

def detector(string): 
    try: 
        if not string.strip(): 
            raise ValueError("Input string is empty or contains only whitespace.") 
        language = detect(string) 
        return language 
    except LangDetectException: 
        print("No features in text. Cannot detect language.") 
        return None 
    except ValueError as e: 
        print(e) 
        return None
 


if __name__ == "__main__":
    webbrowser.open('http://localhost:4000/login')
    app.run(port=4000)
