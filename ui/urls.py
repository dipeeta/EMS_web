from django.urls import path, include
from .views import add_employee, list_employee, add_emp_image, camera, toggle_camera_status, train, view_employee_recog_detail

urlpatterns = [
    path('employee/add', add_employee, name='add_employee'),
    path('employee/list', list_employee, name='list_employee'),
    path('employee/<employee_id>', add_emp_image, name='employee_image'),
    path('employee/train/<employee_id>', train, name='train'),
    path('employee/status/<employee_id>', view_employee_recog_detail, name='employee_recog_detail'),
    path('camera', camera, name='camera'),
    path('camera/<camera_id>', toggle_camera_status, name='toggle_status'),
]
