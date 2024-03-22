from django.urls import path
from . import views

urlpatterns = [
    path('shop', views.shop, name="shop"),
    path('item/<str:pk>', views.item_details, name="item_details"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path("review/<str:pk>", views.review, name="review"),
]