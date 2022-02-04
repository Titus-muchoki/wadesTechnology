from django.shortcuts import render,redirect
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Profile, Catalogue


# Create your views here.


def index(request):
    # Query all items
    items = Catalogue.objects.all()
    return render(request, "index.html", {"items":items})

def signup(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, email=email, password=raw_password)
            profile = Profile(user=user)
            profile.save()
            user.is_active = True
            login(request,user)
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def profile(request):
    return render(request, "profile.html",{})