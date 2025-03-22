# portfolio/forms.py
from django import forms
from captcha.fields import CaptchaField

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-300 focus:ring-2 focus:ring-photo-accent focus:border-photo-accent rounded-md shadow-sm'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'w-full p-3 border border-gray-300 focus:ring-2 focus:ring-photo-accent focus:border-photo-accent rounded-md shadow-sm'})
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'w-full p-3 border border-gray-300 focus:ring-2 focus:ring-photo-accent focus:border-photo-accent rounded-md shadow-sm'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'class': 'w-full p-3 border border-gray-300 focus:ring-2 focus:ring-photo-accent focus:border-photo-accent rounded-md shadow-sm'})
    )
    captcha = CaptchaField(
        help_text='Please enter the characters you see in the image above.'
    )