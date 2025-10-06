from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.db import transaction
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer
)
from .forms import (
    UserRegistrationForm,
    UserProfileForm,
    UserLoginForm,
    ChangePasswordForm,
    ProfilePictureForm
)

User = get_user_model()


# ============================================
# API VIEWS (Keep existing API views)
# ============================================

class UserRegistrationView(viewsets.GenericViewSet):
    """API: User registration endpoint"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ObtainAuthToken):
    """API: User login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = None
        if email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        elif username:
            user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            ip_address = self.get_client_ip(request)
            user.last_login_ip = ip_address
            user.save(update_fields=['last_login_ip', 'last_login'])
            
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user': UserSerializer(user).data
            })
        
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileViewSet(viewsets.ModelViewSet):
    """API: User profile management"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'delete']
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        return self.request.user
    
    def list(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = UserProfileSerializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'user': UserSerializer(instance).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': ['Wrong password']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.data.get('new_password'))
            user.save()
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            return Response({
                'message': 'Password changed successfully',
                'token': token.key
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_picture(self, request):
        user = request.user
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.profile_picture:
            user.profile_picture.delete()
        user.profile_picture = request.FILES['profile_picture']
        user.save()
        return Response({
            'message': 'Profile picture uploaded successfully',
            'profile_picture': request.build_absolute_uri(user.profile_picture.url)
        })
    
    @action(detail=False, methods=['delete'])
    def delete_picture(self, request):
        user = request.user
        if user.profile_picture:
            user.profile_picture.delete()
            user.profile_picture = None
            user.save()
            return Response({'message': 'Profile picture deleted successfully'})
        return Response(
            {'error': 'No profile picture to delete'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutView(viewsets.GenericViewSet):
    """API: User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'message': 'Logout successful'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# DJANGO TEMPLATE VIEWS
# ============================================

class HomePageView(TemplateView):
    """Home page view"""
    template_name = 'users/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Welcome to ZynBudget'
        return context


class UserRegistrationTemplateView(CreateView):
    """Template: User registration view"""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login_page')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('users:profile_page')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class UserLoginTemplateView(LoginView):
    """Template: User login view"""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('users:profile_page')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        
        # Update last login IP
        ip_address = self.get_client_ip()
        self.request.user.last_login_ip = ip_address
        self.request.user.save(update_fields=['last_login_ip'])
        
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutTemplateView(LogoutView):
    """Template: User logout view"""
    next_page = reverse_lazy('users:home')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


class UserProfileTemplateView(LoginRequiredMixin, TemplateView):
    """Template: User profile view"""
    template_name = 'users/profile.html'
    login_url = reverse_lazy('users:login_page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user'] = user
        context['title'] = 'My Profile'
        context['profile_completion'] = self.calculate_profile_completion(user)
        
        return context
    
    def calculate_profile_completion(self, user):
        fields = [
            user.first_name,
            user.last_name,
            user.email,
            user.phone_number,
            user.profile_picture,
            user.date_of_birth,
            user.bio,
        ]
        filled_fields = sum(1 for field in fields if field)
        total_fields = len(fields)
        return round((filled_fields / total_fields) * 100, 2)


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    """Template: Edit user profile"""
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile_page')
    login_url = reverse_lazy('users:login_page')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profile updated successfully!')
        return response
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


@login_required(login_url='users:login_page')
def change_password_view(request):
    """Template: Change password view"""
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:profile_page')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm(request.user)
    
    return render(request, 'users/change_password.html', {
        'form': form,
        'title': 'Change Password'
    })


@login_required(login_url='users:login_page')
def upload_profile_picture_view(request):
    """Template: Upload profile picture"""
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Delete old picture if exists
            if request.user.profile_picture:
                request.user.profile_picture.delete()
            
            form.save()
            messages.success(request, 'Profile picture updated successfully!')
            return redirect('users:profile_page')
        else:
            messages.error(request, 'Please upload a valid image file.')
    else:
        form = ProfilePictureForm(instance=request.user)
    
    return render(request, 'users/upload_picture.html', {
        'form': form,
        'title': 'Upload Profile Picture'
    })


@login_required(login_url='users:login_page')
def delete_profile_picture_view(request):
    """Template: Delete profile picture"""
    if request.method == 'POST':
        user = request.user
        if user.profile_picture:
            user.profile_picture.delete()
            user.profile_picture = None
            user.save()
            messages.success(request, 'Profile picture deleted successfully!')
        else:
            messages.warning(request, 'No profile picture to delete.')
        return redirect('users:profile_page')
    
    return render(request, 'users/delete_picture_confirm.html', {
        'title': 'Delete Profile Picture'
    })