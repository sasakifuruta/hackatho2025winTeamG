from django.shortcuts import render, redirect
from .models import User, Timer, Category, Study_log, Goal
from .forms import LoginForm, SignupForm
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login


def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

class Signup(CreateView):
    form_class = SignupForm
    template_name = 'app/signup.html'
    success_url = '/home/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, form.save())
        return response

class Login(LoginView):
    form_class = LoginForm
    template_name = 'app/login.html'
<<<<<<< HEAD:src/app/views.py
=======

    def form_invalid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.GET.get('next', '/home/')
        return redirect(next_url)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'app/home.html'

class Logout(LogoutView):
    next_page = '/login/'

>>>>>>> 44d9386 (signup,login,logoutのバックエンド処理完了、レンダリング確認):app/views.py
