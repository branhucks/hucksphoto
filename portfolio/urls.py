from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    path('gallery/category/<slug:category_slug>/', views.GalleryView.as_view(), name='category_gallery'),
    path('photo/<slug:photo_slug>/', views.PhotoDetailView.as_view(), name='photo_detail'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('gallery/<slug:category_slug>/<slug:photo_slug>/', views.PhotoDetailView.as_view(), name='category_photo_detail'),
    path('load-more-photos/', views.load_more_photos, name='load_more_photos'),
]