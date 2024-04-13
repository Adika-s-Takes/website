from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name="login"),
    path('register', views.register, name="register"),
    path('add/shipping', views.shipping, name="shipping"),
    path('shipping', views.shipping_detail, name="shipping_detail"),
    path('delete/shipping', views.delete_shipping, name="delete_shipping"),
    path('account-details', views.account, name="account"),
    path('account-info', views.account_info, name="account_info"),
    path('my-orders', views.my_orders, name="my_orders"),
    path('get_cities_by_country/<str:country_id>', views.get_cities_by_country, name="get_cities_by_country"),
]