from distutils.command.upload import upload
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
import datetime as dt
from datetime import datetime
# Create your models here.


class UserRegistrationModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    # dp = Ime(blank=True, manual_crop="")
    bio = models.TextField(max_length=500)
    email_confirmed = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15)


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
    image = models.ImageField(upload_to="images/")
    price = models.IntegerField()
    size = models.CharField(choices=SIZES, max_length=6)
    weight = models.IntegerField()
    name = models.CharField(max_length=50)
    availability = models.BooleanField(default=False)
    dateAdded = models.DateField(default=datetime.utcnow)


    def __str__(self):
        return self.name

    @classmethod
    def get_single_product(cls, pk):
        product = cls.objects.get(pk=pk)
        return product

class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    dateAdded = models.DateField(default=datetime.utcnow)
    receipt = models.CharField(max_length=50, null=True)
    amount = models.FloatField()
    phoneNumber = models.CharField(max_length=15)
    checkoutReuestID = models.CharField(max_length=50)
    merchantRequestId = models.CharField(max_length=50)
    status = models.CharField(max_length=50)


    def __str__(self):
        return self.status


class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE, related_name='orders')
    transaction = models.ForeignKey(Transactions, on_delete=models.CASCADE, related_name='orders')
    isPaid = models.BooleanField(default=False)
    isDelivered = models.BooleanField(default=False)

    def __str__(self):
        return self.status
