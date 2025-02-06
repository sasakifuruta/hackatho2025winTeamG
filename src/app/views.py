from django.shortcuts import render
from .models import User, Timer, Category, Study_log, Goal

def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})
