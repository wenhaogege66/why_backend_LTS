import json
from unittest.mock import patch, Mock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from search.views import (
    BaseSearchView, SearchByTitleView, SearchByArtistView, 
    SearchByAlbumView, AdvancedSearchView, SearchByArtistSongView,
    SearchByAlbumSongView, SearchBySongView, SearchNewSongView
)


class BaseSearchViewTest(TestCase):
    """BaseSearchView 基础测试类"""
    
    def setUp(self):
        self.view = BaseSearchView()
        
    def test_get_search_params(self):
        """测试获取搜索参数"""
        # 创建模拟请求对象
        mock_request = Mock()
        mock_request.GET.get.return_value = 'test_keyword'
        
        result = self.view.get_search_params(mock_request)
        self.assertEqual(result, 'test_keyword')
        mock_request.GET.get.assert_called_once_with('keyword', '')
        
    def test_get_search_params_empty(self):
        """测试获取空搜索参数"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        result = self.view.get_search_params(mock_request)
        self.assertEqual(result, '')
        
    @patch('search.views.requests.get')
    def test_keyword_api_success(self, mock_get):
        """测试关键词API调用成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.json.return_value = {'code': 200, 'data': 'test'}
        mock_get.return_value = mock_response
        
        params = {'keywords': 'test', 'type': 1}
        result = self.view.keyword_api(params)
        
        self.assertEqual(result, {'code': 200, 'data': 'test'})
        mock_get.assert_called_once()
        
    @patch('search.views.requests.get')
    def test_keyword_api_failure(self, mock_get):
        """测试关键词API调用失败"""
        # 模拟请求异常
        mock_get.side_effect = Exception('Network error')
        
        params = {'keywords': 'test', 'type': 1}
        
        with self.assertRaises(Exception) as context:
            self.view.keyword_api(params)
            
        self.assertIn('API调用失败', str(context.exception))
        
    @patch('search.views.requests.get')
    def test_newsong_api_success(self, mock_get):
        """测试新歌API调用成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'code': 200, 'result': []}
        mock_get.return_value = mock_response
        
        result = self.view.newsong_api()
        
        self.assertEqual(result, {'code': 200, 'result': []})
        mock_get.assert_called_once()
        
    @patch('search.views.requests.get')
    def test_newsong_api_failure(self, mock_get):
        """测试新歌API调用失败"""
        mock_get.side_effect = Exception('Network error')
        
        with self.assertRaises(Exception) as context:
            self.view.newsong_api()
            
        self.assertIn('API调用失败', str(context.exception))


class SearchByTitleViewTest(APITestCase):
    """按标题搜索视图测试"""
    
    def setUp(self):
        self.view = SearchByTitleView()
        
    @patch.object(SearchByTitleView, 'keyword_api')
    def test_search_by_title_success(self, mock_api):
        """测试按标题搜索成功"""
        # 模拟API返回数据
        mock_api.return_value = {
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
        
        # 创建模拟请求
        mock_request = Mock()
        mock_request.GET.get.return_value = '测试歌曲'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], 'success')
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '测试歌曲')
        
    def test_search_by_title_no_keyword(self):
        """测试没有关键词的情况"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], '请输入搜索关键词')
        
    @patch.object(SearchByTitleView, 'keyword_api')
    def test_search_by_title_api_error(self, mock_api):
        """测试API调用错误"""
        mock_api.return_value = {'code': 400, 'message': 'error'}
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '测试'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        
    @patch.object(SearchByTitleView, 'keyword_api')
    def test_search_by_title_exception(self, mock_api):
        """测试异常处理"""
        mock_api.side_effect = Exception('API调用失败: Network error')
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '测试'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['code'], 500)
        self.assertIn('搜索出错', response.data['message'])


