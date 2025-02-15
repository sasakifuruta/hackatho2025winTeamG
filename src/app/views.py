from pprint import pprint
import json
from datetime import datetime, timedelta
import calendar


from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView #,TemplateView
from django.views import View
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login,  update_session_auth_hash
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models.functions import TruncDate


from .models import User, Timer, Category, Study_log, Goal
from .forms import LoginForm, SignupForm, AccountChangeForm




User = get_user_model()

def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

def setting(request):
    return render(request, 'app/setting.html')


# サインアップ
class Signup(CreateView):
    form_class = SignupForm
    template_name = 'app/signup.html'
    success_url = reverse_lazy('login')

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
        next_url = self.request.GET.get('next')
        if not next_url:
            next_url = '/home/'
        return redirect(next_url)

# class HomeView(LoginRequiredMixin, TemplateView):
#     template_name = 'app/home.html'

# TODO: 競合！！
def home(request):
    return render(request, 'app/home.html')


# アカウント更新   
@login_required
def update_profile(request):
    if request.method == 'POST':
        form = AccountChangeForm(request.POST, instance=request.user)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # パスワード変更後もログイン状態維持
            messages.success(request, "アカウント情報を更新しました。")
            return redirect('account')
        else:
            # フォーム全体のエラーメッセージ
            messages.error(request, "入力内容にエラーがあります。修正してください。")
            
    else:
        form = AccountChangeForm(instance=request.user)
    
    return render(request, "app/update_profile.html", {
        "form": form,
        "messages": messages.get_messages(request)
    })


        
