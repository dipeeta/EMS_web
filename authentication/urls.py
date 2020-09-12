from django.urls import path, include
from .views import register, homepage

urlpatterns = [
    path('user/register/', register, name='register'),
    path('', homepage, name='homepage'),
]
