from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('contact', views.contact, name="contact"),
    path('about', views.about, name="about"),
    path('thank-you', views.thank_you, name="thank_you"),
    path('clear', views.clear, name="clear"),
    path('faq', views.faq, name="faq"),
    path('track-order', views.track_order, name="track"),
    path('track-status', views.track_results, name="track-status"),
]