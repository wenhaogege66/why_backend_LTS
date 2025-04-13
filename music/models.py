from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'artist'
        verbose_name = '艺术家'
        verbose_name_plural = '艺术家'
    
    def __str__(self):
        return self.name

class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    cover_url = models.URLField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'album'
        verbose_name = '专辑'
        verbose_name_plural = '专辑'
    
    def __str__(self):
        return self.title

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs', null=True, blank=True)
    audio_url = models.URLField()
    cover_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(default=0)  # 歌曲时长（秒）
    lyrics = models.TextField(blank=True, null=True)
    play_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'song'
        verbose_name = '歌曲'
        verbose_name_plural = '歌曲'
    
    def __str__(self):
        return self.title

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'tag'
        verbose_name = '标签'
        verbose_name_plural = '标签'
    
    def __str__(self):
        return self.name

class SongTag(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='songs')
    
    class Meta:
        db_table = 'song_tag'
        unique_together = ('song', 'tag')
        verbose_name = '歌曲标签'
        verbose_name_plural = '歌曲标签'

class Playlist(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    cover_url = models.URLField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'playlist'
        verbose_name = '播放列表'
        verbose_name_plural = '播放列表'
    
    def __str__(self):
        return self.title

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='playlist_songs')
    order = models.IntegerField(default=0)
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'playlist_song'
        unique_together = ('playlist', 'song')
        verbose_name = '播放列表歌曲'
        verbose_name_plural = '播放列表歌曲'

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'favorite'
        unique_together = ('user', 'song')
        verbose_name = '收藏'
        verbose_name_plural = '收藏'

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'comment'
        verbose_name = '评论'
        verbose_name_plural = '评论'

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField()  # 1-5分
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'rating'
        unique_together = ('user', 'song')
        verbose_name = '评分'
        verbose_name_plural = '评分'

class PlayHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='play_history')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='play_history')
    played_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'play_history'
        verbose_name = '播放历史'
        verbose_name_plural = '播放历史'
        ordering = ['-played_at']
