from flask import Flask,redirect,request,render_template,jsonify,session
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

scope = "playlist-modify-private"

load_dotenv()

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
redirect_uri = os.environ['REDIRECT_URI']

sp_oauth = SpotifyOAuth(client_id,
                        client_secret,
                        redirect_uri,
                        scope=scope)
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    '''
    redirect user to auth url
    '''
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    '''
    send playlists to frontend
    '''

    scope = "playlist-modify-private"
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
    redirect_uri = os.environ['REDIRECT_URI']
    
    sp_oauth = SpotifyOAuth(client_id,
                        client_secret,
                        redirect_uri,
                        scope=scope)
    
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    sp = spotipy.Spotify(auth=token_info['access_token'])

    playlists = sp.current_user_playlists(limit=10)

    return render_template('home.html', playlists=playlists['items'])
 

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    '''
    create merged playlist
    '''

    scope = "playlist-modify-private"
    #sp = spotipy.Spotify(auth=access_token)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    current_user_info = sp.current_user()
    current_user_id = current_user_info['id']

    data = request.json
    name = data['name']
    image = data['image']
    highlighted_playlists = data['playlists']

    sp.user_playlist_create( user=current_user_id, name=name, public=True, collaborative=False, description='merged playlist')

    # Add tracks from existing playlists to the new playlist
    user_playlists = sp.current_user_playlists()['items']

    new_playlist = user_playlists[0]

    new_playlist_id = new_playlist['id']

    '''
    get the playlist ID of each playlist to be merged,
    then get all tracks to be added to new playlist.
    Finally, change the playlist image to the one passed
    from frontend
    '''
    for playlist_name in highlighted_playlists:

        playlist_id = None
        for playlist in user_playlists:
            if(playlist['name']==playlist_name):
                playlist_id = playlist['id']
                break

        if(playlist_id != None):

            tracks = sp.playlist_tracks(str(playlist_id))    
            track_uris = [track['track']['uri'] for track in tracks['items']]
            sp.playlist_add_items(str(new_playlist_id), track_uris)


    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(debug=True)