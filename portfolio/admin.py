from django.contrib import admin
from .models import Category, Photo, About, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured', 'date_taken', 'created_at', 'simulation', 'camera')
    list_filter = ('featured', 'categories', 'simulation', 'camera')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'location', 'simulation', 'camera')
    filter_horizontal = ('categories',)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    pass

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass