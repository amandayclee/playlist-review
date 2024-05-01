from django.urls import path
from . import views
	
urlpatterns = [
    path('', views.home, name='home'),
    path('playlists/', views.playlists_index, name='index'),
    path('playlists/<int:playlist_id>/', views.playlists_detail, name='detail'),
    path('playlists/create', views.PlaylistCreate.as_view(), name='playlists_create'),
    path('playlists/<int:playlist_id>/update/', views.PlaylistUpdate.as_view(), name='playlists_update'),
    path('songs/', views.songs, name='song'),
    path('playlists/<int:playlist_id>/save', views.playlist_songsaving, name='playlist_songsaving'),
    path('playlists/<int:playlist_id>/delete/songs/<str:spotify_id>', views.song_delete, name='songs_delete'),
    path('playlists/<int:playlist_id>/delete/', views.PlaylistDelete.as_view(), name='playlists_delete'),
]