from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.contrib.auth import get_user_model
from concurrent.futures import ThreadPoolExecutor, as_completed
from music.models import Favorite
from music.serializers import FavoriteSerializer


class BaseSearchView(APIView):
	def get_search_params(self, request):
		keyword = request.GET.get("keyword", "")
		return keyword

	def keyword_api(self, params):
		api_url = "https://apis.netstart.cn/music/cloudsearch"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")
		
	def newsong_api(self):
		api_url = "https://apis.netstart.cn/music/personalized/newsong"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")




class AdvancedSearchView(APIView):
	def get_search_params(self, request):
		id = request.GET.get("id", "")
		return id

	def artist_api(self, params):
		api_url = "https://apis.netstart.cn/music/artists"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")

	def album_api(self, params):
		api_url = "https://apis.netstart.cn/music/album"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")

	def song_api(self, params):
		api_url = "http://music.alger.fun/music_proxy/music"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")

	def lyric_api(self, params):
		api_url = "https://apis.netstart.cn/music/lyric"
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Accept": "application/json, text/plain, */*",
			"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
			"Origin": "https://music.163.com",
			"Referer": "https://music.163.com/",
		}
		try:
			response = requests.get(api_url, params=params, headers=headers)
			# print(response.text)
			return response.json()
		except Exception as e:
			raise Exception(f"API调用失败: {str(e)}")





class SearchByDescView(BaseSearchView):
	def fetch_song_info(self, name):
		params = {
			"keywords": name,
			"type": 1,
			"limit": 3,
		}
		try:
			data = self.keyword_api(params)
			result = data.get("result", {})
			songs = result.get("songs", [])
			song_infos = []
			for song in songs:
				song_infos.append(
					{
						"name": song.get("name"),
						"id": song.get("id"),
						"ar": [
							{
								"id": ar.get("id"),
								"name": ar.get("name"),
								"tns": ar.get("tns", []),
								"alias": ar.get("alias", []),
							}
							for ar in song.get("ar", [])
						],
						"al": {
							"id": song.get("al", {}).get("id"),
							"name": song.get("al", {}).get("name"),
							"picUrl": song.get("al", {}).get("picUrl"),
							"tns": song.get("al", {}).get("tns", []),
						},
						"publishTime": song.get("publishTime", 0),
					}
				)
			return song_infos
		except Exception:
			return []

	def get(self, request):
		describe = request.GET.get("describe", "")

		if not describe:
			return Response(
				{"code": 403, "message": "请输入描述"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			api_key = "sk-uvxthytexestpleawhxcjtqdjwrzsszrwbcebbhlbxhbnlud"
			song_infos = get_song_names_from_deepseek(describe, api_key)
		except Exception as e:
			return Response(
				{"code": 500, "message": f"AI分析出错: {str(e)}"},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		full_song_infos = []
		with ThreadPoolExecutor(max_workers=8) as executor:  # 8线程，可根据实际情况调整
			future_to_name = {
				executor.submit(self.fetch_song_info, name): name for name in song_infos
			}
			for future in as_completed(future_to_name):
				result = future.result()
				if result:
					full_song_infos.extend(result)
		return Response(
			{
				"code": 200,
				"message": "success",
				"data": full_song_infos,
			}
		)


def get_song_names_from_deepseek(description, api_key):
	url = "https://api.siliconflow.cn/v1/chat/completions"  # 假设的 DeepSeek endpoint
	prompt = (
		f"请根据以下描述，推荐20首不同的歌曲名称，只返回歌名列表，不要有其他内容，歌曲有名一点，中文歌曲和英文歌曲最好都有\n描述：{description}\n"
		"严格按照如下格式返回：\n歌名1\n歌名2\n...\n歌名20"
	)
	payload = {
		"model": "deepseek-ai/DeepSeek-V3",  # 具体模型名按实际填写
		"messages": [{"role": "user", "content": prompt}],
		"max_tokens": 512,
		"temperature": 0.7,
		"n": 1,
		"stop": None,
	}
	headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()
	result = response.json()
	# 假设返回格式和OpenAI一致
	text = result["choices"][0]["message"]["content"]
	# 解析歌名
	song_names = [line.strip() for line in text.split("\n") if line.strip()]
	# 去重，只取前20个
	unique_song_names = []
	for name in song_names:
		if name not in unique_song_names:
			unique_song_names.append(name)
		if len(unique_song_names) == 20:
			break
	return unique_song_names


class SearchBySpiritView(BaseSearchView):
	def fetch_song_info(self, name):
		params = {
			"keywords": name,
			"type": 1,
			"limit": 3,
		}
		try:
			data = self.keyword_api(params)
			result = data.get("result", {})
			songs = result.get("songs", [])
			song_infos = []
			for song in songs:
				song_infos.append(
					{
						"name": song.get("name"),
						"id": song.get("id"),
						"ar": [
							{
								"id": ar.get("id"),
								"name": ar.get("name"),
								"tns": ar.get("tns", []),
								"alias": ar.get("alias", []),
							}
							for ar in song.get("ar", [])
						],
						"al": {
							"id": song.get("al", {}).get("id"),
							"name": song.get("al", {}).get("name"),
							"picUrl": song.get("al", {}).get("picUrl"),
							"tns": song.get("al", {}).get("tns", []),
						},
						"publishTime": song.get("publishTime", 0),
					}
				)
			return song_infos
		except Exception:
			return []

	def get(self, request):
		describe = request.GET.get("spirit", "")

		if not describe:
			return Response(
				{"code": 403, "message": "请输入情感"},
				status=status.HTTP_400_BAD_REQUEST,
			)

		try:
			api_key = "sk-uvxthytexestpleawhxcjtqdjwrzsszrwbcebbhlbxhbnlud"
			song_infos = get_song_names_by_emotion(describe, api_key)
		except Exception as e:
			return Response(
				{"code": 500, "message": f"AI分析出错: {str(e)}"},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		full_song_infos = []
		with ThreadPoolExecutor(max_workers=8) as executor:  # 8线程，可根据实际情况调整
			future_to_name = {
				executor.submit(self.fetch_song_info, name): name for name in song_infos
			}
			for future in as_completed(future_to_name):
				result = future.result()
				if result:
					full_song_infos.extend(result)
		return Response(
			{
				"code": 200,
				"message": "success",
				"data": full_song_infos,
			}
		)


def get_song_names_by_emotion(description, api_key):
	url = "https://api.siliconflow.cn/v1/chat/completions"  # 假设的 DeepSeek endpoint
	prompt = (
		f"请根据以下情绪，推荐20首不同的歌曲名称，只返回歌名列表，不要有其他内容，歌曲有名一点，中文歌曲和英文歌曲最好都有\n描述：{description}\n"
		"严格按照如下格式返回：\n歌名1\n歌名2\n...\n歌名20"
	)
	payload = {
		"model": "deepseek-ai/DeepSeek-V3",  # 具体模型名按实际填写
		"messages": [{"role": "user", "content": prompt}],
		"max_tokens": 512,
		"temperature": 0.7,
		"n": 1,
		"stop": None,
	}
	headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()
	result = response.json()
	# 假设返回格式和OpenAI一致
	text = result["choices"][0]["message"]["content"]
	# 解析歌名
	song_names = [line.strip() for line in text.split("\n") if line.strip()]
	# 去重，只取前20个
	unique_song_names = []
	for name in song_names:
		if name not in unique_song_names:
			unique_song_names.append(name)
		if len(unique_song_names) == 20:
			break
	return unique_song_names


class SearchGuess(BaseSearchView):
	def fetch_song_info(self, name):
		params = {
			"keywords": name,
			"type": 1,
			"limit": 1,
		}
		try:
			data = self.keyword_api(params)
			result = data.get("result", {})
			songs = result.get("songs", [])
			song_infos = []
			for song in songs:
				song_infos.append(
					{
						"name": song.get("name"),
						"id": song.get("id"),
						"ar": [
							{
								"id": ar.get("id"),
								"name": ar.get("name"),
								"tns": ar.get("tns", []),
								"alias": ar.get("alias", []),
							}
							for ar in song.get("ar", [])
						],
						"al": {
							"id": song.get("al", {}).get("id"),
							"name": song.get("al", {}).get("name"),
							"picUrl": song.get("al", {}).get("picUrl"),
							"tns": song.get("al", {}).get("tns", []),
						},
						"publishTime": song.get("publishTime", 0),
					}
				)
			return song_infos
		except Exception:
			return []

	def get(self, request):
		favorites = Favorite.objects.filter(user=request.user)
		song_names = [fav.song_name for fav in favorites]
		song_names_str = "、".join(song_names)
		try:
			api_key = "sk-uvxthytexestpleawhxcjtqdjwrzsszrwbcebbhlbxhbnlud"
			song_infos = get_song_by_guess(song_names_str, api_key)
			print(song_infos)
		except Exception as e:
			return Response(
				{"code": 500, "message": f"AI分析出错: {str(e)}"},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		full_song_infos = []
		with ThreadPoolExecutor(max_workers=8) as executor:  # 8线程，可根据实际情况调整
			future_to_name = {
				executor.submit(self.fetch_song_info, name): name for name in song_infos
			}
			for future in as_completed(future_to_name):
				result = future.result()
				if result:
					full_song_infos.extend(result)
		return Response(
			{
				"code": 200,
				"message": "success",
				"data": full_song_infos,
			}
		)


def get_song_by_guess(song_names_str, api_key):
	url = "https://api.siliconflow.cn/v1/chat/completions"  # 假设的 DeepSeek endpoint
	prompt = (
		f"请根据以下歌曲名称，推荐10首类似相关但是不同的歌曲名称，只返回歌名列表，不要有其他内容，歌曲有名一点，中文歌曲和英文歌曲最好都有\n歌名：{song_names_str}\n"
		"严格按照如下格式返回：\n歌名1\n歌名2\n...\n歌名10"
	)
	payload = {
		"model": "deepseek-ai/DeepSeek-V3",  # 具体模型名按实际填写
		"messages": [{"role": "user", "content": prompt}],
		"max_tokens": 512,
		"temperature": 0.7,
		"n": 1,
		"stop": None,
	}
	headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()
	result = response.json()
	# 假设返回格式和OpenAI一致
	text = result["choices"][0]["message"]["content"]
	# 解析歌名
	song_names = [line.strip() for line in text.split("\n") if line.strip()]
	# 去重，只取前10个
	unique_song_names = []
	for name in song_names:
		if name not in unique_song_names:
			unique_song_names.append(name)
		if len(unique_song_names) == 10:
			break
	return unique_song_names


class SearchRelated(BaseSearchView):
	def fetch_song_info(self, name):
		params = {
			"keywords": name,
			"type": 1,
			"limit": 2,
		}
		try:
			data = self.keyword_api(params)
			result = data.get("result", {})
			songs = result.get("songs", [])
			song_infos = []
			for song in songs:
				song_infos.append(
					{
						"name": song.get("name"),
						"id": song.get("id"),
						"ar": [
							{
								"id": ar.get("id"),
								"name": ar.get("name"),
								"tns": ar.get("tns", []),
								"alias": ar.get("alias", []),
							}
							for ar in song.get("ar", [])
						],
						"al": {
							"id": song.get("al", {}).get("id"),
							"name": song.get("al", {}).get("name"),
							"picUrl": song.get("al", {}).get("picUrl"),
							"tns": song.get("al", {}).get("tns", []),
						},
						"publishTime": song.get("publishTime", 0),
					}
				)
			return song_infos
		except Exception:
			return []

	def get(self, request):
		search_song = request.GET.get("title", "")

		if not search_song:
			return Response(
				{"code": 403, "message": "请输入歌曲"},
				status=status.HTTP_400_BAD_REQUEST,
			)
		try:
			api_key = "sk-uvxthytexestpleawhxcjtqdjwrzsszrwbcebbhlbxhbnlud"
			song_infos = get_song_by_title(search_song, api_key)
		except Exception as e:
			return Response(
				{"code": 500, "message": f"AI分析出错: {str(e)}"},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		full_song_infos = []
		with ThreadPoolExecutor(max_workers=8) as executor:  # 8线程，可根据实际情况调整
			future_to_name = {
				executor.submit(self.fetch_song_info, name): name for name in song_infos
			}
			for future in as_completed(future_to_name):
				result = future.result()
				if result:
					full_song_infos.extend(result)
		return Response(
			{
				"code": 200,
				"message": "success",
				"data": full_song_infos,
			}
		)


def get_song_by_title(song_names_str, api_key):
	url = "https://api.siliconflow.cn/v1/chat/completions"  # 假设的 DeepSeek endpoint
	prompt = (
		f"请根据歌曲名称，推荐10首类似相关但是不同的歌曲名称，只返回歌名列表，不要有其他内容，歌曲有名一点，中文歌曲和英文歌曲最好都有\n歌名：{song_names_str}\n"
		"严格按照如下格式返回：\n歌名1\n歌名2\n...\n歌名10"
	)
	payload = {
		"model": "deepseek-ai/DeepSeek-V3",  # 具体模型名按实际填写
		"messages": [{"role": "user", "content": prompt}],
		"max_tokens": 512,
		"temperature": 0.7,
		"n": 1,
		"stop": None,
	}
	headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
	response = requests.post(url, json=payload, headers=headers)
	response.raise_for_status()
	result = response.json()
	# 假设返回格式和OpenAI一致
	text = result["choices"][0]["message"]["content"]
	# 解析歌名
	song_names = [line.strip() for line in text.split("\n") if line.strip()]
	# 去重，只取前10个
	unique_song_names = []
	for name in song_names:
		if name not in unique_song_names:
			unique_song_names.append(name)
		if len(unique_song_names) == 10:
			break
	return unique_song_names

class SearchNewSongView(BaseSearchView):
	def get(self, request):
		try:
			data = self.newsong_api()
			if data.get("code") == 200:
				results = data.get("result", [])

				formatted_results = []
				for result in results:
					song = result.get("song", [])
					formatted_results.append(
						{
							"name": song.get("name"),
							"id": song.get("id"),
							"ar": [
								{
									"id": ar.get("id"),
									"name": ar.get("name"),
									"picUrl": ar.get("picUrl")
								}
								for ar in song.get("artists", [])
							],
							"al": {
								"id": song.get("album", {}).get("id"),
								"name": song.get("album", {}).get("name"),
								"picUrl": song.get("album", {}).get("picUrl"),
							},
							"publishTime": song.get("album", {}).get("publishTime", 0),
						}
					)
				return Response(
					{"code": 200, "message": "success", "data": formatted_results}
				)
			return Response(
				{"code": 403, "message": "failed"}, status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			return Response(
				{
					"code": 500,
					"message": f"获取新歌失败: {str(e)}",
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