class SearchByArtistViewTest(APITestCase):
    """按歌手搜索视图测试"""
    
    def setUp(self):
        self.view = SearchByArtistView()
        
    @patch.object(SearchByArtistView, 'keyword_api')
    def test_search_by_artist_success(self, mock_api):
        """测试按歌手搜索成功"""
        mock_api.return_value = {
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
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '测试歌手'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '测试歌手')
        
    def test_search_by_artist_no_keyword(self):
        """测试没有关键词的情况"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)


class SearchByAlbumViewTest(APITestCase):
    """按专辑搜索视图测试"""
    
    def setUp(self):
        self.view = SearchByAlbumView()
        
    @patch.object(SearchByAlbumView, 'keyword_api')
    def test_search_by_album_success(self, mock_api):
        """测试按专辑搜索成功"""
        mock_api.return_value = {
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
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '测试专辑'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '测试专辑')


class AdvancedSearchViewTest(TestCase):
    """高级搜索视图基础测试"""
    
    def setUp(self):
        self.view = AdvancedSearchView()
        
    def test_get_search_params(self):
        """测试获取搜索参数（ID）"""
        mock_request = Mock()
        mock_request.GET.get.return_value = '123456'
        
        result = self.view.get_search_params(mock_request)
        self.assertEqual(result, '123456')
        
    @patch('search.views.requests.get')
    def test_artist_api_success(self, mock_get):
        """测试歌手API调用成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'code': 200, 'artist': {}}
        mock_get.return_value = mock_response
        
        params = {'id': '123'}
        result = self.view.artist_api(params)
        
        self.assertEqual(result, {'code': 200, 'artist': {}})
        
    @patch('search.views.requests.get')
    def test_album_api_success(self, mock_get):
        """测试专辑API调用成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'code': 200, 'album': {}}
        mock_get.return_value = mock_response
        
        params = {'id': '456'}
        result = self.view.album_api(params)
        
        self.assertEqual(result, {'code': 200, 'album': {}})
        
    @patch('search.views.requests.get')
    def test_song_api_success(self, mock_get):
        """测试歌曲API调用成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'data': {'url': 'http://music.mp3'}}
        mock_get.return_value = mock_response
        
        params = {'id': '789'}
        result = self.view.song_api(params)
        
        self.assertEqual(result, {'data': {'url': 'http://music.mp3'}})
        
    @patch('search.views.requests.get')
    def test_lyric_api_success(self, mock_get):
        """测试歌词API调用成功"""
        mock_response = Mock()
        mock_response.json.return_value = {'lrc': {'lyric': '[00:00]测试歌词'}}
        mock_get.return_value = mock_response
        
        params = {'id': '789'}
        result = self.view.lyric_api(params)
        
        self.assertEqual(result, {'lrc': {'lyric': '[00:00]测试歌词'}})


class SearchByArtistSongViewTest(APITestCase):
    """按歌手搜索歌曲视图测试"""
    
    def setUp(self):
        self.view = SearchByArtistSongView()
        
    @patch.object(SearchByArtistSongView, 'artist_api')
    def test_search_by_artist_song_success(self, mock_api):
        """测试按歌手搜索歌曲成功"""
        mock_api.return_value = {
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
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '123'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['artist']['name'], '测试歌手')
        self.assertEqual(len(response.data['data'][0]['songs']), 1)
        
    def test_search_by_artist_song_no_id(self):
        """测试没有ID的情况"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], '请输入歌手id')


class SearchByAlbumSongViewTest(APITestCase):
    """按专辑搜索歌曲视图测试"""
    
    def setUp(self):
        self.view = SearchByAlbumSongView()
        
    @patch.object(SearchByAlbumSongView, 'album_api')
    def test_search_by_album_song_success(self, mock_api):
        """测试按专辑搜索歌曲成功"""
        mock_api.return_value = {
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
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '456'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['album']['name'], '测试专辑')
        self.assertEqual(len(response.data['data'][0]['songs']), 1)
        
    def test_search_by_album_song_no_id(self):
        """测试没有ID的情况"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], '请输入专辑id')


class SearchBySongViewTest(APITestCase):
    """按歌曲搜索视图测试"""
    
    def setUp(self):
        self.view = SearchBySongView()
        
    @patch.object(SearchBySongView, 'lyric_api')
    @patch.object(SearchBySongView, 'song_api')
    def test_search_by_song_success(self, mock_song_api, mock_lyric_api):
        """测试按歌曲搜索成功"""
        mock_song_api.return_value = {
            'data': {'url': 'http://music.mp3'}
        }
        mock_lyric_api.return_value = {
            'lrc': {'lyric': '[00:00]测试歌词\n[00:10]第二行歌词'}
        }
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '789'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['data']['url'], 'http://music.mp3')
        self.assertIn('测试歌词', response.data['data']['lyric'])
        
    def test_search_by_song_no_id(self):
        """测试没有ID的情况"""
        mock_request = Mock()
        mock_request.GET.get.return_value = ''
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        self.assertEqual(response.data['message'], '请输入歌曲id')
        
    @patch.object(SearchBySongView, 'lyric_api')
    @patch.object(SearchBySongView, 'song_api')
    def test_search_by_song_no_url(self, mock_song_api, mock_lyric_api):
        """测试没有音乐URL的情况"""
        mock_song_api.return_value = {'data': {'url': ''}}
        mock_lyric_api.return_value = {'lrc': {'lyric': '[00:00]测试歌词'}}
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '789'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        
    @patch.object(SearchBySongView, 'lyric_api')
    @patch.object(SearchBySongView, 'song_api')
    def test_search_by_song_no_lyric(self, mock_song_api, mock_lyric_api):
        """测试没有歌词的情况"""
        mock_song_api.return_value = {'data': {'url': 'http://music.mp3'}}
        mock_lyric_api.return_value = {'lrc': {'lyric': ''}}
        
        mock_request = Mock()
        mock_request.GET.get.return_value = '789'
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)


