from django.contrib import admin

from .models import Employee, EmployeeImage, Camera, RecognitionInfo

# Register your models here.
admin.site.register(Employee)
admin.site.register(EmployeeImage)
admin.site.register(Camera)
admin.site.register(RecognitionInfo)