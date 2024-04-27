from django.urls import path
from . import views
	
urlpatterns = [
    path('', views.home, name='home'),
    path('playlists/', views.playlists_index, name='index'),
    path('songs/', views.song, name='song'),
]