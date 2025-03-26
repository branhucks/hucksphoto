from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Photo(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='photos/')
    image_thumbnail = models.ImageField(upload_to='photos/thumbnails/', blank=True, null=True)
    image_webp = models.ImageField(upload_to='photos/webp/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='photos')
    date_taken = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    simulation = models.CharField(max_length=200, blank=True)
    camera = models.CharField(max_length=200, default="Fuji X-T50")
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Create slug if not exists
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Process and create optimized images
        if self.image:
            # Create WebP version
            webp_image = self._create_webp_version()
            
            # Create thumbnail
            thumbnail = self._create_thumbnail()
            
            # Save processed images
            if webp_image:
                self.image_webp = webp_image
            if thumbnail:
                self.image_thumbnail = thumbnail
        
        super().save(*args, **kwargs)
    
    def _create_webp_version(self):
        """Convert image to WebP format"""
        if not self.image:
            return None
        
        try:
            # Open image 
            img = Image.open(self.image)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize for web
            img.thumbnail((1920, 1920), Image.LANCZOS)
            
            # Prepare WebP version
            output = BytesIO()
            img.save(output, format='WEBP', quality=70)
            output.seek(0)
            
            # Create InMemoryUploadedFile
            return InMemoryUploadedFile(
                output, 
                'ImageField', 
                f"{self.image.name.split('.')[0]}.webp", 
                'image/webp',
                sys.getsizeof(output), 
                None
            )
        except Exception as e:
            print(f"WebP conversion error: {e}")
            return None
    
    def _create_thumbnail(self):
        """Create a smaller thumbnail version of the image"""
        if not self.image:
            return None
        
        try:
            # Open image
            img = Image.open(self.image)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail((300, 300), Image.LANCZOS)
            
            # Prepare thumbnail
            output = BytesIO()
            img.save(output, format='JPEG', quality=60)
            output.seek(0)
            
            # Create InMemoryUploadedFile
            return InMemoryUploadedFile(
                output, 
                'ImageField', 
                f"{self.image.name.split('.')[0]}_thumb.jpg", 
                'image/jpeg',
                sys.getsizeof(output), 
                None
            )
        except Exception as e:
            print(f"Thumbnail creation error: {e}")
            return None
    
    def __str__(self):
        return self.title

class About(models.Model):
    profile_image = models.ImageField(upload_to='about/', blank=True)
    bio = models.TextField()
    
    def __str__(self):
        return "About Page"
    
    class Meta:
        verbose_name_plural = "About"

class Contact(models.Model):
    email = models.EmailField()
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    
    def __str__(self):
        return "Contact Information"