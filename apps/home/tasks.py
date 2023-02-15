
from celery import shared_task
from core.uploader import PostingDailyReport
from django.core.files.storage import default_storage

@shared_task
def upload_file(nip, file_path):
    try:
        with default_storage.open(file_path, 'rb') as f:
            PostingDailyReport(nip=nip, filename=file_path).requests_data()
        default_storage.delete(file_path)
    except Exception as e:
        upload_file.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    return 'Posting upload data to ekinerja.'