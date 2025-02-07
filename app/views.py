from django.shortcuts import render, redirect
from .models import User, Timer, Category, Study_log, Goal
from .forms import LoginForm, SignupForm, AccountChangeForm
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView ,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login,  update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required


User = get_user_model()

def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

# サインアップ
# 処理後は'home'に遷移
class Signup(CreateView):
    form_class = SignupForm
    template_name = 'app/signup.html'
    success_url = reverse_lazy('home')

    # サインアップ後にログイン状態を保持
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, form.save())
        return response
    
    
# ログイン
class Login(LoginView):
    form_class = LoginForm
    template_name = 'app/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.GET.get('next', '/home/')
        return redirect(next_url)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'app/home.html'


# アカウント更新   
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = AccountChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)

            user.save()
            update_session_auth_hash(request, user)

            messages.success(request, "アカウント情報を更新しました。")
            return redirect('account')
    else:
        form = AccountChangeForm(instance=request.user)
        # GET時は初期化して表示
    
    return render(request, "app/update_profile.html", {"form":form})


        




