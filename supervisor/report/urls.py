from django.urls import path
from report import views

urlpatterns = [
    path('', views.index, name='index'),
]
