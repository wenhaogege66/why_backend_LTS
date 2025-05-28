"""
测试配置文件
包含测试运行的配置和工具函数
"""

import os
import sys
from django.test.utils import get_runner
from django.conf import settings


class TestConfig:
    """测试配置类"""
    
    # 测试数据库配置
    TEST_DATABASE = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # 测试用的API响应模板
    MOCK_SONG_RESPONSE = {
        'code': 200,
        'result': {
            'songs': [
                {
                    'name': '测试歌曲',
                    'id': 123456,
                    'ar': [{'id': 1, 'name': '测试歌手', 'tns': [], 'alias': []}],
                    'al': {'id': 1, 'name': '测试专辑', 'picUrl': 'http://test.jpg', 'tns': []},
                    'publishTime': 1640995200000
                }
            ]
        }
    }
    
    MOCK_ARTIST_RESPONSE = {
        'code': 200,
        'result': {
            'artists': [
                {
                    'id': 123,
                    'name': '测试歌手',
                    'picUrl': 'http://test.jpg',
                    'alias': ['别名'],
                    'albumSize': 10,
                    'mvSize': 5
                }
            ]
        }
    }
    
    MOCK_ALBUM_RESPONSE = {
        'code': 200,
        'result': {
            'albums': [
                {
                    'name': '测试专辑',
                    'id': 456,
                    'size': 12,
                    'picUrl': 'http://test.jpg',
                    'publishTime': 1640995200000,
                    'company': '测试公司',
                    'alias': [],
                    'artists': [{'name': '测试歌手', 'id': 123, 'picUrl': 'http://artist.jpg'}]
                }
            ]
        }
    }
    
    MOCK_ARTIST_DETAIL_RESPONSE = {
        'code': 200,
        'artist': {
            'briefDesc': '测试歌手简介',
            'musicSize': 100,
            'albumSize': 10,
            'picUrl': 'http://artist.jpg',
            'alias': ['别名'],
            'name': '测试歌手',
            'id': 123,
            'publishTime': 1640995200000,
            'mvSize': 5
        },
        'hotSongs': [
            {
                'ar': [{'id': 123, 'name': '测试歌手'}],
                'al': {'id': 456, 'name': '测试专辑', 'picUrl': 'http://album.jpg'},
                'name': '热门歌曲',
                'id': 789
            }
        ]
    }
    
    MOCK_ALBUM_DETAIL_RESPONSE = {
        'code': 200,
        'album': {
            'artist': {
                'musicSize': 100,
                'albumSize': 10,
                'picUrl': 'http://artist.jpg',
                'alias': [],
                'name': '测试歌手',
                'id': 123
            },
            'company': '测试公司',
            'picUrl': 'http://album.jpg',
            'alias': [],
            'description': '专辑描述',
            'name': '测试专辑',
            'id': 456
        },
        'songs': [
            {
                'ar': [{'id': 123, 'name': '测试歌手'}],
                'al': {'id': 456, 'name': '测试专辑', 'picUrl': 'http://album.jpg'},
                'name': '专辑歌曲',
                'id': 789
            }
        ]
    }
    
    MOCK_SONG_DETAIL_RESPONSE = {
        'data': {'url': 'http://music.mp3'}
    }
    
    MOCK_LYRIC_RESPONSE = {
        'lrc': {'lyric': '[00:00]测试歌词\n[00:10]第二行歌词'}
    }
    
    MOCK_NEW_SONG_RESPONSE = {
        'code': 200,
        'result': [
            {
                'song': {
                    'name': '新歌测试',
                    'id': 999,
                    'artists': [{'id': 123, 'name': '测试歌手', 'picUrl': 'http://artist.jpg'}],
                    'album': {
                        'id': 456,
                        'name': '新专辑',
                        'picUrl': 'http://album.jpg',
                        'publishTime': 1640995200000
                    }
                }
            }
        ]
    }


def run_tests():
    """运行测试的工具函数"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # 运行测试
    execute_from_command_line(['manage.py', 'test', 'search.test'])


def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ['DJANGO_TESTING'] = 'True'
    
    # 禁用日志输出（可选）
    import logging
    logging.disable(logging.CRITICAL)


def teardown_test_environment():
    """清理测试环境"""
    # 重新启用日志
    import logging
    logging.disable(logging.NOTSET)
    
    # 清理环境变量
    if 'DJANGO_TESTING' in os.environ:
        del os.environ['DJANGO_TESTING']


if __name__ == '__main__':
    setup_test_environment()
    try:
        run_tests()
    finally:
        teardown_test_environment() 