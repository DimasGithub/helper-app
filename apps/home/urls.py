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
]