from django.urls import path,include
from . import views



urlpatterns = [

    path('',views.classify_query),
           path('upload-db/', views.upload_db, name='upload_db'),
    path('get-table-data/', views.get_table_data, name='get_table_data'),


   
]