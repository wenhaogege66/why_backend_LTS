from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.contrib.auth import get_user_model

class BaseSearchView(APIView):
	def get_search_params(self, request):
		keyword = request.GET.get('keyword', '')
		return keyword

	def keyword_api(self, params):
		api_url = 'https://apis.netstart.cn/music/cloudsearch'
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'application/json, text/plain, */*',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Origin': 'https://music.163.com',
			'Referer': 'https://music.163.com/',
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f'API调用失败: {str(e)}')

class SearchByTitleView(BaseSearchView):
	def get(self, request):
		keyword = self.get_search_params(request)
		if not keyword:
			return Response({'code': 403, 'message': '请输入搜索关键词'}, status=status.HTTP_400_BAD_REQUEST)

		params = {
			'keywords': keyword,
			'type': 1,  # 歌曲
			'limit': 100  # 获取足够多的结果以便分页
		}

		try:
			data = self.keyword_api(params)
			if data.get('code') == 200:
				result = data.get('result', {})
				all_songs = result.get('songs', [])
				
				formatted_results = []
				for song in all_songs:
					formatted_results.append({
						'name': song.get('name'),
						'id': song.get('id'),
						'ar': [{
							'id': ar.get('id'),
							'name': ar.get('name'),
							'tns': ar.get('tns', []),
							'alias': ar.get('alias', [])
						} for ar in song.get('ar', [])],
						'al': {
							'id': song.get('al', {}).get('id'),
							'name': song.get('al', {}).get('name'),
							'picUrl': song.get('al', {}).get('picUrl'),
							'tns': song.get('al', {}).get('tns', [])
						},
						'publishTime': song.get('publishTime', 0)
					})
				return Response({
					'code': 200,
					'message': 'success',
					'data': formatted_results
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchByArtistView(BaseSearchView):
	def get(self, request):
		keyword = self.get_search_params(request)
		if not keyword:
			return Response({'code': 403, 'message': '请输入搜索关键词'}, status=status.HTTP_400_BAD_REQUEST)

		params = {
			'keywords': keyword,
			'type': 100,  # 歌手
			'limit': 100  # 获取足够多的结果以便分页
		}

		try:
			data = self.keyword_api(params)
			if data.get('code') == 200:
				result = data.get('result', {})
				all_artists = result.get('artists', [])
				formatted_results = []
				for artist in all_artists:
					formatted_results.append({
						'id': artist.get('id'),
						'name': artist.get('name'),
						'picUrl': artist.get('picUrl'),
						'alias': artist.get('alias', []),
						'albumSize': artist.get('albumSize', 0),
						'mvSize': artist.get('mvSize', 0)
					})
				return Response({
					'code': 200,
					'message': 'success',
					'data': formatted_results
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchByAlbumView(BaseSearchView):
	def get(self, request):
		keyword = self.get_search_params(request)
		if not keyword:
			return Response({'code': 403, 'message': '请输入搜索关键词'}, status=status.HTTP_400_BAD_REQUEST)

		params = {
			'keywords': keyword,
			'type': 10,  # 专辑
			'limit': 100  # 获取足够多的结果以便分页
		}

		try:
			data = self.keyword_api(params)
			if data.get('code') == 200:
				result = data.get('result', {})
				all_albums = result.get('albums', [])
				formatted_results = []
				for album in all_albums:
					formatted_results.append({
						'name': album.get('name'),
						'id': album.get('id'),
						'size': album.get('size', 0),
						'picUrl': album.get('picUrl'),
						'publishTime': album.get('publishTime', 0),
						'company': album.get('company', ''),
						'alias': album.get('alias', []),
						'artists': [{
							'name': ar.get('name'),
							'id': ar.get('id'),
							'picUrl': ar.get('picUrl')
						} for ar in album.get('artists', [])]
					})

				return Response({
					'code': 200,
					'message': 'success',
					'data': formatted_results
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AdvancedSearchView(APIView):
	def get_search_params(self, request):
		id = request.GET.get('id', '')
		return id

	def artist_api(self, params):
		api_url = 'https://apis.netstart.cn/music/artists'
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'application/json, text/plain, */*',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Origin': 'https://music.163.com',
			'Referer': 'https://music.163.com/',
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f'API调用失败: {str(e)}')
	
	def album_api(self, params):
		api_url = 'https://apis.netstart.cn/music/album'
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'application/json, text/plain, */*',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Origin': 'https://music.163.com',
			'Referer': 'https://music.163.com/',
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f'API调用失败: {str(e)}')
		
	def song_api(self, params):
		api_url = 'http://music.alger.fun/music_proxy/music'
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'application/json, text/plain, */*',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Origin': 'http://music.alger.fun/',
			'Referer': 'http://music.alger.fun/',
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f'API调用失败: {str(e)}')
		
	def lyric_api(self, params):
		api_url = 'https://apis.netstart.cn/music/lyric'
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'application/json, text/plain, */*',
			'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
			'Origin': 'https://music.163.com',
			'Referer': 'https://music.163.com/',
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f'API调用失败: {str(e)}')

class SearchByArtistSongView(AdvancedSearchView):
	def get(self, request):
		id = self.get_search_params(request)
		if not id:
			return Response({'code': 403, 'message': '请输入歌手id'}, status=status.HTTP_400_BAD_REQUEST)
		params = {
			'id': id
		}
		try:
			data = self.artist_api(params)
			if data.get('code') == 200:
				artist_info = data.get('artist', {})
				songs = data.get('hotSongs', [])
				
				# 格式化歌手信息
				formatted_artist = {
					'artist': {
						'briefDesc': artist_info.get('briefDesc', ''),
						'musicSize': artist_info.get('musicSize', 0),
						'albumSize': artist_info.get('albumSize', 0),
						'picUrl': artist_info.get('picUrl', ''),
						'alias': artist_info.get('alias', []),
						'name': artist_info.get('name', ''),
						'id': artist_info.get('id', 0),
						'publishTime': artist_info.get('publishTime', 0),
						'mvSize': artist_info.get('mvSize', 0)
					},
					'songs': []
				}

				# 格式化歌曲信息
				for song in songs:
					formatted_song = {
						'ar': [{
							'id': ar.get('id', 0),
							'name': ar.get('name', '')
						} for ar in song.get('ar', [])],
						'al': {
							'id': song.get('al', {}).get('id', 0),
							'name': song.get('al', {}).get('name', ''),
							'picUrl': song.get('al', {}).get('picUrl', '')
						},
						'name': song.get('name', ''),
						'id': song.get('id', 0)
					}
					formatted_artist['songs'].append(formatted_song)
				return Response({
					'code': 200,
					'message': 'success',
					'data': [formatted_artist]
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SearchByAlbumSongView(AdvancedSearchView):
	def get(self, request):
		id = self.get_search_params(request)
		if not id:
			return Response({'code': 403, 'message': '请输入专辑id'}, status=status.HTTP_400_BAD_REQUEST)
		params = {
			'id': id
		}
		try:
			data = self.album_api(params)
			if data.get('code') == 200:
				album_info = data.get('album', {})
				songs = data.get('songs', [])
				
				# 格式化专辑信息
				formatted_album = {
					'album': {
						'artist': {
							'musicSize': album_info.get('artist', {}).get('musicSize', 0),
							'albumSize': album_info.get('artist', {}).get('albumSize', 0),
							'picUrl': album_info.get('artist', {}).get('picUrl', ''),
							'alias': album_info.get('artist', {}).get('alias', []),
							'name': album_info.get('artist', {}).get('name', ''),
							'id': album_info.get('artist', {}).get('id', 0)
						},
						'company': album_info.get('company', ''),
						'picUrl': album_info.get('picUrl', ''),
						'alias': album_info.get('alias', []),
						'description': album_info.get('description', ''),
						'name': album_info.get('name', ''),
						'id': album_info.get('id', 0)
					},
					'songs': []
				}

				# 格式化歌曲信息
				for song in songs:
					formatted_song = {
						'ar': [{
							'id': ar.get('id', 0),
							'name': ar.get('name', '')
						} for ar in song.get('ar', [])],
						'al': {
							'id': song.get('al', {}).get('id', 0),
							'name': song.get('al', {}).get('name', ''),
							'picUrl': song.get('al', {}).get('picUrl', '')
						},
						'name': song.get('name', ''),
						'id': song.get('id', 0)
					}
					formatted_album['songs'].append(formatted_song)
				return Response({
					'code': 200,
					'message': 'success',
					'data': [formatted_album]
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		
class SearchBySongView(AdvancedSearchView):
	def get(self, request):
		id = self.get_search_params(request)
		if not id:
			return Response({'code': 403, 'message': '请输入歌曲id'}, status=status.HTTP_400_BAD_REQUEST)
		params = {
			'id': id
		}
		try:
			data = self.song_api(params)
			url = data.get('data', {}).get('url', '')
			data = self.lyric_api(params)
			lyric = data.get('lrc', {}).get('lyric', '')
			if url and lyric:
				return Response({
					'code': 200,
					'message': 'success',
					'data': {
						'url': url,
						'lyric': lyric
					}
				})
			return Response({'code': 403, 'message': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as e:
			return Response({'code': 500, 'message': f'搜索出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