class SearchNewSongViewTest(APITestCase):
    """搜索新歌视图测试"""
    
    def setUp(self):
        self.view = SearchNewSongView()
        
    @patch.object(SearchNewSongView, 'newsong_api')
    def test_search_new_song_success(self, mock_api):
        """测试搜索新歌成功"""
        mock_api.return_value = {
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
        
        mock_request = Mock()
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['name'], '新歌测试')
        self.assertEqual(response.data['data'][0]['ar'][0]['name'], '测试歌手')
        
    @patch.object(SearchNewSongView, 'newsong_api')
    def test_search_new_song_api_error(self, mock_api):
        """测试新歌API错误"""
        mock_api.return_value = {'code': 400, 'message': 'error'}
        
        mock_request = Mock()
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 403)
        
    @patch.object(SearchNewSongView, 'newsong_api')
    def test_search_new_song_exception(self, mock_api):
        """测试新歌搜索异常"""
        mock_api.side_effect = Exception('API调用失败: Network error')
        
        mock_request = Mock()
        
        response = self.view.get(mock_request)
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['code'], 500)
        self.assertIn('获取新歌失败', response.data['message'])


class IntegrationTest(APITestCase):
    """集成测试"""
    
    @patch('search.views.requests.get')
    def test_full_search_workflow(self, mock_get):
        """测试完整搜索工作流程"""
        # 模拟搜索歌曲的完整流程
        mock_response = Mock()
        mock_response.json.return_value = {
            'code': 200,
            'result': {
                'songs': [
                    {
                        'name': '集成测试歌曲',
                        'id': 123456,
                        'ar': [{'id': 1, 'name': '集成测试歌手', 'tns': [], 'alias': []}],
                        'al': {'id': 1, 'name': '集成测试专辑', 'picUrl': 'http://test.jpg', 'tns': []},
                        'publishTime': 1640995200000
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        view = SearchByTitleView()
        mock_request = Mock()
        mock_request.GET.get.return_value = '集成测试'
        
        response = view.get(mock_request)
        
        # 验证响应结构
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        
        # 验证数据格式
        song_data = response.data['data'][0]
        required_fields = ['name', 'id', 'ar', 'al', 'publishTime']
        for field in required_fields:
            self.assertIn(field, song_data)
            
        # 验证歌手信息格式
        artist_data = song_data['ar'][0]
        artist_required_fields = ['id', 'name', 'tns', 'alias']
        for field in artist_required_fields:
            self.assertIn(field, artist_data)
            
        # 验证专辑信息格式
        album_data = song_data['al']
        album_required_fields = ['id', 'name', 'picUrl', 'tns']
        for field in album_required_fields:
            self.assertIn(field, album_data)


class ErrorHandlingTest(APITestCase):
    """错误处理测试"""
    
    def test_network_timeout_handling(self):
        """测试网络超时处理"""
        with patch('search.views.requests.get') as mock_get:
            mock_get.side_effect = Exception('Connection timeout')
            
            view = SearchByTitleView()
            mock_request = Mock()
            mock_request.GET.get.return_value = '测试'
            
            response = view.get(mock_request)
            
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.data['code'], 500)
            self.assertIn('搜索出错', response.data['message'])
            
    def test_invalid_json_response_handling(self):
        """测试无效JSON响应处理"""
        with patch('search.views.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.side_effect = ValueError('Invalid JSON')
            mock_get.return_value = mock_response
            
            view = SearchByTitleView()
            mock_request = Mock()
            mock_request.GET.get.return_value = '测试'
            
            response = view.get(mock_request)
            
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.data['code'], 500)
            
    def test_empty_response_handling(self):
        """测试空响应处理"""
        with patch.object(SearchByTitleView, 'keyword_api') as mock_api:
            mock_api.return_value = {'code': 200, 'result': {'songs': []}}
            
            view = SearchByTitleView()
            mock_request = Mock()
            mock_request.GET.get.return_value = '不存在的歌曲'
            
            response = view.get(mock_request)
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['code'], 200)
            self.assertEqual(len(response.data['data']), 0)


class PerformanceTest(APITestCase):
    """性能测试"""
    
    @patch.object(SearchByTitleView, 'keyword_api')
    def test_large_result_set_handling(self, mock_api):
        """测试大结果集处理"""
        # 模拟大量搜索结果
        large_songs_list = []
        for i in range(100):
            large_songs_list.append({
                'name': f'测试歌曲{i}',
                'id': i,
                'ar': [{'id': i, 'name': f'歌手{i}', 'tns': [], 'alias': []}],
                'al': {'id': i, 'name': f'专辑{i}', 'picUrl': f'http://test{i}.jpg', 'tns': []},
                'publishTime': 1640995200000 + i
            })
            
        mock_api.return_value = {
            'code': 200,
            'result': {'songs': large_songs_list}
        }
        
        view = SearchByTitleView()
        mock_request = Mock()
        mock_request.GET.get.return_value = '热门'
        
        response = view.get(mock_request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 100)
        
        # 验证数据完整性
        for i, song in enumerate(response.data['data']):
            self.assertEqual(song['name'], f'测试歌曲{i}')
            self.assertEqual(song['id'], i)


if __name__ == '__main__':
    import unittest
    unittest.main() 