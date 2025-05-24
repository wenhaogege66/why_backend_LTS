from django.urls import path
from . import views

urlpatterns = [
    path('bytitle/', views.SearchByTitleView.as_view(), name='search_by_title'),
    path('byartist/', views.SearchByArtistView.as_view(), name='search_by_artist'),
    path('byalbum/', views.SearchByAlbumView.as_view(), name='search_by_album'),
	path('byartistsong/', views.SearchByArtistSongView.as_view(), name='search_by_artist_song'),
	path('byalbumsong/', views.SearchByAlbumSongView.as_view(), name='search_by_album_song'),
	path('bysong/', views.SearchBySongView.as_view(), name='search_by_song'),
] 