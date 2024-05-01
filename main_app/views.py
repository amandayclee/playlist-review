from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Playlist
from requests import post, get
import requests, os, base64, json
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'playlistreivew', '.env')
load_dotenv(dotenv_path)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    
    return token

def get_auth_header(token):
    return { "Authorization": "Bearer " + token}

def search_for_song(token, song_kw):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={song_kw}&type=track&limit=5"
    
    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    return json_result

# Create your views here.
def home(request):
    return render(request, 'home.html')

def playlists_index(request):
    playlists = Playlist.objects.all()
    return render(request, 'playlists/index.html', { 'playlists': playlists })

def playlists_detail(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    return render(request, 'playlists/detail.html', { 'playlist': playlist })

def playlist_songsaving(request, playlist_id):
    print(request.body)
    response_data = {'message': 'Added to playlist successfully'}
    return JsonResponse(response_data)

def song(request):
    song_kw = request.POST.get("search", "")
    search_results = []
    if song_kw:
        token = get_token()
        search_results = search_for_song(token, song_kw)
        
    for result in search_results:
        total_seconds = result['duration_ms'] // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        result['formatted_duration'] = f"{hours:02}:{minutes:02}:{seconds:02}"
        result['album']['release_year'] = result['album']['release_date'][:4]
        
    playlists = Playlist.objects.all()
    return render(request, 'playlists/song.html', {
        'search_results': search_results,
        'playlists': playlists })

class PlaylistCreate(CreateView):
    model = Playlist
    fields = ['name', 'description']
    
class PlaylistUpdate(UpdateView):
    model = Playlist
    fields = ['name', 'description']  
    
class PlaylistDelete(DeleteView):
    model = Playlist
    success_url = '/playlists'