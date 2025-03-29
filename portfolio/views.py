from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from .models import Photo, Category, About, Contact
from .forms import ContactForm
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import random

class HomeView(ListView):
    model = Photo
    template_name = 'portfolio/home.html'
    context_object_name = 'photos'
    
    def get_queryset(self):
        # Optimize query with select_related and better prefetch
        return Photo.objects.filter(featured=True).select_related().prefetch_related('categories')[:9]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['categories'] = Category.objects.only('name', 'description', 'slug')
        
        return context

class GalleryView(ListView):
    model = Photo
    template_name = 'portfolio/gallery.html'
    context_object_name = 'photos'
    paginate_by = 24
    
    def get_queryset(self):
        # Start with optimized base queryset
        queryset = Photo.objects.all().only(
            'id', 'title', 'slug', 'location', 'image', 'image_thumbnail', 'image_webp'
        )
        
        # Apply category filter if specified
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(location__icontains=search_query)
            )
        
        # Apply sorting with optimized queries
        sort_by = self.request.GET.get('sort', 'random')
        
        if sort_by == 'date_asc':
            queryset = queryset.order_by('date_taken', 'id')
        elif sort_by == 'date_desc':
            queryset = queryset.order_by('-date_taken', '-id')
        elif sort_by == 'random':
            # Create a consistent session key for this specific gallery view
            filter_key = f"{category_slug or 'all'}_{search_query}"
            session_key = f"random_seed_{filter_key}"
            
            # Check if we need a new random seed
            new_seed_requested = self.request.GET.get('new_seed') == '1'
            if new_seed_requested or session_key not in self.request.session:
                # Generate a new random seed and store it in the session
                self.request.session[session_key] = random.randint(1, 1000000)
                
            # Use the consistent seed for random ordering
            random.seed(self.request.session[session_key])
            
            # Convert queryset to list and shuffle with our seeded random
            photo_list = list(queryset)
            random.shuffle(photo_list)
            
            # Return the shuffled list directly - Django's Paginator can handle lists
            return photo_list
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Optimize category query
        context['categories'] = Category.objects.only('id', 'name', 'slug')
        
        # Pass the search query to the template for form persistence
        context['search_query'] = self.request.GET.get('search', '')
        
        # Pass the current sort option to the template
        context['sort_by'] = self.request.GET.get('sort', 'random')
        
        # Category filtering with optimized query
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(
                Category.objects.only('id', 'name', 'description', 'slug'),
                slug=category_slug
            )
            
        return context

@require_GET
def load_more_photos(request):
    page = request.GET.get('page', 1)
    category_slug = request.GET.get('category', None)
    sort_by = request.GET.get('sort', 'random')
    search_query = request.GET.get('search', '')
    
    # Start with base queryset
    queryset = Photo.objects.all().only(
        'id', 'title', 'slug', 'location', 'image', 'image_thumbnail', 'image_webp'
    )
    
    # Apply filters similar to GalleryView
    if category_slug:
        queryset = queryset.filter(categories__slug=category_slug)
    
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | 
            Q(location__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by == 'date_asc':
        queryset = queryset.order_by('date_taken', 'id')
    elif sort_by == 'date_desc':
        queryset = queryset.order_by('-date_taken', '-id')
    elif sort_by == 'random':
        filter_key = f"{category_slug or 'all'}_{search_query}"
        session_key = f"random_seed_{filter_key}"
        
        if session_key in request.session:
            # Use the same seed as the main gallery view
            random.seed(request.session[session_key])
            
            # Convert to list and shuffle with the same seed
            photo_list = list(queryset)
            random.shuffle(photo_list)
            queryset = photo_list
        else:
            # Fallback to database random if no seed (shouldn't happen normally)
            queryset = queryset.order_by('?')
    
    # Set up pagination
    paginator = Paginator(queryset, 24)
    photos = paginator.get_page(page)
    
    # Format data for JSON response
    data = []
    for photo in photos:
        # Handle both model instances and dictionaries (when using shuffled list)
        if isinstance(photo, dict):
            photo_data = {
                'id': photo['id'],
                'title': photo['title'],
                'slug': photo['slug'],
                'location': photo['location'],
                'image_url': photo['image'].url,
                'thumbnail_url': photo['image_thumbnail'].url if photo['image_thumbnail'] else '',
                'webp_url': photo['image_webp'].url if photo['image_webp'] else '',
                'detail_url': f"/photo/{photo['slug']}/"
            }
        else:
            photo_data = {
                'id': photo.id,
                'title': photo.title,
                'slug': photo.slug,
                'location': photo.location,
                'image_url': photo.image.url,
                'thumbnail_url': photo.image_thumbnail.url if photo.image_thumbnail else '',
                'webp_url': photo.image_webp.url if photo.image_webp else '',
                'detail_url': f"/photo/{photo.slug}/"
            }
        data.append(photo_data)
    
    return JsonResponse({
        'photos': data,
        'has_next': photos.has_next(),
        'next_page': photos.next_page_number() if photos.has_next() else None
    })

class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'portfolio/photo_detail.html'
    slug_url_kwarg = 'photo_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get current photo
        current_photo = self.get_object()
        
        # Get category filter if viewing from a specific category
        category_slug = self.kwargs.get('category_slug')
        queryset = Photo.objects.all()
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)
        elif current_photo.categories.exists():
            # If no category specified in URL but photo has categories,
            # use the first category for navigation context
            first_category = current_photo.categories.first()
            queryset = queryset.filter(categories=first_category)
        
        # Order by date_taken and then by id to handle same-date photos
        ordered_photos = queryset.order_by('date_taken', 'id')
        
        # Find the index of the current photo
        photo_ids = list(ordered_photos.values_list('id', flat=True))
        
        try:
            current_index = photo_ids.index(current_photo.id)
            
            # Get next photo (circular - go to first if at end)
            next_index = (current_index + 1) % len(photo_ids)
            next_photo = Photo.objects.get(id=photo_ids[next_index])
            
            # Get previous photo (circular - go to last if at beginning)
            prev_index = (current_index - 1) % len(photo_ids)
            previous_photo = Photo.objects.get(id=photo_ids[prev_index])
            
        except (ValueError, IndexError):
            # Fallback in case of any errors
            next_photo = None
            previous_photo = None
        
        context['next_photo'] = next_photo
        context['previous_photo'] = previous_photo
        
        # Pass the category for context and link building in template
        if category_slug:
            context['current_category'] = get_object_or_404(Category, slug=category_slug)
        
        # Add preload URLs for next and previous images to enable instant loading
        if next_photo:
            context['next_photo_url'] = next_photo.image.url
        if previous_photo:
            context['previous_photo_url'] = previous_photo.image.url
        
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
        context['form'] = ContactForm()
        return context
        
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Get the contact information
            contact = Contact.objects.first()
            recipient_email = contact.email
            
            try:
                # Format the email message
                email_message = f"Name: {name}\nEmail: {email}\n\n{message}"
                
                # Send the email
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                
                # Add success message
                messages.success(request, "Your message has been sent successfully!")
                return redirect('portfolio:contact')
                
            except Exception as e:
                # Add more detailed error message that includes the exception
                error_message = f"Error: {str(e)}"
                print(error_message)  # This will appear in your console/logs
                messages.error(request, "There was an error sending your message. Please try again later.")
        else:
            # If form is invalid, return the form with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        # Return the form with errors
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)