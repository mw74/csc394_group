from django.urls import path
from . import views


urlpatterns = [
    path("", views.index), 
    path("process_form", views.process_form, name='process_form'),
    path('task_status/', views.task_status, name='task_status'),
]