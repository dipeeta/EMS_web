from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import EmployeeForm, EmployeeImageForm, CameraForm
from api.models import Employee, EmployeeImage, Camera, RecognitionInfo
from .tasks import train_publish, cam_status_publish

# Create your views here.
@login_required
def add_employee(request):
    if request.method=='POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_employee')
    else:
        form = EmployeeForm()
    return render(request, 'ui/add_employee.html', {'form':form})


@login_required
def list_employee(request):
    emps = Employee.objects.all()
    return render(request, 'ui/list_employee.html', {'employees':emps})


@login_required
def add_emp_image(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    images = EmployeeImage.objects.filter(employee=employee)
    train = False
    for image in images:
        if not image.train_status:
            train = True
            break
    if request.method=='POST':
        form = EmployeeImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_data = form.save(commit=False)
            image_data.employee = employee
            image_data.save()
    else:
        form = EmployeeImageForm()
    return render(request, 'ui/add_emp_image.html', {'form':form, 'images':images, 'train':train, 'employee':employee})


@login_required
def camera(request):
    cameras = Camera.objects.all()
    if request.method=='POST':
        form = CameraForm(request.POST)
        if form.is_valid():
            form.save()
            form = CameraForm()
    else:
        form = CameraForm()
    return render(request, 'ui/camera.html', {'form':form, 'cameras':cameras})


@login_required
def toggle_camera_status(request, camera_id):
    camera = Camera.objects.get(id=camera_id)
    if camera.status:
        camera.status = False
    else:
        camera.status = True
    camera.save()
    cam_status_publish(camera.id, camera.status, camera.url, camera.category)
    return redirect('camera')


@login_required
def train(request, employee_id):
    train_publish(employee_id)
    return redirect('list_employee')


@login_required
def view_employee_recog_detail(request, employee_id):
    emp = Employee.objects.get(id=employee_id)
    try:
        image = EmployeeImage.objects.filter(employee=emp)[0]
    except IndexError:
        image = None
    info_data = RecognitionInfo.objects.filter(employee=emp)
    emp_recog_group = {}
    emp_recog_group[str(employee_id)] = {'employee':emp, 'data':[], 'time_spend':[], 'total_duration':0}
    last_status = False # Initialize as check out
    for da in info_data:
        if not last_status==da.category:
            emp_recog_group[str(employee_id)]['data'].append({'timestamp':da.timestamp, 'category':da.category})
            last_status = da.category
    for count in range(0, len(emp_recog_group[str(employee_id)]['data']), 2):
        check_in_time = emp_recog_group[str(employee_id)]['data'][count]['timestamp']
        try:
            check_out_time = emp_recog_group[str(employee_id)]['data'][count+1]['timestamp']
            duration = check_out_time - check_in_time
            emp_recog_group[str(employee_id)]['time_spend'].append({'check_in':check_in_time, 'check_out':check_out_time, 'duration':duration.total_seconds()})
            emp_recog_group[str(employee_id)]['total_duration'] = emp_recog_group[str(employee_id)]['total_duration'] + duration.total_seconds()
        except IndexError:
            emp_recog_group[str(employee_id)]['time_spend'].append({'check_in':check_in_time, 'check_out':None, 'duration':None})
    return render(request, 'ui/emp_recog_info.html', {'image':image, 'emp_recog':emp_recog_group})