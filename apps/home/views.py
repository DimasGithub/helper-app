# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import time
import json
import random

from django import template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views import View

from .models import Nip, UploadFile
from core.uploader import EkinerjaException, ListDailyReport, DeleteReportDaily, DeleteAllData

from apps.home.tasks import upload_file, delete_all_file


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
class DataView(LoginRequiredMixin,View):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    context = {'segment': 'upload-data'}
    html_template = loader.get_template('home/upload-data.html')

    def get(self, request):
        return HttpResponse(self.html_template.render(self.context, request))

    def post(self, request):
        context = {'segment': 'upload-data'}
        html_template = loader.get_template('home/upload-data.html')
        try:
            nip = request.POST['nip']
            data_nip = Nip.objects.get(nip=nip)
            if data_nip:
                file = request.FILES['upload_data']
                if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or not file.name.endswith('.xlsx'):
                    messages.warning(request, "File must be an .xls file.")
                    return redirect(reverse('dashboard:data'))
                length = 10
                rand_string = ""
                for i in range(length):
                    rand_num = random.randint(0, 9)
                    rand_string += str(rand_num)
                fs = FileSystemStorage(base_url=os.path.join(settings.IMAGE_UPLOAD_URL,f"{time.strftime('%Y/%m/%d/')}"), location=os.path.join(settings.IMAGE_UPLOAD, f"{time.strftime('%Y/%m/%d/')}"))
                file_save = fs.save(f"{rand_string}.xlsx", file)
                file_url = fs.url(file_save)
                obj = UploadFile.objects.create(title=file.name, file_upload=file_save, file_path=file_url, nip=data_nip)
                obj.save()
                file_pk = obj.id
                if data_nip and obj:
                    upload_file.apply_async(args=(nip, file_pk), countdown=3)
                    messages.success(request, f"Upload data successfull.")
                return redirect(reverse('dashboard:home'))
        except Nip.DoesNotExist:
            messages.warning(request, f"NIP `{nip}` not registered.")
        except EkinerjaException as err:
            messages.warning(request, f"{err.message} Please contact admin.")
        except Exception as err:
            messages.warning(request, f"{err}. Please contact admin.")
        
        return redirect(reverse('dashboard:data'))

class DataUserView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    context = {'segment': 'user-data'}
    html_template = 'home/user-data.html'
    def get(self, request): 
        return render(request, self.html_template, context=self.context)
    def post(self, request):
        try:
            nip = request.POST['nip']
            return redirect(reverse('dashboard:user_data_details', kwargs={'id':nip}))
        except Nip.DoesNotExist:
            messages.warning(request, f"NIP `{nip}` not registered.")
        return render(request, self.html_template, context=self.context)

class DataUserDetailView(View, LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'redirect_to'
    
    context = {'segment': 'user-data'}
    html_template = 'home/user-data.html'
    def get(self, request, id):
        try:
            data_nip = Nip.objects.get(nip=id)
            if data_nip:
                daily_report = ListDailyReport(nip=data_nip.nip).requests_data()
                data = json.loads(daily_report.text)
                self.context = {'reports':data, 'nip':data_nip.nip}
        except Nip.DoesNotExist:
            messages.warning(request, f"NIP `{id}` not registered.")
        except EkinerjaException as err:
            messages.warning(request, f"{err.message} Please contact admin.")
        return render(request, self.html_template, context=self.context)
    
@login_required(login_url='/login/')
def deleted_report_daily(request, id):
    html_template ='home/register_nip.html'
    resp = DeleteReportDaily(id=id).requests_data()
    messages.success(request, f"Deleted report daily item successfull.")
    return redirect(reverse('dashboard:user_data' ))

@login_required(login_url='/login/')
def deleted_all_report_daily(request, id):
    try:
        data_nip = Nip.objects.get(nip=id)
        nip = str(id)
        if data_nip:
            delete_all_file.apply_async(args=(nip,), countdown=3)
            messages.success(request, f"Deleted all report daily successfull.")
    except Nip.DoesNotExist:
        messages.warning(request, f"NIP `{id}` not registered.")
    return redirect(reverse('dashboard:user_data' ))

@login_required(login_url='/login/')
def register_nip(request):
    context = {'segment': 'register-nip'}
    html_template ='home/register_nip.html'
    if request.method == 'POST':
        number_nip = request.POST['nip']
        nip, created = Nip.objects.get_or_create(nip=number_nip)
        if not created:
            messages.warning(request, f"NIP `{nip}` already registered.")
            return redirect(reverse('dashboard:register_nip'))
        messages.success(request, f"NIP `{nip}` register successfull.")
        nip.save()
        return redirect(reverse('dashboard:register_nip'))
    return render(request,template_name=html_template, context=context)

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
