from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def playlists_index(request):
    return render(request, 'playlists/index.html')

def song(request):
    return render(request, 'playlists/song.html')