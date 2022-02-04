from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pyuploadcare.dj.forms import ImageField
from .models import Catalogue, Profile

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ['first_name', 'last_name','username', 'email', 'password1', 'password2']

class CatalogueForm(forms.ModelForm):
    image = ImageField()
    class Meta:
        model = Catalogue
        exclude = ["dateAdded"]
        fields = ['image','price','size','weight','name', 'availability']

class ProfileForm(forms.ModelForm):
    firstName = forms.CharField(max_length=30)
    lastName = forms.CharField(max_length=30)
    email = forms.CharField(max_length=30)

    class Meta:
        model = Profile