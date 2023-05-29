from django.urls import path
from . import views


urlpatterns = [
    path("", views.index), 
    path("process_form", views.process_form, name='process_form'),
    path('task_status/', views.task_status, name='task_status'),
    path('response/', views.view_response, name='response'),
    path('about/', views.about, name = "about"),
    path('response/error', views.error, name="error"),
    path('response/generate-pdf/', views.generate_pdf, name='generate_pdf')
]