from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer
)

User = get_user_model()


class UserRegistrationView(viewsets.GenericViewSet):
    """
    User registration endpoint
    POST /api/users/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Register a new user"""
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
    """
    User login endpoint
    POST /api/users/login/
    Body: {"username": "user", "password": "pass"} or {"email": "user@email.com", "password": "pass"}
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Allow login with either username or email
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
            
            # Update last login IP
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
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    User profile management endpoints
    GET /api/users/profile/ - Get current user profile
    PUT /api/users/profile/ - Update current user profile
    PATCH /api/users/profile/ - Partial update current user profile
    POST /api/users/profile/change_password/ - Change password
    POST /api/users/profile/upload_picture/ - Upload profile picture
    DELETE /api/users/profile/delete_picture/ - Delete profile picture
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'post', 'delete']
    
    def get_queryset(self):
        """Return only the current user"""
        return User.objects.filter(id=self.request.user.id)
    
    def get_object(self):
        """Return the current user"""
        return self.request.user
    
    def list(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user profile"""
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
        """Change user password"""
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': ['Wrong password']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            # Update token
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                'message': 'Password changed successfully',
                'token': token.key
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_picture(self, request):
        """Upload profile picture"""
        user = request.user
        
        if 'profile_picture' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete old picture if exists
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
        """Delete profile picture"""
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
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        user = request.user
        
        stats = {
            'username': user.username,
            'email': user.email,
            'member_since': user.created_at,
            'is_premium': user.is_premium_active,
            'premium_expires': user.premium_expires_at,
            'email_verified': user.is_email_verified,
            'profile_complete': self.calculate_profile_completion(user)
        }
        
        return Response(stats)
    
    def calculate_profile_completion(self, user):
        """Calculate profile completion percentage"""
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


class UserLogoutView(viewsets.GenericViewSet):
    """
    User logout endpoint
    POST /api/users/logout/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout user by deleting token"""
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logout successful'
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)