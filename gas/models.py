from django.db import models
from django.contrib.auth.models import User
import datetime as dt
from pyuploadcare.dj.models import ImageField
from tinymce.models import HTMLField
from datetime import datetime
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    dp = ImageField(blank=True, manual_crop="")
    bio = HTMLField(max_length=500)
    email_confirmed = models.BooleanField(default=False)


    def save_profile(self):
        self.save()

    def delete_profile(self):
        self.delete()

    def __str__(self):
        return self.user.username


class Catalogue(models.Model):
    SIZES = [
        ("LARGE", 'Large'),
        ("MEDIUM", 'Medium'),
        ("SMALL", 'Small')
    ]
    image = ImageField(blank=True, manual_crop="")
    price = models.IntegerField()
    size = models.CharField(choices=SIZES, max_length=6)
    weight = models.IntegerField()
    name = models.CharField(max_length=50)
    availability = models.BooleanField(default=False)
    dateAdded = models.DateField(default=datetime.utcnow)


    def __str__(self):
        return self.name
