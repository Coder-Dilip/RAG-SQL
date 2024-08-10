from django.urls import path,include
from . import views



urlpatterns = [

           path('', views.upload_db, name='upload_db'),
    path('get-table-data/', views.get_table_data, name='get_table_data'),
    path('get-table-overview/', views.get_table_overview, name='get_table_overview'),


   
]