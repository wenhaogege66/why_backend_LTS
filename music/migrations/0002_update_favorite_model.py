# Generated manually to update Favorite model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0001_initial'),
    ]

    operations = [
        # 删除旧的Favorite表
        migrations.DeleteModel(
            name='Favorite',
        ),
        
        # 创建新的Favorite表
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_id', models.IntegerField(default=0)),
                ('song_name', models.CharField(default='Unknown Song', max_length=200)),
                ('artist_name', models.CharField(default='Unknown Artist', max_length=200)),
                ('album_name', models.CharField(blank=True, default='', max_length=200)),
                ('pic_url', models.URLField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        
        # 添加唯一约束
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'song_id')},
        ),
    ] 