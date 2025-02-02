from django.urls import path
from . import views
from .views import LearningSummary

urlpatterns = [
    path('', views.index, name='index'),
    path('summary', LearningSummary.as_view(), name='summary'),
    path('summary/<str:period>', LearningSummary.as_view(), name='summary_api')
]