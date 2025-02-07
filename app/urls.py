from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('account/', views.update_profile, name='account'),
]   