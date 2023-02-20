
from celery import shared_task
from core.uploader import PostingDailyReport, DeleteAllData
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from .models import UploadFile

@shared_task
def upload_file(nip:str, file_path:str):
    try:
        file = get_object_or_404(UploadFile, pk=file_path)
        path = file.file_path
        file.delete()
        PostingDailyReport(nip=nip, filename=path).requests_data()
        return 'Posting upload data to ekinerja.'
    except Exception as e:
        upload_file.update_state(state='FAILURE', mezta={'error': str(e)})
        raise

@shared_task
def delete_all_file(nip:str):
    try:
        DeleteAllData(nip=nip).requests_data()
        return 'Deleted all report daily.'
    except Exception as e:
        upload_file.update_state(state='FAILURE', mezta={'error': str(e)})
        raise