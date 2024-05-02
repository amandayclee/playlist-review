from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from .models import Playlist, Song, Photo
from requests import post, get
import requests, os, base64, json, uuid, boto3
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

token = get_token()

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

def get_song_detail(token, song_id):
    url = f"https://api.spotify.com/v1/tracks/{song_id}??market=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    # total_seconds = json_result['duration_ms'] // 1000
    # hours = total_seconds // 3600
    # minutes = (total_seconds % 3600) // 60
    # seconds = total_seconds % 60
    # json_result['formatted_duration'] = f"{hours:02}:{minutes:02}:{seconds:02}"
    # json_result['album']['release_year'] = json_result['album']['release_date'][:4]
    
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

@login_required
def user_playlists(request):
    playlist = Playlist.objects.filter(user=request.user)
    return render(request, 'playlists/user_playlists.html', { 'playlists': playlist })

@login_required
def playlist_songsaving(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    request_body = json.loads(request.body.decode('utf-8'))
    if not Song.objects.filter(spotify_id=request_body['song_id']).exists():
        detail = get_song_detail(token, request_body['song_id'])
        total_seconds = detail['duration_ms'] // 1000
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        detail['formatted_duration'] = f"{hours:02}:{minutes:02}:{seconds:02}"
        detail['album']['release_year'] = detail['album']['release_date'][:4]
        song = Song.objects.create(
            name=detail['name'],
            artists=detail['artists'][0]['name'],
            album=detail['album']['name'],
            spotify_id=detail['id'],
            album_cover=detail['album']['images'][1]['url'],
            release_year=detail['album']['release_year'],
            formatted_duration=detail['formatted_duration']
        )
        song.save()
    else:
        song = Song.objects.get(spotify_id=request_body['song_id'])
    playlist.songs.add(song)
    response_data = {'message': f"{song.name} added to playlist successfully"}
    return JsonResponse(response_data)

@login_required
def songs(request):
    song_kw = request.POST.get("search", "")
    search_results = []
    if song_kw:
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

@login_required
def song_delete(request, playlist_id, spotify_id):
    song = Song.objects.get(spotify_id=spotify_id)
    playlist = Playlist.objects.get(id=playlist_id)
    playlist.songs.remove(song)
    return redirect('detail', playlist_id=playlist.id)

@login_required
def add_photo(request, playlist_id):
    photo_file = request.FILES.get('photo-file', None)
    print(photo_file)
    if photo_file:
        s3 = boto3.client('s3')
        key = f"{playlist_id}_photo" + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.getenv("S3_BUCKET")
            s3.upload_fileobj(photo_file, bucket, key)
            url = f"{os.getenv('S3_BASE_URL')}{bucket}/{key}"
            Photo.objects.get_or_create(url=url, playlist_id=playlist_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('detail', playlist_id=playlist_id)

class PlaylistCreate(LoginRequiredMixin, CreateView):
    model = Playlist
    fields = ['name', 'description']
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        add_photo(self.request, form.instance.id)
        return response
        
    
class PlaylistUpdate(LoginRequiredMixin, UpdateView):
    model = Playlist
    fields = ['name', 'description']  
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        add_photo(self.request, form.instance.id)
        return response
    
class PlaylistDelete(LoginRequiredMixin, DeleteView):
    model = Playlist
    success_url = '/playlists'
    
def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {
        'form': form,
        'error_message': error_message
    }
    return render(request, 'registration/signup.html', context)