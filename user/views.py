from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordUpdateSerializer
)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({
                    'code': 0,
                    'message': '注册成功'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'code': 40003,
                    'message': f'注册请求处理失败: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'code': 40004,
            'message': '数据验证失败',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(email=email, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'code': 0,
                    'message': '登录成功',
                    'data': {
                        'token': str(refresh.access_token)
                    }
                })
            return Response({
                'code': 40003,
                'message': '密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({
            'code': 0,
            'message': '获取成功',
            'data': serializer.data
        })

class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'code': 0,
                'message': '更新成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordUpdateSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['password']):
                return Response({
                    'code': 40001,
                    'message': '原密码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if serializer.validated_data['password'] == serializer.validated_data['new_password']:
                return Response({
                    'code': 40002,
                    'message': '新密码与旧密码一致'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({
                'code': 0,
                'message': '密码修改成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            request.user.delete()
            return Response({
                'code': 0,
                'message': '注销成功'
            })
        except Exception as e:
            return Response({
                'code': 40002,
                'message': '注销请求处理失败，请稍后再试'
            }, status=status.HTTP_400_BAD_REQUEST)

