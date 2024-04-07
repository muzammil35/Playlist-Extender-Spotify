from flask import Flask,redirect,request,render_template,jsonify,session,url_for
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import json

from utils.get_encoded_image import image_url_to_base64
from utils.is_valid_url import is_valid_image_url
from flask import Flask, make_response

scope = "playlist-modify-public ugc-image-upload"

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
    response = make_response("Cookies cleared")
    for cookie_name in request.cookies:
        response.set_cookie(cookie_name, expires=0)
    session.clear()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route('/callback')
def callback():
    '''
    send playlists to frontend
    '''
    code = request.args.get('code')

    token_url = 'https://accounts.spotify.com/api/token'
    payload = {
      'grant_type': 'authorization_code',
      'code': code,
      'redirect_uri': redirect_uri,
      'client_id': client_id,
      'client_secret': client_secret
    }
    response = requests.post(token_url, data=payload)
    token_info = response.json()

    # Extract the access token
    access_token = token_info['access_token']

    # Use the access token to make a request to get the current user's information
    user_info_url = 'https://api.spotify.com/v1/me'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    user_info_response = requests.get(user_info_url, headers=headers)
    current_user_info = user_info_response.json()
  
    # Get user's playlists
    playlists_url = f"{SPOTIFY_API_BASE_URL}/me/playlists"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    playlists_response = requests.get(playlists_url, headers=headers)
    playlists_data = playlists_response.json()
    playlists = playlists_data['items']

    # Render home.html template with user's playlists
    return render_template('home.html', playlists=playlists)
 

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    '''
    create merged playlist
    '''

    scope = "playlist-modify-public ugc-image-upload"
    #sp = spotipy.Spotify(auth=access_token)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    #sp = spotipy.Spotify(auth=token_info['access_token'])

    token_info = session.get('token_info')

    if(token_info):
        if sp_oauth.is_token_expired(token_info):
            refresh_token = session.get('refresh_token')
            token_info = sp_oauth.refresh_access_token(refresh_token)


    current_user_info = sp.current_user()
    current_user_id = current_user_info['id']

    data = request.json
    name = data['name']
    image = data['image']
    highlighted_playlists = data['playlists']

    sp.user_playlist_create( user=current_user_id, name=name, public=True, collaborative=False, description="merged playlist")

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
    
    image_url = image


    if(is_valid_image_url(image_url)):
        encoded_img = image_url_to_base64(image_url)
        sp.playlist_upload_cover_image(str(new_playlist_id), encoded_img)



    return jsonify({'success': True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
