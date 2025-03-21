# portfolio/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from .models import Photo, Category, About, Contact

class HomeView(ListView):
    model = Photo
    template_name = 'portfolio/home.html'
    context_object_name = 'photos'
    
    def get_queryset(self):
        return Photo.objects.filter(featured=True)[:9]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class GalleryView(ListView):
    model = Photo
    template_name = 'portfolio/gallery.html'
    context_object_name = 'photos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Photo.objects.all().order_by('-date_taken')
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
            
        return context

class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'portfolio/photo_detail.html'
    slug_url_kwarg = 'photo_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get next and previous photos
        current_photo = self.get_object()
        
        try:
            next_photo = Photo.objects.filter(
                date_taken__gte=current_photo.date_taken
            ).exclude(id=current_photo.id).order_by('date_taken', 'id').first()
        except Photo.DoesNotExist:
            next_photo = None
            
        try:
            previous_photo = Photo.objects.filter(
                date_taken__lte=current_photo.date_taken
            ).exclude(id=current_photo.id).order_by('-date_taken', '-id').first()
        except Photo.DoesNotExist:
            previous_photo = None
            
        context['next_photo'] = next_photo
        context['previous_photo'] = previous_photo
        
        return context

class AboutView(TemplateView):
    template_name = 'portfolio/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['about'] = About.objects.first()
        return context

class ContactView(TemplateView):
    template_name = 'portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contact'] = Contact.objects.first()
        return context