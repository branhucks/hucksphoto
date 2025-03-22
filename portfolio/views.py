from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Photo, Category, About, Contact
from .forms import ContactForm

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
        queryset = Photo.objects.all().order_by('?')
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