from django.shortcuts import render
from .models import User, Timer, Category, Study_log, Goal

def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

def home(request):
    return render(request, 'app/home.html')

def setting(request):
    return render(request, 'app/setting.html')