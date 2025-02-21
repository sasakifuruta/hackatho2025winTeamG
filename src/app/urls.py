from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import LearningSummary

urlpatterns = [
    path('', views.index, name='index'),
    path('setting/', views.SettingView.as_view(), name='setting'),
    path('setting/api/add_category/', views.add_category, name='add_category'),
    path('setting/api/delete_category/', views.delete_category, name='delete_category'),
    path('setting/api/save_work_time/', views.save_work_time, name='save_work_time'),
    path('setting/api/save_rest_time/', views.save_rest_time, name='save_rest_time'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', views.HomeView.as_view(), name='home'),
    path('home/api/get_study_time/', views.get_study_time, name='get_study_time'),
    path('home/api/get_rest_time/', views.get_rest_time, name='get_rest_time'),
    path('home/api/store_elapsed_time/', views.store_elapsed_time, name='store_elapsed_time'),
    path('home/api/get_timer_data/', views.get_timer_data, name='get_timer_data'),
    path('home/api/get_categories/', views.get_categories, name='get_categories'),
    path('home/api/update_chart/', views.update_chart, name='update_chart'),
    path('signup/', views.Signup.as_view(), name='signup'),
    path('account/', views.update_profile, name='account'),
    path('summary', LearningSummary.as_view(), name='summary'),
    path('summary/<str:period>', LearningSummary.as_view(), name='summary_api')
]   
