from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from collections import OrderedDict

from api.models import RecognitionInfo, Employee, EmployeeImage, Camera
from .fusioncharts import FusionCharts


def register(request):
    user = request.user
    if user.is_authenticated:
        return redirect('homepage')
    if request.method=='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'authentication/register.html', {'form':form})

@login_required
def homepage(request):
    # Get all recognition data
    recog_data = RecognitionInfo.objects.all()
    emp_counts = recog_data.values('employee').annotate(count=Count('pk', distinct=True)).order_by()
    top_5_emp_seen_cam_count = recog_data.values('employee').annotate(count=Count('camera', distinct=True)).order_by('-count')[:5]
    total_known = 0
    total_unknown = 0
    total_cam = len(Camera.objects.all())
    total_emp = len(Employee.objects.all())
    emp_recog_group = {}
    for emp in emp_counts:
        if emp['employee'] == None:
            total_unknown = emp['count']
        else:
            total_known = total_known + 1
            emplo = Employee.objects.get(id=int(emp['employee']))
            info_data = RecognitionInfo.objects.filter(employee=emplo)
            emp_recog_group[str(emp['employee'])] = {'employee':emplo, 'data':[], 'time_spend':[], 'total_duration':0}
            last_status = False # Initialize as check out
            for da in info_data:
                if not last_status==da.category:
                    emp_recog_group[str(emp['employee'])]['data'].append({'timestamp':da.timestamp, 'category':da.category})
                    last_status = da.category
            for count in range(0, len(emp_recog_group[str(emp['employee'])]['data']), 2):
                check_in_time = emp_recog_group[str(emp['employee'])]['data'][count]['timestamp']
                try:
                    check_out_time = emp_recog_group[str(emp['employee'])]['data'][count+1]['timestamp']
                    duration = check_out_time - check_in_time
                    emp_recog_group[str(emp['employee'])]['time_spend'].append({'check_in':check_in_time, 'check_out':check_out_time, 'duration':duration.total_seconds()})
                    emp_recog_group[str(emp['employee'])]['total_duration'] = emp_recog_group[str(emp['employee'])]['total_duration'] + duration.total_seconds()
                except IndexError:
                    emp_recog_group[str(emp['employee'])]['time_spend'].append({'check_in':check_in_time, 'check_out':None, 'duration':None})

    
    # Bar Chart
    dataSource = OrderedDict()
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Total Duration spend by Employees in Office"
    chartConfig["xAxisName"] = "Employee Name"
    chartConfig["yAxisName"] = "Total Duration in seconds"
    chartConfig["theme"] = "fusion"
    chartData = OrderedDict()
    for value in emp_recog_group:
        emp_recog_data = emp_recog_group[value]
        chartData[emp_recog_data['employee'].name] = emp_recog_data['total_duration']
    dataSource["chart"] = chartConfig
    dataSource["data"] = []
    for key, value in chartData.items():
        data = {}
        data["label"] = key
        data["value"] = value
        dataSource["data"].append(data)
    column2D = FusionCharts("column2d", "ex1" , "600", "400", "chart-1", "json", dataSource)

    #Pie Chart
    dataSource = OrderedDict()
    chartConfig = OrderedDict()
    chartConfig["caption"] = "Count of Camera where Employees are Seen"
    chartConfig["showValues"] = "1"
    chartConfig["showPercentInTooltip"] = "0"
    chartConfig["enableMultiSlicing"] = "1"
    chartConfig["theme"] = "fusion"
    dataSource["chart"] = chartConfig
    dataSource["data"] = []
    chartData = OrderedDict()
    for emp in top_5_emp_seen_cam_count:
        if emp['employee']==None:
            chartData['Visitor'] = emp['count']
        else:
            employee = Employee.objects.get(id=emp['employee'])
            chartData[employee.name] = emp['count']
    for key, value in chartData.items():
        data = {}
        data['label'] = key
        data['value'] = value
        dataSource['data'].append(data)
    pie3d = FusionCharts("pie3d", "ex2" , "100%", "400", "chart-2", "json", dataSource)

    return render(request, 'authentication/dashboard.html', {'emp_counts':emp_counts, 'top_5_emp_seen_cam_count':top_5_emp_seen_cam_count, 'total_known':total_known, 'total_unknown':total_unknown, 'total_emp':total_emp, 'total_cam':total_cam, 'emp_chart':column2D.render(), 'emp_pie':pie3d.render(), 'emp_recog':emp_recog_group})

# Create your views here.
