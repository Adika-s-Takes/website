from django.db import models
from django.contrib.auth.models import User
import uuid


# Models for the product page

LEAGUE = (
    ("PREMIER LEAGUE", "PREMIER LEAGUE"),
    ("SPANISH LEAGUE", "SPANISH LEAGUE"),
    ("SAUDI LEAGUE", "SAUDI LEAGUE"),
    ("GERMAN LEAGUE", "GERMAN LEAGUE"),
    ("FRENCH LEAGUE", "FRENCH LEAGUE"),
    ("MLS", "MLS"),
    ("ITALIAN LEAGUE", "ITALIAN LEAGUE"),
    ("INTERNATIONAL", "INTERNATIONAL"),
)

PRODUCT_TYPE = (
    ("JERSEY", "JERSEY"),
    ("BOOTS", "BOOTS"),
    ("EQUIPMENT", "EQUIPMENT"),
    ("POLO", "POLO"),
    ("BABY KIT", "BABY KIT"),
)

KIT_TYPE = (
    ("HOME", "Home Kit"),
    ("AWAY", "Away Kit"),
    ("THIRD", "Third Kit"),
    ("FOURTH", "Fourth Kit"),
)

VERSION = (
    ("RETRO", "RETRO"),
    ("MODERN", "MODERN"),
)

SEASON = (
    ("2023/2024", "2023/2024"),
    ("2022/2023", "2022/2023"),
    ("2021/2022", "2021/2022"),
    ("1980/1981", "1980/1981"),
    ("1990/1991", "1990/1991"),
    ("1991/1992", "1991/1992"),
    ("1992/1993", "1992/1993"),
    ("1993/1994", "1993/1994"),
    ("1994/1995", "1994/1995"),
    ("1995/1996", "1995/1996"),
    ("1996/1997", "1996/1997"),
    ("1997/1998", "1997/1998"),
    ("1998/1999", "1998/1999"),
    ("1999/2000", "1999/2000"),
    ("2000/2001", "2000/2001"),
)

class ProductTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    tag = models.CharField(max_length=300)

    def __str__(self):
        return self.tag


class Size(models.Model):
    size = models.CharField(max_length=300)

    def __str__(self):
        return self.size

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=300)
    price = models.IntegerField(default=0)
    initial_price = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    customizable = models.BooleanField(default=False, null=True)
    description = models.TextField()
    featured_image = models.FileField(upload_to="products/featured/images")
    version = models.CharField(max_length=300, choices=VERSION, null=True, blank=True)
    league = models.CharField(max_length=300, choices=LEAGUE, null=True, blank=True)
    type = models.CharField(max_length=300, choices=PRODUCT_TYPE)
    kit_type = models.CharField(max_length=300, choices=KIT_TYPE, blank=True)
    season = models.CharField(max_length=300, choices=SEASON, blank=True)
    stock = models.IntegerField(default=0)
    product_tags = models.ManyToManyField(ProductTag, max_length=300)
    sizes = models.ManyToManyField(Size, max_length=300)
    custom_item_link = models.URLField(null=True)


    def __str__(self):
        return self.name

    @staticmethod
    def get_products_by_id(ids):
        return Item.objects.filter (id__in=ids)

class ProductReview(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=5, null=True)
    review = models.TextField()

    def __str__(self):
        return f"{self.reviewer.username}"

STATUS = (
    ("ORDER PLACED", "ORDER PLACED"),
    ("SHIPPED", "SHIPPED"),
    ("DELIVERED", "DELIVERED"),
    ("PENDING", "PENDING")
)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    ref = models.CharField(max_length=300, null=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    number = models.CharField(max_length=300, null=True, blank=True)
    status = models.CharField(max_length=300, choices=STATUS, null=True, default="PENDING")
    paid = models.BooleanField(default=False)
    flutterwave_ref = models.CharField(max_length=300, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=300, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    price = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=0, null=True)
    shipping_info = models.ForeignKey('accounts.ShippingInfo', on_delete=models.SET_NULL, null=True)
    size = models.CharField(max_length=300, null=True)


    def __str__(self):
        return self.item.name

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    product = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    image = models.FileField(upload_to="products/images")


    def __str__(self):
        return self.product.name

class ProductDetail(models.Model):
    product = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    detail = models.CharField(max_length=300)


class ProductReview(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=5, null=True)
    review = models.TextField(null=True)

    def __str__(self):
        return f"{self.reviewer.username}"



# Create your models here.
