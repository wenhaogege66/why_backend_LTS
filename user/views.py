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
    PasswordUpdateSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(
                    {"code": 200, "message": "注册成功"}, status=status.HTTP_200_OK
                )
            except ValidationError as e:
                return Response(
                    {"code": 40003, "message": f"注册请求处理失败: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"code": 40005, "message": f"服务器内部错误: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        # 处理具体的验证错误
        error_messages = []
        for field, errors in serializer.errors.items():
            if field == 'email':
                if 'unique' in str(errors):
                    error_messages.append("该邮箱已被注册")
                elif 'invalid' in str(errors):
                    error_messages.append("邮箱格式不正确")
            elif field == 'password':
                if 'too_short' in str(errors):
                    error_messages.append("密码长度不能少于8个字符")
                elif 'too_common' in str(errors):
                    error_messages.append("密码过于简单，请使用更复杂的密码")
                elif 'numeric' in str(errors):
                    error_messages.append("密码不能全为数字")
            elif field == 'nickname':
                if 'unique' in str(errors):
                    error_messages.append("该昵称已被使用")
                elif 'blank' in str(errors):
                    error_messages.append("昵称不能为空")
        
        return Response(
            {
                "code": 40004,
                "message": "，".join(error_messages) if error_messages else "数据验证失败"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            
            try:
                user = authenticate(email=email, password=password)
                if user:
                    refresh = RefreshToken.for_user(user)
                    return Response(
                        {
                            "code": 200,
                            "message": "登录成功",
                            "data": {"token": str(refresh.access_token)},
                        }
                    )
                return Response(
                    {"code": 40003, "message": "邮箱或密码错误"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:
                return Response(
                    {"code": 40005, "message": f"登录过程发生错误: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        # 处理具体的验证错误
        error_messages = []
        for field, errors in serializer.errors.items():
            if field == 'email':
                if 'required' in str(errors):
                    error_messages.append("邮箱不能为空")
                elif 'invalid' in str(errors):
                    error_messages.append("邮箱格式不正确")
            elif field == 'password':
                if 'required' in str(errors):
                    error_messages.append("密码不能为空")
        
        return Response(
            {
                "code": 40004,
                "message": "，".join(error_messages) if error_messages else "数据验证失败"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = UserProfileSerializer(request.user)
            return Response(
                {"code": 200, "message": "获取成功", "data": serializer.data}
            )
        except Exception as e:
            return Response(
                {"code": 40005, "message": f"获取用户信息失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({"code": 200, "message": "更新成功"})
            except Exception as e:
                return Response(
                    {"code": 40005, "message": f"更新用户信息失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        # 处理具体的验证错误
        error_messages = []
        for field, errors in serializer.errors.items():
            if field == 'nickname':
                if 'unique' in str(errors):
                    error_messages.append("该昵称已被使用")
                elif 'blank' in str(errors):
                    error_messages.append("昵称不能为空")
            elif field == 'avatar_url':
                if 'invalid' in str(errors):
                    error_messages.append("头像URL格式不正确")
        
        return Response(
            {
                "code": 40004,
                "message": "，".join(error_messages) if error_messages else "数据验证失败"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = PasswordUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                if not request.user.check_password(serializer.validated_data["password"]):
                    return Response(
                        {"code": 40001, "message": "原密码错误"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if (
                    serializer.validated_data["password"]
                    == serializer.validated_data["new_password"]
                ):
                    return Response(
                        {"code": 40002, "message": "新密码不能与旧密码相同"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                request.user.set_password(serializer.validated_data["new_password"])
                request.user.save()
                return Response({"code": 200, "message": "密码修改成功"})
            except Exception as e:
                return Response(
                    {"code": 40005, "message": f"修改密码失败: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        
        # 处理具体的验证错误
        error_messages = []
        for field, errors in serializer.errors.items():
            if field == 'password':
                if 'required' in str(errors):
                    error_messages.append("原密码不能为空")
            elif field == 'new_password':
                if 'required' in str(errors):
                    error_messages.append("新密码不能为空")
                elif 'too_short' in str(errors):
                    error_messages.append("新密码长度不能少于8个字符")
                elif 'too_common' in str(errors):
                    error_messages.append("新密码过于简单，请使用更复杂的密码")
                elif 'numeric' in str(errors):
                    error_messages.append("新密码不能全为数字")
        
        return Response(
            {
                "code": 40004,
                "message": "，".join(error_messages) if error_messages else "数据验证失败"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            request.user.delete()
            return Response({"code": 200, "message": "注销成功"})
        except Exception as e:
            return Response(
                {"code": 40005, "message": f"注销账号失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
