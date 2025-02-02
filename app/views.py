from datetime import datetime, timedelta
from collections import defaultdict
from pprint import pprint
import json
import calendar

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models.functions import TruncDate
from .models import User, Timer, Category, Study_log, Goal


def index(request):
    categories = Category.objects.all() 
    return render(request, 'app/index.html' , {'categories': categories})

# TODO:クラスにする
def learning_summary2(request):
    """_グラフデータの取得_
    Args:
        request (_type_): _description_
    Returns:
        _dict_: 
        - 週間日別 week_logs = 
                    {week_range:
                    [日付, 曜日, インプット時間, アウトプット時間]
                    total: １週間の学習時間
                    }
        - 月間週別 month_logs = 
                    {month:
                    [週番号, インプット時間, アウトプット時間]
                    total: １ヶ月の学習時間
                    }
        - 年間月別 year_logs = 
                    {year:
                    [月, インプット時間, アウトプット時間]
                    total: １年間の学習時間
                    }
    """
    logs = Study_log.objects.all()
    # 日付一覧を取得
    dates = logs.annotate(
        date = TruncDate('start_time')
        ).values_list('date', flat=True).distinct()
    # 日ごとの学習時間
    day_logs = {}
    # 週ごとの学習時間
    week_logs = {}
    # 月ごとの学習時間
    month_logs = {}
    for date in dates:
        # 日ごとのアウトプット時間
        day_outputs = logs.filter(start_time__date=date, category__is_output=True)
        day_output_total = sum(log.studied_time for log in day_outputs)
        # 日ごとのインプット時間
        day_inputs = logs.filter(start_time__date=date, category__is_output=False)
        day_input_total = sum(log.studied_time for log in day_inputs)
        # 日毎のアウトプット,インプット
        day_logs[date] = [day_input_total, day_output_total]
        
        # 週ごとのアウトプット時間
        week_outputs = logs.filter(start_time__week=date.isocalendar().week, category__is_output=True)
        week_output_total = sum(log.studied_time for log in week_outputs)
        # 週ごとのインプット時間
        week_inputs = logs.filter(start_time__week=date.isocalendar().week, category__is_output=False)
        week_input_total = sum(log.studied_time for log in week_inputs)
        year_month = date.strftime('%Y/%m')
        week_num = date.isocalendar().week
        # 週毎のアウトプット,インプット
        week_logs[f'{year_month}の{week_num}週目'] = [year_month, week_num, week_input_total, week_output_total]
        
        # 月ごとのアウトプット時間
        month_outputs = logs.filter(start_time__month=date.month, category__is_output=True)
        month_output_total = sum(log.studied_time for log in month_outputs)
        # 月ごとのインプット時間
        month_inputs = logs.filter(start_time__month=date.month, category__is_output=False)
        month_input_total = sum(log.studied_time for log in month_inputs)
        # 月毎のアウトプット,インプット
        month_logs[year_month] = [date.year, date.month, month_input_total, month_output_total]
    pprint(f'日毎{day_logs}')
    pprint(f'週毎{week_logs}')
    pprint(f'月毎{month_logs}')
        
    # TODO:メソッド化する
    # 日ごとの学習時間を週ごとにグループ化
    week_data = {}
    for date in day_logs:
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        week_range = f"{week_start.strftime('%Y/%m/%d')}-{week_end.strftime('%m/%d')}"

        # 週別日別
        week_data.setdefault(week_range, {'days':[], 'total':0})
        week_data[week_range]['days'].append([
            date.strftime('%Y/%m/%d'),
            conv_day_of_week(date),
            day_input_total,
            day_output_total
            ])
        week_data[week_range]['total'] += day_input_total+ day_output_total
        
    pprint(f'週間日別{week_data}')
    week_chart = conv_data(week_data, 'week')
    pprint(f'週間日別こんぶ{week_chart}')
        
    # 週ごとの学習時間を月ごとにグループ化
    month_data = {}
    for week in week_logs.values():
        month = week[0]
        week_num = week[1]
        week_input_total = week[2]
        week_output_total = week[3]
        
        # 月間週別
        month_data.setdefault(month,{"weeks":[], "total":0})
        month_data[month]["weeks"].append([
            week_num, 
            week_input_total,
            week_output_total
            ])
        month_data[month]["total"] += week_input_total + week_output_total
    pprint(f'月間週別{month_data}')
    month_chart = conv_data(month_data, 'month')
    pprint(f'月間週別こんぶ{month_chart}')
    
    # 月ごとの学習時間を年ごとにグループ化
    year_data = {}
    for month_item in month_logs.values():
        year = month_item[0]
        month = month_item[1]
        
        # 年間月別
        year_data.setdefault(year,{"months":[], "total":0})
        year_data[year]['months'].append([
            month,
            month_input_total,
            month_output_total
            ])
        year_data[year]["total"] += month_input_total + month_output_total
    pprint(f'年間月別{year_data}')
    year_chart = conv_data(year_data, 'year')
    pprint(f'年間月別こんぶ{year_chart}')

    return render(request, 'app/summary.html' ,
                {
                'week_chart': json.dumps(week_chart), 
                'month_chart': json.dumps(month_chart),
                'year_chart': json.dumps(year_chart)
                })


