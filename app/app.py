from flask import Flask, redirect, request, session, url_for,send_from_directory
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = "user-library-read"

load_dotenv()

client_id = os.environ['CLIENT_ID']
client_secret=os.environ['CLIENT_SECRET']
redirect_uri=os.environ['REDIRECT_URI']

sp_oauth = SpotifyOAuth(client_id,
                        client_secret,
                        redirect_uri,
                        scope=scope)

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def index():
    # Redirect to Spotify authorization URL
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Retrieve authorization code from callback URI
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Use the access token to initialize Spotipy
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Retrieve and print user's saved tracks
    results = sp.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artists'][0]['name'], " – ", track['name'])

    return "Authentication successful. Check console for saved tracks."

if __name__ == '__main__':
   
    app.run(debug=True)
