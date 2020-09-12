from django.forms import ModelForm
from api.models import Employee, EmployeeImage, Camera

class EmployeeForm(ModelForm):
    class Meta:
        model = Employee
        fields = ['emp_id', 'name', 'email', 'address']


class EmployeeImageForm(ModelForm):
    class Meta:
        model = EmployeeImage
        fields = ['image']
        exclude = ('train_status', 'employee')


class CameraForm(ModelForm):
    class Meta:
        model = Camera
        fields = ['name', 'url', 'category']
        exclude = ('status',)