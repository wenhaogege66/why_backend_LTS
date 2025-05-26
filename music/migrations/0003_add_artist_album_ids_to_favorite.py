# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_update_favorite_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='artist_id',
            field=models.IntegerField(blank=True, null=True, help_text='歌手ID（来自第三方API）'),
        ),
        migrations.AddField(
            model_name='favorite',
            name='album_id',
            field=models.IntegerField(blank=True, null=True, help_text='专辑ID（来自第三方API）'),
        ),
    ]
 