# ===============
# グラフ画面
# ===============
class LearningSummary(View):
    def get(self, request, period=None):
        if period == None:
            # グラフ画面アクセス時は週間グラフを表示
            logs_all, days = self.get_days()
            day_logs = self.get_day_logs(logs_all, days)
            week_data = self.get_weekly_data(days, day_logs)
            week_chart, week_chart_ratio,labels = self.conv_week_data(week_data)
            # pprint(f'クラス内の週間日別{week_chart}')
            # pprint(f'クラス内の週間日別比率{week_chart_ratio}')
            # pprint(f'クラス内の週間ラベル{labels}')
            
            return render(request, 'app/summary.html',
                    {
                    'week_chart': json.dumps(week_chart),
                    'week_chart_ratio': json.dumps(week_chart_ratio),
                    'week_labels':json.dumps(labels)
                    })
        # ボタンを押した時
        return self.get_chart(period)
        
        
    
    # ボタンを押した時の処理
    def get_chart(self, period):
        logs_all, days = self.get_days()
        if period == 'week':
            day_logs = self.get_day_logs(logs_all, days)
            week_data = self.get_weekly_data(days, day_logs)
            chart, chart_ratio, labels= self.conv_week_data(week_data) # labelsはAPI取得時は使わない
        elif period == 'month':
            week_logs = self.get_week_logs(logs_all, days)
            month_data = self.get_monthly_data(week_logs)
            chart, chart_ratio = self.conv_month_data(month_data)
        elif period == 'year':
            month_logs = self.get_month_logs(logs_all, days)
            year_data = self.get_year_data(month_logs)
            chart, chart_ratio = self.conv_year_data(year_data)
            pprint(f'クラス内の月{month_logs}')
            pprint(f'クラス内の年間{year_data}')
            pprint(f'クラス内のchart{chart}')
            pprint(f'クラス内のchart_ratio{chart_ratio}')
        else:
            return JsonResponse({"error": "periodが無効です"}, status=400)
        
        return JsonResponse({
                            'chart': json.dumps(chart),
                            'chart_ratio': json.dumps(chart_ratio),
                            }
                            )
    
    
    def get_days(self):
        # 日付一覧を取得
        logs_all = Study_log.objects.all()
        days = logs_all.annotate(
                day = TruncDate('start_time')
                ).values_list('day', flat=True).distinct()
        return logs_all, days

    
    def get_day_logs(self, logs_all, days):
        # 日別データを取得
        day_logs = {}
        for day in days:
            outputs = logs_all.filter(start_time__date=day, category__is_output=True)
            output_total = sum(log.studied_time for log in outputs)
            inputs = logs_all.filter(start_time__date=day, category__is_output=False)
            input_total = sum(log.studied_time for log in inputs)
            day_logs[day] = [input_total, output_total]
        return day_logs
    
    
    def get_week_logs(self, logs_all, days):
        # 週別データを取得
        week_logs = {}
        for day in days:
            outputs = logs_all.filter(start_time__week=day.isocalendar().week, category__is_output=True)
            output_total = sum(log.studied_time for log in outputs)
            inputs = logs_all.filter(start_time__week=day.isocalendar().week, category__is_output=False)
            input_total = sum(log.studied_time for log in inputs)
            
            year_month = day.strftime('%Y/%m')
            week_num = day.isocalendar().week
            week_logs[f'{year_month}の{week_num}週目'] = [year_month, week_num, input_total, output_total]
        return week_logs


    def get_month_logs(self, logs_all, days):
        # 月別データを取得
        month_logs = {}
        for day in days:
            outputs = logs_all.filter(start_time__month=day.month, category__is_output=True)
            output_total = sum(log.studied_time for log in outputs)
            inputs = logs_all.filter(start_time__month=day.month, category__is_output=False)
            input_total = sum(log.studied_time for log in inputs)
            
            year_month = day.strftime('%Y/%m')
            month_logs[year_month] =[day.year, day.month, input_total, output_total]
        return month_logs
            

    def get_weekly_data(self, days, day_logs):
        # 週ごと日別データを取得
        week_data = {}
        for day in days:
            week_start = day - timedelta(days=day.weekday())
            week_end = week_start + timedelta(days=6)
            week_range = f"{week_start.strftime('%Y/%m/%d')}-{week_end.strftime('%m/%d')}"
            week_data.setdefault(week_range, {'days':[], 'total':0})
            week_data[week_range]['days'].append([
                day.strftime('%Y/%m/%d'),
                self.conv_day_of_week(day),
                day_logs[day][0], # インプット
                day_logs[day][1] # アウトプット
                ])
            week_data[week_range]['total'] += day_logs[day][0] + day_logs[day][1]
        return week_data

    
    # 曜日を日本語に変換
    def conv_day_of_week(self,date):
        ja_week = ['月','火','水','木','金','土','日']
        week_num = date.isocalendar().weekday
        day = ja_week[week_num-1]
        return day
    
    
    def get_monthly_data(self, week_logs):
        # 月ごと週別データを取得
        month_data = {}
        for week in week_logs.values():
            month = week[0]
            week_num = week[1]
            week_input_total = week[2]
            week_output_total = week[3]
            month_data.setdefault(month,{"weeks":[], "total":0})
            month_data[month]["weeks"].append([
                week_num, 
                week_input_total,
                week_output_total
                ])
            month_data[month]["total"] += week_input_total + week_output_total
        return month_data
    
    
    def get_year_data(self, month_logs):
        # 月ごと週別データを取得
        year_data = {}
        for month_item in month_logs.values():
            year = month_item[0]
            month = month_item[1]
            month_input_total = month_item[2]
            month_output_total = month_item[3]
            
            year_data.setdefault(year,{"months":[], "total":0})
            year_data[year]['months'].append([
                month, month_input_total,
                month_output_total
                ])
            year_data[year]["total"] += month_input_total + month_output_total
        pprint(f'年間月別{year_data}')
        return year_data
    
    
    def conv_week_data(self, week_data):
        # 週間日別データの整形
        labels = ['月','火','水','木','金','土','日']
        chart_data = []
        chart_ratio = []
        for week_range, value in week_data.items():
            input_data = [0 for _ in range(7)]
            output_data = [0 for _ in range(7)]
            for key, days in value.items():
                if key == 'total':
                    continue
                for day in days:
                    for i, label in enumerate(labels):
                        if day[1] == label:
                            input_data[i] = day[2]
                            output_data[i] = day[3]
                chart_data.append({
                    'period': week_range, 
                    'input_data': input_data,
                    'output_data': output_data,
                    'total': round(value['total'] / 60, 1),
                    })
                chart_ratio.append({
                    'week': week_range,
                    'input_ratio': sum(input_data) * 100 / value['total'],
                    'output_ratio': sum(output_data) * 100 / value['total']
                    })
        return chart_data, chart_ratio, labels
    
    
    def conv_month_data(self, month_data):
        # 月間週別データの整形
        chart_data = []
        chart_ratio = []
        for year_month, value in month_data.items():
            year, month = map(int, year_month.split('/'))
            weeks = len(calendar.monthcalendar(year, month))
            input_data = [0 for _ in range(weeks)]
            output_data = [0 for _ in range(weeks)]
            for week in value['weeks']:
                i = week[0]-1
                input_data[i] = week[1]
                output_data[i] = week[2]
            chart_data.append({
                'period': year_month,
                'input_data': input_data,
                'output_data': output_data,
                # TODO: 小数点第一位まで
                'total': round(value['total'] / 60, 1) 
                })
            chart_ratio.append({
                'month': year_month,
                'input_ratio': sum(input_data) * 100 / value['total'],
                'output_ratio': sum(output_data) * 100 / value['total']
                })
        return chart_data, chart_ratio
    
    
    def conv_year_data(self, year_data):
        # 年間月別データの整形
        chart_data = []
        chart_ratio = []
        start_month = self.get_start_month()
    
        for year, value in year_data.items():
            input_data = [0 for _ in range(12)]
            output_data = [0 for _ in range(12)]
            for month in value['months']:
                # month = [月, インプット時間, アウトプット時間]
                if month[0] == start_month:
                    input_data[0] = month[1]
                    output_data[0] = month[2]
                elif month[0] > start_month:
                    input_data[month[0]-start_month] = month[1]
                    output_data[month[0]-start_month] = month[2]
                else:
                    input_data[month[0]+12-start_month] = month[1]
                    output_data[month[0]+12-start_month] = month[2]
                chart_data.append({
                'period': year,
                'input_data': input_data,
                'output_data': output_data,
                'total': round(value['total'] / 60, 1),
                })
                chart_ratio.append({
                'year': year,
                'input_ratio': sum(input_data) * 100 / value['total'],
                'output_ratio': sum(output_data) * 100 / value['total']
                })
        return chart_data, chart_ratio


    def get_start_month(self):
        # 開始月を取得
        start_month_from_goal = Goal.objects.first()
        start_month_from_log = Study_log.objects.order_by('created_at').first()
        if start_month_from_goal:
            # 目標テーブルにあれば
            start_month = start_month_from_goal.start_month
        elif start_month_from_log:
            # 学習ログテーブルから一番最初に記録した月を取得
            start_month = start_month_from_log.start_time.month
        else:
            # 閲覧している月を取得
            start_month = datetime.now().month
        return start_month



