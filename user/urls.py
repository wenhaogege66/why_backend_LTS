from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    UserUpdateView,
    PasswordUpdateView,
    UserDeleteView,
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('update/', UserUpdateView.as_view(), name='user-update'),
    path('update/password/', PasswordUpdateView.as_view(), name='user-update-password'),
    path('delete/', UserDeleteView.as_view(), name='user-delete'),
]  