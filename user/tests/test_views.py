from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import User

class UserViewsTest(TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.client = APIClient()
        self.register_url = reverse('user-register')
        self.login_url = reverse('user-login')
        self.profile_url = reverse('user-profile')
        self.update_url = reverse('user-update')
        self.password_update_url = reverse('user-update-password')
        self.delete_url = reverse('user-delete')
        
        # 创建测试用户
        self.test_user = User.objects.create_user(
            email='test@example.com',
            password='Test123456',
            nickname='testuser'
        )
        
        # 登录获取token
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'Test123456'
        })
        self.token = response.data.get('data', {}).get('token')
        if self.token:
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_user_register_success(self):
        """测试用户注册成功"""
        data = {
            'email': 'newuser@example.com',
            'password': 'NewTest123456',
            'nickname': 'newuser'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '注册成功')

    def test_user_register_duplicate_email(self):
        """测试注册重复邮箱"""
        data = {
            'email': 'test@example.com',
            'password': 'Test123456',
            'nickname': 'testuser2'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40004)
        self.assertIn('该邮箱已被注册', response.data['message'])

    def test_user_register_invalid_password(self):
        """测试注册密码不符合要求"""
        data = {
            'email': 'newuser@example.com',
            'password': '123',
            'nickname': 'newuser'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40004)
        self.assertIn('密码长度不能少于8个字符', response.data['message'])

    def test_user_login_success(self):
        """测试用户登录成功"""
        data = {
            'email': 'test@example.com',
            'password': 'Test123456'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '登录成功')
        self.assertIn('token', response.data['data'])

    def test_user_login_wrong_password(self):
        """测试登录密码错误"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40003)
        self.assertEqual(response.data['message'], '邮箱或密码错误')

    def test_get_user_profile(self):
        """测试获取用户信息"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '获取成功')
        self.assertEqual(response.data['data']['email'], 'test@example.com')
        self.assertEqual(response.data['data']['nickname'], 'testuser')

    def test_update_user_profile(self):
        """测试更新用户信息"""
        data = {
            'nickname': 'updateduser'
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '更新成功')

    def test_update_user_profile_duplicate_nickname(self):
        """测试更新重复昵称"""
        # 先创建另一个用户
        User.objects.create_user(
            email='other@example.com',
            password='Test123456',
            nickname='otheruser'
        )
        
        data = {
            'nickname': 'otheruser'
        }
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40004)
        self.assertIn('该昵称已被使用', response.data['message'])

    def test_update_password_success(self):
        """测试修改密码成功"""
        data = {
            'password': 'Test123456',
            'new_password': 'NewTest123456'
        }
        response = self.client.put(self.password_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '密码修改成功')

    def test_update_password_wrong_old_password(self):
        """测试修改密码时原密码错误"""
        data = {
            'password': 'wrongpassword',
            'new_password': 'NewTest123456'
        }
        response = self.client.put(self.password_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40001)
        self.assertEqual(response.data['message'], '原密码错误')

    def test_update_password_same_password(self):
        """测试修改密码时新旧密码相同"""
        data = {
            'password': 'Test123456',
            'new_password': 'Test123456'
        }
        response = self.client.put(self.password_update_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 40002)
        self.assertEqual(response.data['message'], '新密码不能与旧密码相同')

    def test_delete_user(self):
        """测试删除用户"""
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], '注销成功')
        
        # 验证用户是否真的被删除
        self.assertFalse(User.objects.filter(email='test@example.com').exists())

    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 清除认证信息
        self.client.credentials()
        
        # 测试获取用户信息
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 测试更新用户信息
        response = self.client.put(self.update_url, {'nickname': 'newuser'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 测试修改密码
        response = self.client.put(self.password_update_url, {
            'password': 'oldpass',
            'new_password': 'newpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 测试删除用户
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 