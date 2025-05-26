from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Avg, Max
from django.utils import timezone

from .models import Artist, Album, Song, Tag, Playlist, Favorite, Comment, Rating, PlayHistory, PlaylistSong
from .serializers import (
    ArtistSerializer, AlbumSerializer, SongSerializer, SongDetailSerializer,
    TagSerializer, PlaylistSerializer, PlaylistDetailSerializer,
    CommentSerializer, RatingSerializer, FavoriteSerializer, PlayHistorySerializer,
    FavoriteCreateSerializer
)

class ArtistViewSet(viewsets.ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True)
    def songs(self, request, pk=None):
        artist = self.get_object()
        songs = Song.objects.filter(artist=artist)
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True)
    def albums(self, request, pk=None):
        artist = self.get_object()
        albums = Album.objects.filter(artist=artist)
        serializer = AlbumSerializer(albums, many=True, context={'request': request})
        return Response(serializer.data)

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'artist__name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True)
    def songs(self, request, pk=None):
        album = self.get_object()
        songs = Song.objects.filter(album=album)
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'artist__name', 'album__title']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SongDetailSerializer
        return SongSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'play', 'comments']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['post'])
    def play(self, request, pk=None):
        song = self.get_object()
        # 增加播放次数
        song.play_count += 1
        song.save()
        
        # 记录播放历史（仅登录用户）
        if request.user.is_authenticated:
            PlayHistory.objects.create(user=request.user, song=song)
            
        return Response({'status': 'success'})
    
    @action(detail=True)
    def comments(self, request, pk=None):
        song = self.get_object()
        comments = Comment.objects.filter(song=song).order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        song = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, song=song)
        if created:
            return Response({'status': 'added to favorites'})
        return Response({'status': 'already in favorites'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unfavorite(self, request, pk=None):
        song = self.get_object()
        try:
            favorite = Favorite.objects.get(user=request.user, song=song)
            favorite.delete()
            return Response({'status': 'removed from favorites'})
        except Favorite.DoesNotExist:
            return Response({'status': 'not in favorites'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        song = self.get_object()
        score = request.data.get('score')
        
        if not score or not isinstance(score, int) or not (1 <= score <= 5):
            return Response({'error': '评分必须是1-5之间的整数'}, status=status.HTTP_400_BAD_REQUEST)
        
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            song=song,
            defaults={'score': score}
        )
        
        return Response({
            'status': 'rated' if created else 'updated',
            'score': score
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        song = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': '评论内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(
            user=request.user,
            song=song,
            content=content
        )
        
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=False, permission_classes=[AllowAny])
    def recommended(self, request):
        # 简单推荐：返回播放次数最多的歌曲
        songs = Song.objects.all().order_by('-play_count')[:10]
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(methods=['get'], detail=False, permission_classes=[AllowAny])
    def trending(self, request):
        # 获取最近一周内被播放最多的歌曲
        one_week_ago = timezone.now() - timezone.timedelta(days=7)
        songs = Song.objects.filter(
            play_history__played_at__gte=one_week_ago
        ).annotate(
            play_count_recent=Count('play_history')
        ).order_by('-play_count_recent')[:10]
        
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated])
    def personalized(self, request):
        # 基于用户收藏和播放历史的个性化推荐
        # 这里使用简单逻辑，实际可以接入更复杂的推荐算法
        user = request.user
        
        # 获取用户收藏的歌曲的标签
        favorite_tags = Tag.objects.filter(
            songs__song__favorites__user=user
        ).values_list('id', flat=True)
        
        # 获取含有这些标签的其他歌曲
        recommended_songs = Song.objects.filter(
            tags__tag__id__in=favorite_tags
        ).exclude(
            favorites__user=user  # 排除已收藏的
        ).annotate(
            tag_count=Count('tags')
        ).order_by('-tag_count', '-play_count')[:10]
        
        serializer = SongSerializer(recommended_songs, many=True, context={'request': request})
        return Response(serializer.data)

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    
    @action(detail=True)
    def songs(self, request, pk=None):
        tag = self.get_object()
        songs = Song.objects.filter(tags__tag=tag)
        serializer = SongSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)

class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'user__nickname']
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            # 返回用户自己的所有播放列表和其他公开的播放列表
            return Playlist.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        # 未登录用户只能看到公开播放列表
        return Playlist.objects.filter(is_public=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaylistDetailSerializer
        return PlaylistSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def add_song(self, request, pk=None):
        playlist = self.get_object()
        
        # 检查是否是播放列表拥有者
        if playlist.user != request.user:
            return Response(
                {'error': '只有播放列表创建者才能添加歌曲'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({'error': '缺少song_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            song = Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return Response({'error': '歌曲不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取最大顺序值
        max_order = playlist.playlist_songs.aggregate(max_order=Max('order'))['max_order'] or 0
        
        # 添加歌曲到播放列表
        playlist_song, created = PlaylistSong.objects.get_or_create(
            playlist=playlist,
            song=song,
            defaults={'order': max_order + 1}
        )
        
        if created:
            return Response({'status': 'added to playlist'})
        return Response({'status': 'already in playlist'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def remove_song(self, request, pk=None):
        playlist = self.get_object()
        
        # 检查是否是播放列表拥有者
        if playlist.user != request.user:
            return Response(
                {'error': '只有播放列表创建者才能删除歌曲'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({'error': '缺少song_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            playlist_song = PlaylistSong.objects.get(playlist=playlist, song_id=song_id)
            playlist_song.delete()
            return Response({'status': 'removed from playlist'})
        except PlaylistSong.DoesNotExist:
            return Response({'status': 'not in playlist'}, status=status.HTTP_404_NOT_FOUND)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FavoriteCreateSerializer
        return FavoriteSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """切换收藏状态"""
        song_id = request.data.get('song_id')
        if not song_id:
            return Response({'error': '缺少song_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            favorite = Favorite.objects.get(user=request.user, song_id=song_id)
            favorite.delete()
            return Response({'message': '取消收藏成功', 'is_favorite': False})
        except Favorite.DoesNotExist:
            # 创建收藏
            serializer = FavoriteCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({'message': '收藏成功', 'is_favorite': True})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """检查歌曲是否已收藏"""
        song_id = request.query_params.get('song_id')
        if not song_id:
            return Response({'error': '缺少song_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_favorite = Favorite.objects.filter(user=request.user, song_id=song_id).exists()
        return Response({'is_favorite': is_favorite})

class PlayHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PlayHistory.objects.filter(user=self.request.user)
