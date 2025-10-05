from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    instead of username for authentication.
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model for ZynBudget application
    Extends Django's AbstractUser with additional fields
    """
    
    # Override email to make it unique and required
    email = models.EmailField(
        unique=True,
        verbose_name='Email Address',
        help_text='Required. Enter a valid email address.'
    )
    
    # Additional profile fields
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Phone Number'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        verbose_name='Profile Picture'
    )
    
    # User preferences
    currency = models.CharField(
        max_length=3,
        default='USD',
        verbose_name='Preferred Currency',
        help_text='ISO 4217 currency code (e.g., USD, EUR, GBP)'
    )
    
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        verbose_name='Timezone',
        help_text='User preferred timezone'
    )
    
    # Account settings
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verified'
    )
    
    is_premium = models.BooleanField(
        default=False,
        verbose_name='Premium Account'
    )
    
    premium_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Premium Expiration Date'
    )
    
    # Additional information
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date of Birth'
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='Bio'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date Joined'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Updated'
    )
    
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Last Login IP'
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() or self.username
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username
    
    @property
    def is_premium_active(self):
        """Check if user has active premium subscription"""
        if not self.is_premium:
            return False
        if self.premium_expires_at is None:
            return True
        from django.utils import timezone
        return self.premium_expires_at > timezone.now()