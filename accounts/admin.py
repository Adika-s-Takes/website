from django.contrib import admin
from .models import ShippingInfo, Country, City


admin.site.register(ShippingInfo)
admin.site.register(Country)
admin.site.register(City)

# Register your models here.
