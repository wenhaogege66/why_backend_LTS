from rest_framework import serializers
from .models import Artist, Album, Song, Tag, Playlist, Favorite, Comment, Rating, PlayHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'image_url']

class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    
    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'artist_name', 'cover_url', 'release_date']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class SongSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    album_title = serializers.CharField(source='album.title', read_only=True, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Song
        fields = ['id', 'title', 'artist', 'artist_name', 'album', 'album_title', 
                 'audio_url', 'cover_url', 'duration', 'lyrics', 'play_count', 
                 'tags', 'average_rating', 'created_at']
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings:
            return 0
        return sum(rating.score for rating in ratings) / len(ratings)

class SongDetailSerializer(SongSerializer):
    is_favorite = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    
    class Meta(SongSerializer.Meta):
        fields = SongSerializer.Meta.fields + ['is_favorite', 'user_rating']
    
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, song=obj).exists()
        return False
    
    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = Rating.objects.get(user=request.user, song=obj)
                return rating.score
            except Rating.DoesNotExist:
                pass
        return None

class PlaylistSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    song_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'title', 'user', 'user_nickname', 'cover_url', 'is_public', 'song_count', 'created_at']
    
    def get_song_count(self, obj):
        return obj.playlist_songs.count()

class PlaylistDetailSerializer(PlaylistSerializer):
    songs = serializers.SerializerMethodField()
    
    class Meta(PlaylistSerializer.Meta):
        fields = PlaylistSerializer.Meta.fields + ['songs']
    
    def get_songs(self, obj):
        playlist_songs = obj.playlist_songs.all().order_by('order')
        return SongSerializer([ps.song for ps in playlist_songs], many=True, context=self.context).data

class CommentSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.CharField(source='user.avatar_url', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_nickname', 'user_avatar', 'song', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'song', 'score', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def validate_score(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("评分必须在1-5之间")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        rating, created = Rating.objects.update_or_create(
            user=validated_data['user'],
            song=validated_data['song'],
            defaults={'score': validated_data['score']}
        )
        return rating

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'song_id', 'song_name', 'artist_name', 'album_name', 'pic_url', 'created_at']
        read_only_fields = ['id', 'created_at']

class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['song_id', 'song_name', 'artist_name', 'album_name', 'pic_url']

class PlayHistorySerializer(serializers.ModelSerializer):
    song_detail = SongSerializer(source='song', read_only=True)
    
    class Meta:
        model = PlayHistory
        fields = ['id', 'user', 'song', 'song_detail', 'played_at']
        read_only_fields = ['user', 'played_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 