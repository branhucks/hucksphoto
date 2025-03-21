from django.contrib import admin
from .models import Category, Photo, About, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured', 'date_taken', 'created_at')
    list_filter = ('featured', 'categories')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'description', 'location')
    filter_horizontal = ('categories',)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    pass

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass