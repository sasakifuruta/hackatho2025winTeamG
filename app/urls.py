from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
]