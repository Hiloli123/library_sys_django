from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Book(models.Model):

    """
    This class is created a model schema for database.
    It have details with their character limit, requiired or optional field or 
    option choices which needed as per the column.

    All inputs are database column.

    created_at, updated_at, is_deleted_at is by default created by self.
    """
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('non-fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('history', 'History'),
        ('biography', 'Biography'),
        ('other','other'),
    ]
     
    title = models.CharField(max_length=200,unique=True)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='fiction')
    publication_year = models.PositiveSmallIntegerField(validators=[
            MinValueValidator(1000), # Minimum 4-digit number
            MaxValueValidator(2026)  # Maximum 4-digit number
        ],
        help_text="Enter a 4-digit year (e.g., 2026)")
    isbn = models.CharField(max_length=13, unique=True)
    is_available = models.BooleanField(default=True)
    description = models.CharField(max_length=400,null=True,blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)