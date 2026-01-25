# models.py - Example Models for DjCrudX

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Status(models.Model):
    """Status model with color support for ColoredSelectDropdownWidget"""
    name = models.CharField(max_length=50)
    bg_color = models.CharField(max_length=7, default="#e5e7eb")  # Hex color for background
    txt_color = models.CharField(max_length=7, default="#374151")  # Hex color for text
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Statuses"


class Category(models.Model):
    """Hierarchical category model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Tag(models.Model):
    """Simple tag model for many-to-many relationships"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#3b82f6")
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Main product model demonstrating all widget types"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Foreign key relationships
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    
    # Many-to-many relationships
    tags = models.ManyToManyField(Tag, blank=True)
    assigned_users = models.ManyToManyField(User, blank=True)
    
    # Boolean field
    is_active = models.BooleanField(default=True)
    
    # DateTime fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']