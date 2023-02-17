# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import asyncio
import aiohttp
import os
import time
import json
import tempfile
from asgiref.sync import sync_to_async
import threading
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from celery.result import AsyncResult

from django.contrib import messages
from .models import Nip, UploadFile
from core.uploader import PostingDailyReport, EkinerjaException
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.views import View
from apps.home.tasks import upload_file


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

# async def upload(request):
#     context = {'segment': 'upload-data'}
#     html_template = loader.get_template('home/upload-data.html')
#     if request.method == 'POST':
#         try:
#             nip = request.POST['nip']
#             data_nip = Nip.objects.get(nip=nip)
#             if data_nip:
#                 file = request.FILES['upload_data']
#                 PostingDailyReport(nip=data_nip.nip, filename=file).requests_data()
#                 messages.success(request, f"Upload data successfull.")
#                 return HttpResponseRedirect(reverse('dashboard:data'))
#         except Nip.DoesNotExist:
#             messages.warning(request, f"NIP `{nip}` not registered.")
#             return HttpResponseRedirect(reverse('dashboard:data'))
#         except EkinerjaException as err:
#             messages.warning(request, f"{err.message} Please contact admin.")
#             return HttpResponseRedirect(reverse('dashboard:data'))
#         except Exception as err:
#             messages.warning(request, f"{err}. Please contact admin.")
#             return HttpResponseRedirect(reverse('dashboard:data'))

#     return HttpResponse(html_template.render(context, request))

class DataView(View):
    context = {'segment': 'upload-data'}
    html_template = loader.get_template('home/upload-data.html')

    def get(self, request):
        return HttpResponse(self.html_template.render(self.context, request))

    def post(self, request):
        context = {'segment': 'upload-data'}
        html_template = loader.get_template('home/upload-data.html')
        if request.method == 'POST':
            try:
                nip = request.POST['nip']
                data_nip = Nip.objects.get(nip=nip)
                if data_nip:
                    file = request.FILES['upload_data']
                    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or not file.name.endswith('.xlsx'):
                        messages.warning(request, "File must be an .xls file.")
                        return redirect(reverse('dashboard:data'))
                    
                    fs = FileSystemStorage(base_url=os.path.join(settings.IMAGE_UPLOAD_URL,f"{time.strftime('%Y/%m/%d/')}"), location=os.path.join(settings.IMAGE_UPLOAD, f"{time.strftime('%Y/%m/%d/')}"))
                    file_save = fs.save(file.name, file)
                    file_url = fs.url(file_save)
                    obj = UploadFile.objects.create(title=file.name, file_upload=file_save, file_path=file_url, nip=data_nip)
                    obj.save()
                    file_pk = obj.id
                    upload_file.apply_async(args=(nip, file_pk), countdown=3)
                    messages.success(request, f"Upload data successfull.")
                    return redirect(reverse('dashboard:home'))
            except Nip.DoesNotExist:
                messages.warning(request, f"NIP `{nip}` not registered.")
                return redirect(reverse('dashboard:data'))
            except EkinerjaException as err:
                messages.warning(request, f"{err.message} Please contact admin.")
                return redirect(reverse('dashboard:data'))
            except Exception as err:
                messages.warning(request, f"{err}. Please contact admin.")
                return redirect(reverse('dashboard:data'))
        return render(request, self.template_name, context)

@login_required(login_url='/login/')
def register_nip(request):
    context = {'segment': 'register-nip'}
    html_template = loader.get_template('home/register_nip.html')
    if request.method == 'POST':
        number_nip = request.POST['nip']
        nip, created = Nip.objects.get_or_create(nip=number_nip)
        if not created:
            messages.warning(request, f"NIP `{nip}` already registered.")
            return redirect(reverse('dashboard:register_nip'))
        messages.success(request, f"NIP `{nip}` register successfull.")
        nip.save()
        return redirect(reverse('dashboard:register_nip'))
    return render(request,html_template, context)

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
