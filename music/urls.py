from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtistViewSet, AlbumViewSet, SongViewSet, TagViewSet,
    PlaylistViewSet, FavoriteViewSet, PlayHistoryViewSet
)

router = DefaultRouter()
router.register(r'artists', ArtistViewSet)
router.register(r'albums', AlbumViewSet)
router.register(r'songs', SongViewSet)
router.register(r'tags', TagViewSet)
router.register(r'playlists', PlaylistViewSet, basename='playlist')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'history', PlayHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
] 