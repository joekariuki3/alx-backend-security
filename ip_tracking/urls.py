from django.urls import path
from .views import home, my_login, my_logout, profile

urlpatterns = [
    path('', home, name='home'),
    path('login/', my_login, name='login'),
    path('logout/', my_logout, name='logout'),
    path('profile/', profile, name='profile'),
]