# 曜日を日本語に変換
def conv_day_of_week(date):
    ja_week = ['月','火','水','木','金','土','日']
    week_num = date.isocalendar().weekday
    day = ja_week[week_num-1]
    return day


# グラフ用にデータを整形
def conv_data(dates, view_type):
    chart_data = []
    if view_type == 'week':
        labels = ['月','火','水','木','金','土','日']
        for week_range, value in dates.items():
            input_data = [0 for _ in range(7)]
            output_data = [0 for _ in range(7)]
            for key, days in value.items():
                if key == 'total':
                    continue
                for day in days:
                    # day = [日付, 曜日, インプット時間, アウトプット時間]
                    for i, label in enumerate(labels):
                        if day[1] == label:
                            input_data[i] = day[2]
                            output_data[i] = day[3]
                chart_data.append({
                    'week': week_range, 
                    'input_data': input_data,
                    'output_data': output_data,
                    'total': value['total'] // 60,
                    })
    elif view_type == 'month':
        for year_month, value in dates.items():
            year, month = map(int, year_month.split('/'))
            # 月の週数
            weeks = len(calendar.monthcalendar(year, month))
            input_data = [0 for _ in range(weeks)]
            output_data = [0 for _ in range(weeks)]
            for week in value['weeks']:
                i = week[0]-1 # 週番号
                input_data[i] = week[1]
                output_data[i] = week[2]
            chart_data.append({
                'month': year_month,
                'input_data': input_data,
                'output_data': output_data,
                'total': value['total'] // 60
                })
    elif view_type == 'year':
        # todo:目標テーブルから開始月と終了月を取得　もしくは　記録の最初の月を取得
        start_month_from_goal = Goal.objects.first()
        start_month_from_log = Study_log.objects.order_by('created_at').first()
        if start_month_from_goal:
            start_month = start_month_from_goal.start_month
        elif start_month_from_log:
            start_month = start_month_from_log.start_time.month
        else:
            start_month = datetime.now().month
    
        for year, value in dates.items():            
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
            pprint(f'年昆布input_data{input_data}')
            pprint(f'年昆布output_data{output_data}')
            chart_data.append({
                'year': year,
                'input_data': input_data,
                'output_data': output_data,
                'total': value['total'] // 60
                })
    context = {
            'chart_data': chart_data
        }
    return context


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
        pprint(period)
        return self.get_chart(period)
        
        
    
    # ボタンを押した時の処理
    def get_chart(self, period):
        if period == 'week':
            logs_all, days = self.get_days()
            day_logs = self.get_day_logs(logs_all, days)
            week_data = self.get_weekly_data(days, day_logs)
            chart, chart_ratio, labels= self.conv_week_data(week_data)
        elif period == 'month':
            logs_all, days = self.get_days()
            week_logs = self.get_week_logs(logs_all, days)
            month_data = self.get_monthly_data(week_logs)
            chart, chart_ratio = self.conv_month_data(month_data)
            pprint(f'クラス内の週別{week_logs}')
            pprint(f'クラス内の月間{month_data}')
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
                conv_day_of_week(day),
                day_logs[day][0], # インプット
                day_logs[day][1] # アウトプット
                ])
            week_data[week_range]['total'] += day_logs[day][0] + day_logs[day][1]
        return week_data
    
    
    # 曜日を日本語に変換
    def conv_day_of_week(date):
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
    
    
    def conv_week_data(self, week_data):
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
                    'total': value['total'] // 60,
                    })
                chart_ratio.append({
                    'week': week_range,
                    'input_ratio': sum(input_data) * 100 / value['total'],
                    'output_ratio': sum(output_data) * 100 / value['total']
                    })
        return chart_data, chart_ratio, labels
    
    
    def conv_month_data(self, month_data):
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
                'total': value['total'] // 60
                })
            chart_ratio.append({
                'month': year_month,
                'input_ratio': sum(input_data) * 100 / value['total'],
                'output_ratio': sum(output_data) * 100 / value['total']
                })
        return chart_data, chart_ratio
    
    