from django.urls import path
from . import views

urlpatterns = [
    path('', views.seao_login, name='seao_login'),
    path('seao_home', views.seao_home, name='seao_home'),
    path('seao_logout', views.seao_logout, name = 'seao_logout'),
    path('upload',views.upload_login,name='upload_login'),
    path('seao_upload',views.seao_upload,name='seao_upload'),
    path('seao_upload_data',views.seao_upload_data,name='seao_upload_data'),
    path('seao_download',views.seao_download,name='seao_download'),
    path('annual', views.annual, name='annual'),
    path('monthly', views.monthly, name='monthly'),
    path('weekly', views.weekly, name='weekly'),
    path('xml_result', views.xml_result, name='xml_result'),
    path('json_result', views.json_result, name='json_result'),
    path('xml_result_monthly', views.xml_result_monthly, name='xml_result_monthly'),
    path('seao_data_result', views.seao_data_result, name='seao_data_result')

]