from django.shortcuts import render
from .models import User, Timer, Category, Study_log, Goal
from .forms import LoginForm
from django.contrib.auth.views import LoginView
from django.views import generic


def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

class Login(LoginView):
    form_class = LoginForm
    template_name = 'app/login.html'
