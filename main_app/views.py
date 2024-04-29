from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Playlist

# Create your views here.
def home(request):
    return render(request, 'home.html')

def playlists_index(request):
    playlists = Playlist.objects.all()
    return render(request, 'playlists/index.html', { 'playlists': playlists })

def playlists_detail(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    return render(request, 'playlists/detail.html', { 'playlist': playlist })

def song(request):
    return render(request, 'playlists/song.html')

class PlaylistCreate(CreateView):
    model = Playlist
    fields = ['name', 'description']
    
class PlaylistDelete(DeleteView):
    model = Playlist
    success_url = '/playlists'