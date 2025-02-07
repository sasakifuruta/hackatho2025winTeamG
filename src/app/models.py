from django.conf import settings
from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
    
class Timer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    study = models.IntegerField(default=25)
    rest = models.IntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.study} 分"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=255)
    is_output = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.category
    

class Study_log(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    studied_time = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
    def time_log(self):
        self.studied_time = self.end_time - self.start_time
        self.save()

    def __str__(self):
        return f"{self.studied_time} "


class Goal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    goal = models.TextField(null=True, blank=True)
    target_time = models.IntegerField()
    output_ratio = models.IntegerField(null=True)
    start_month = models.DateField(null=True, default=timezone.now)
    end_month = models.DateField(null=True, default=timezone.now() + relativedelta(years=1))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.goal