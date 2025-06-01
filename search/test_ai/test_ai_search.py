from django.test import TestCase, Client
from django.urls import reverse
from music.models import Song, Artist, Tag
import json

class AISearchTest(TestCase):
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.client = Client()
        
        # 创建测试数据
        self.artist1 = Artist.objects.create(name="周杰伦")
        self.artist2 = Artist.objects.create(name="林俊杰")
        
        self.tag1 = Tag.objects.create(name="流行")
        self.tag2 = Tag.objects.create(name="摇滚")
        
        self.song1 = Song.objects.create(
            title="晴天",
            artist=self.artist1,
            duration=180,
            release_date="2020-01-01"
        )
        self.song1.tags.add(self.tag1)
        
        self.song2 = Song.objects.create(
            title="江南",
            artist=self.artist2,
            duration=240,
            release_date="2020-02-01"
        )
        self.song2.tags.add(self.tag2)

    def test_basic_search(self):
        """测试基本搜索功能"""
        # 测试成功搜索
        response = self.client.get(reverse('search:ai_search'), {'query': '晴天'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['title'], '晴天')

        # 测试空查询
        response = self.client.get(reverse('search:ai_search'), {'query': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 2)  # 应该返回所有歌曲

        # 测试无搜索结果
        response = self.client.get(reverse('search:ai_search'), {'query': '不存在的歌曲'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 0)

    def test_advanced_search(self):
        """测试高级搜索功能"""
        # 测试按歌手搜索
        response = self.client.get(reverse('search:ai_search'), {'query': '周杰伦'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['data'][0]['artist']['name'], '周杰伦')

        # 测试按标签搜索
        response = self.client.get(reverse('search:ai_search'), {'query': '流行'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 1)
        self.assertTrue(any(tag['name'] == '流行' for tag in data['data'][0]['tags']))

    def test_pagination(self):
        """测试分页功能"""
        # 创建更多测试数据
        for i in range(15):
            song = Song.objects.create(
                title=f"测试歌曲{i}",
                artist=self.artist1,
                duration=180,
                release_date="2020-01-01"
            )
            song.tags.add(self.tag1)

        # 测试第一页
        response = self.client.get(reverse('search:ai_search'), {'query': '测试', 'page': 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 10)  # 默认每页10条

        # 测试第二页
        response = self.client.get(reverse('search:ai_search'), {'query': '测试', 'page': 2})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 5)  # 剩余5条

    def test_sorting(self):
        """测试排序功能"""
        # 测试按标题排序
        response = self.client.get(reverse('search:ai_search'), {
            'query': '',
            'sort_by': 'title',
            'sort_order': 'asc'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data'][0]['title'], '江南')
        self.assertEqual(data['data'][1]['title'], '晴天')

        # 测试按发行日期排序
        response = self.client.get(reverse('search:ai_search'), {
            'query': '',
            'sort_by': 'release_date',
            'sort_order': 'desc'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data'][0]['title'], '江南')
        self.assertEqual(data['data'][1]['title'], '晴天') 