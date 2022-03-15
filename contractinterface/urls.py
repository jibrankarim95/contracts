from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('annual', views.annual, name='annual'),
    path('monthly', views.monthly, name='monthly'),
    path('weekly', views.weekly, name='weekly'),
    path('combine', views.combine, name='combine'),

    path('xml_result', views.xml_result, name='xml_result'),
    path('json_result', views.json_result, name='json_result'),
    path('xml_result_monthly', views.xml_result_monthly, name='xml_result_monthly'),
    path('combine_files', views.combine_files, name='combine_files'),


]
