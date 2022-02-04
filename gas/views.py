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
    return render(request, "profile.html", {})

def search_results(request):
    if 'size' in request.GET or request.GET['size']:
        search_item = request.GET.get('size')
        searched_items = Catalogue.objects.filter(size=search_item)
        print(searched_items)
        message = f"{search_item}"
        return render(request, 'search.html',{"message":message,
            "searched_items": searched_items})
    else:
        message = "You haven't searched for any item"
        return render(request, 'search.html', {"message":message})