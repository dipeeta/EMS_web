import json

from celery import shared_task
from api_server.celery import app

from api.models import EmployeeImage, Employee, Camera


@shared_task
def train_publish(emp_id=0):
    if emp_id=='0' or emp_id==0:
        images = EmployeeImage.objects.filter(train_status=False)
    else:
        employee = Employee.objects.get(id=emp_id)
        images = EmployeeImage.objects.filter(employee=employee).filter(train_status=False)
    message = {'data':[], 'type':'train'}
    for image in images:
        message['data'].append({'image':str(image.image), 'employee':image.employee.id})
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            json.dumps(message),
            exchange='ems_train_exchange',
            routing_key='train',
        )

@shared_task
def cam_status_publish(cam_id, status, cam_url, cam_category):
    message = {'data':{'camera_id':cam_id, 'status':status, 'camera_url':cam_url, 'camera_category':cam_category}, 'type':'camera'}
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            json.dumps(message),
            exchange='ems_train_exchange',
            routing_key='train',
        )