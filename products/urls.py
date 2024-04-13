from django.urls import path
from . import views

urlpatterns = [
    path('shop', views.shop, name="shop"),
    path('item/<str:pk>', views.item_details, name="item_details"),
    path('cart', views.cart, name="cart"),
    path('checkout', views.checkout, name="checkout"),
    path("review/<str:pk>", views.review, name="review"),
    path('search', views.item_search_results, name="search"),
    path('wishlist', views.wishlist, name="wishlist"),
    path('wishlist/add/<str:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]