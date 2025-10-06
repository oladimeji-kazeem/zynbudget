from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'users'

# API Router
router = DefaultRouter()
router.register(r'api/register', views.UserRegistrationView, basename='api_register')
router.register(r'api/logout', views.UserLogoutView, basename='api_logout')
router.register(r'api/profile', views.UserProfileViewSet, basename='api_profile')

urlpatterns = [
    # Template URLs
    path('', views.HomePageView.as_view(), name='home'),
    path('register/', views.UserRegistrationTemplateView.as_view(), name='register_page'),
    path('login/', views.UserLoginTemplateView.as_view(), name='login_page'),
    path('logout/', views.UserLogoutTemplateView.as_view(), name='logout_page'),
    path('profile/', views.UserProfileTemplateView.as_view(), name='profile_page'),
    path('profile/edit/', views.UserProfileEditView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.change_password_view, name='change_password'),
    path('profile/upload-picture/', views.upload_profile_picture_view, name='upload_picture'),
    path('profile/delete-picture/', views.delete_profile_picture_view, name='delete_picture'),
    
    # API URLs
    path('api/login/', views.UserLoginView.as_view(), name='api_login'),
    path('', include(router.urls)),
]