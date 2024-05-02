from django.urls import path
from . import views
	
urlpatterns = [
    path('', views.home, name='home'),
    path('playlists/', views.playlists_index, name='index'),
    path('playlists/<int:playlist_id>/', views.playlists_detail, name='detail'),
    path('playlists/create/', views.PlaylistCreate.as_view(), name='playlists_create'),
    path('playlists/<int:pk>/update/', views.PlaylistUpdate.as_view(), name='playlists_update'),
    path('playlists/<int:playlist_id>/save', views.playlist_songsaving, name='playlist_songsaving'),
    path('playlists/<int:playlist_id>/delete/songs/<str:spotify_id>', views.song_delete, name='songs_delete'),
    path('playlists/<int:pk>/delete/', views.PlaylistDelete.as_view(), name='playlists_delete'),
    path('playlists/<int:playlist_id>/add_photo/', views.add_photo, name='add_photo'),
    path('playlists/<int:playlist_id>/delete_photo/', views.delete_photo, name='delete_photo'),
    path('user/playlists/', views.user_playlists, name='user_playlists'),
    path('songs/', views.songs, name='song'),
    path('accounts/signup/', views.signup, name='signup'),
]