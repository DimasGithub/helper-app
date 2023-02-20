# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='home'),
    path('data/', views.DataView.as_view(), name='data'),
    path('nip/register', views.register_nip, name='register_nip'),
    path('nip/user-data', views.DataUserView.as_view(), name='user_data'),
    path('nip/user-data/<str:id>', views.DataUserDetailView.as_view(), name='user_data_details'),
    path('nip/user-data/<int:id>/delete', views.deleted_report_daily, name='report_delete'),
    path('nip/user-data/<int:id>/delete-all', views.deleted_all_report_daily, name='report_delete_all')
]