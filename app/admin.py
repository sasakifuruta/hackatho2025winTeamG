from django.contrib import admin
from .models import User, Timer, Category, Study_log, Goal

admin.site.register(User)
admin.site.register(Timer)
admin.site.register(Category)
admin.site.register(Study_log)
admin.site.register(Goal)
