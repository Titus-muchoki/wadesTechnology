from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Catalogue, Profile


class UserRegistration(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password'] != cd['password2']:
                raise forms.ValidationError('Passwords don\'t match.')
            return cd['password2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class CatalogueForm(forms.ModelForm):    
    class Meta:
        model = Catalogue
        exclude = ["dateAdded"]
        fields = ['image','price','size','weight','name', 'availability']

class ProfileForm(forms.ModelForm):
    firstName = forms.CharField(max_length=30)
    lastName = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30)

    class Meta:
        # dp = ImageField()
        model = Profile
        fields = ['firstName', 'lastName', 'email', 'bio']
