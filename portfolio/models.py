from django.db import models
from django.utils.text import slugify

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
    categories = models.ManyToManyField(Category, related_name='photos')
    date_taken = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    simulation = models.CharField(max_length=200, blank=True)
    camera = models.CharField(max_length=200, default="Fuji X-T50")
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
                
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
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    def __str__(self):
        return "Contact Information"