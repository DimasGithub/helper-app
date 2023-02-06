# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Nip
from core.uploader import PostingDailyReport
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def upload(request):
    context = {'segment': 'upload-data'}
    html_template = loader.get_template('home/forms-general2.html')
    if request.method == 'POST':
        try:
            nip = request.POST['nip']
            data_nip = Nip.objects.get(nip)
            if data_nip:
                file = request.FILES['upload_data']
                api_kinerja = PostingDailyReport(nip=data_nip.nip, filename=file)
                
                return HttpResponseRedirect(reverse('admin:index'))
        except Nip.DoesNotExist:
            return HttpResponseRedirect(reverse('admin:index')) 
    return HttpResponse(html_template.render(context, request))

@login_required(login_url='/login/')
def register_nip(request):
    context = {'segment': 'register-nip'}
    html_template = loader.get_template('home/register_nip.html')
    if request.method == 'POST':
        number_nip = request.POST['nip']
        nip, created = Nip.objects.get_or_create(nip=number_nip)
        if not created: return HttpResponseRedirect(reverse('admin:index'))
        nip.save()
        return HttpResponseRedirect(reverse('admin:index'))
    return HttpResponse(html_template.render(context, request))

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