from django.contrib import admin
from .models import Playlist, Song, Photo

# Register your models here.
admin.site.register([Playlist, Song, Photo])