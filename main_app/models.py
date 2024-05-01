from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.
class Song(models.Model):
    name = models.CharField(max_length=100)
    artists = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    spotify_id = models.CharField(max_length=100)
    album_cover = models.CharField(max_length=200) # album image [1]
    release_year = models.IntegerField() # album release_date
    formatted_duration = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('song_detail', kwargs={'pk': self.id})

class Playlist(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    songs = models.ManyToManyField(Song)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('detail', kwargs={'playlist_id': self.id})
    
    
class Photo(models.Model):
    url = models.CharField(max_length=200)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)

    def __str__(self):
        return f'Photo for playlist_id: {self.playlist_id} @{self.url}'