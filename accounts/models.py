from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()
    

class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.name
    
class City(models.Model):
    name = models.CharField(max_length=300)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.country.name} | {self.name}"
    
    
class ShippingInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=300)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    house_number = models.CharField(max_length=300)
    street_name = models.CharField(max_length=300)

    def __str__(self):
        return self.user.username


  

# Create your models here.
