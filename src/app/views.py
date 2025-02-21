from pprint import pprint
import json
from datetime import datetime, timedelta, date
import calendar
import logging


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login,  update_session_auth_hash
from django.views.generic import CreateView ,TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.db.models.functions import TruncDate
from django.db.models import Sum


from .models import User, Timer, Category, Study_log, Goal
from .forms import LoginForm, SignupForm, AccountChangeForm

logger = logging.getLogger(__name__) #エラーログの確認

User = get_user_model()

def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

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

# ===============
# ホーム画面
# ===============

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'app/home.html'

    # ホーム画面に遷移した時にインプットかアウトプットに応じて、小カテゴリー一覧を取得して表示
    # **kwargsは辞書型の可変長変数。
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        input_categories = Category.objects.filter(is_output=False, user=self.request.user)
        context["input_categories"] = input_categories
        
        # 今日の日付を追加
        context["today"] = date.today()

        return context
    


# 勉強時間データの取得,ログイン時のみ
@login_required 
def get_study_time(request):
    user = request.user
    try:
        timer = Timer.objects.get(user=user)
        return JsonResponse({'study':timer.study})
    except Timer.DoesNotExist:
        return JsonResponse({'study':25})

# 休憩時間データの取得,ログイン時のみ
@login_required 
def get_rest_time(request):
    user = request.user
    try:
        timer = Timer.objects.get(user=user)
        return JsonResponse({'rest':timer.rest})
    except Timer.DoesNotExist:
        return JsonResponse({'rest':5})

# 累積勉強時間を追加
@csrf_exempt
def store_elapsed_time(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            elapsed = data.get("elapsed", 0)  # 経過時間（分）
            category_id = data.get("category_id")  # カテゴリID
            
            if not category_id:
                return JsonResponse({"error": "カテゴリIDが必要です"}, status=400)

            category = Category.objects.get(id=category_id)

            # Study_logに新しい記録を追加
            now = timezone.now()
            study_log = Study_log.objects.create(
                category=category,
                studied_time=int(elapsed),
                start_time=now - timezone.timedelta(minutes=elapsed),
                end_time=now
            )

            return JsonResponse({"message": "記録が保存されました", "studied_time": study_log.studied_time})
        except Category.DoesNotExist:
            return JsonResponse({"error": "カテゴリが見つかりません"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "POSTリクエストのみ対応しています"}, status=405)

# 累積勉強時間を取得
@login_required
def get_timer_data(request):
    user = request.user
    categories = Category.objects.filter(user=user)

    timer_data = {"input": {}, "output": {}}

    for category in categories:
        total_time = Study_log.objects.filter(category=category).aggregate(Sum('studied_time'))["studied_time__sum"] or 0
        mode = "output" if category.is_output else "input"
        timer_data[mode][category.category] = total_time  # カテゴリごとの累積時間を格納

    return JsonResponse({"timerData": timer_data})

# カテゴリーを取得する
def get_categories(request):
    mode = request.GET.get("mode", "input")  # デフォルトは "input"
    user = request.user 
    
    if mode == "output":# "input" の場合 False, "output" の場合 True
        is_output = True
    else:
        is_output = False 
    
    categories = Category.objects.filter(is_output=is_output, user = user)  # ユーザーのカテゴリを取得
    
    category_list = [{"id": cat.id, "name": cat.category} for cat in categories]

    return JsonResponse({"categories": category_list})

# グラフを更新
def update_chart(request):
    user = request.user
    categories = Category.objects.filter(user=user)

    timer_data = {"input": {}, "output": {}}

    for category in categories:
        total_time = Study_log.objects.filter(category=category).aggregate(Sum('studied_time'))["studied_time__sum"] or 0
        mode = "output" if category.is_output else "input"
        timer_data[mode][category.category] = total_time  # カテゴリごとの累積時間を格納
    
    data = {
    "input": sum(timer_data["input"].values()),
    "output": sum(timer_data["output"].values())
    }
    return JsonResponse(data)

# ===============
# 設定画面
# ===============

class SettingView(LoginRequiredMixin, TemplateView):
    template_name = 'app/setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        input_categories = Category.objects.filter(is_output=False, user=self.request.user)
        output_categories = Category.objects.filter(is_output=True, user=self.request.user)
        context["input_categories"] = input_categories
        context["output_categories"] = output_categories

        context["test"] = date.today()

        return context

@csrf_exempt
@login_required
def add_category(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category_name = data.get("category")
            is_output = data.get("is_output", False)  # デフォルトは input (False)

            if not category_name:
                return JsonResponse({"success": False, "message": "カテゴリー名が空です。"}, status=400)

            Category.objects.create(user=request.user, category=category_name, is_output=is_output)
            return JsonResponse({"success": True, "message": "カテゴリーが追加されました！"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "リクエストが不正です。"}, status=400)
        except Exception as e:
           return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "POSTリクエストのみ受け付けています。"}, status=405)

@csrf_exempt
@login_required
def save_work_time(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            study_time = data.get("study")
            user = request.user

            if study_time is None:
                return JsonResponse({"success": False, "message": "勉強時間が指定されていません。"}, status=400)
            
            # ユーザーのTimerデータを取得または作成
            if not Timer.objects.filter(user=user).exists():
                Timer.objects.create(user=user,study = study_time)
                message = "勉強時間の設定が変更されました！"
            else:
                Timer.objects.filter(user=user).update(study = study_time,updated_at=timezone.now())
                message = "勉強時間の設定が作成されました！"

            return JsonResponse({"success": True, "message": message})
        
        except Exception as e:
           return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "POSTリクエストのみ受け付けています。"}, status=405)

@csrf_exempt
@login_required
def save_rest_time(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            rest_time = data.get("rest")
            user = request.user

            if rest_time is None:
                return JsonResponse({"success": False, "message": "休憩時間が指定されていません。"}, status=400)
            
            # ユーザーのTimerデータを取得または作成
            if not Timer.objects.filter(user=user).exists():
                Timer.objects.create(user=user,rest = rest_time)
                message = "休憩時間の設定が変更されました！"
            else:
                Timer.objects.filter(user=user).update(rest = rest_time,updated_at=timezone.now())
                message = "休憩時間の設定が作成されました！"

            return JsonResponse({"success": True, "message": message})
        
        except Exception as e:
           return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "POSTリクエストのみ受け付けています。"}, status=405)

# カテゴリー削除処理
@login_required
@csrf_exempt
def delete_category(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category_id = data.get("id")

            # カテゴリーを取得
            category = get_object_or_404(Category, id=category_id, user=request.user)

            # そのカテゴリーの is_output を取得（True なら Output、False なら Input）
            category_is_output = category.is_output

            # 同じ is_output のカテゴリー数を取得
            category_count = Category.objects.filter(user=request.user, is_output=category_is_output).count()

            # もしカテゴリーが1つしかなければ削除を禁止
            if category_count <= 1:
                return JsonResponse({"success": False, "error": "カテゴリーは最低1つ必要です。"})

            # カテゴリーを削除
            category.delete()
            return JsonResponse({"success": True})

        except Exception as e:
            logger.error(f"Category delete error: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})
