from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileViewSet,
    UserLogoutView
)

router = DefaultRouter()
router.register(r'register', UserRegistrationView, basename='register')
router.register(r'logout', UserLogoutView, basename='logout')
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('', include(router.urls)),
]