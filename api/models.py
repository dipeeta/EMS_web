from django.db import models

# Create your models here.
def emp_image_upload(instance, file):
    return '{}/{}'.format(instance.employee.id, file)

def recog_image_upload(instance, file):
    return 'recog/{}/{}/{}'.format(instance.camera.id, instance.employee.id, file)

class Employee(models.Model):
    name = models.CharField(max_length=200)
    emp_id = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return str(self.id)


class EmployeeImage(models.Model):
    image = models.ImageField(upload_to=emp_image_upload, max_length=300)
    train_status = models.BooleanField(default=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return self.employee.emp_id


class Camera(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=1000)
    status = models.BooleanField(default=False) # True = on and False = off
    category = models.BooleanField(default=True) # True = check in and False = check out

    def __str__(self):
        return str(self.id)


class RecognitionInfo(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField()
    category = models.BooleanField(default=True) # True means in and False means out
    # face_image = models.ImageField(upload_to=recog_image_upload, max_length=300)

    def __str__(self):
        return str(self.id)