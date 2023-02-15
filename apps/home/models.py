# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models

class Nip(models.Model):
    id = models.BigAutoField(primary_key=True)
    nip = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.nip
    class Meta:
        db_table = 'nip'
        verbose_name = 'Nip'
        verbose_name_plural = 'Nips'

# class UploadFile(models.Model):
#     title = models.CharField(max_length = 150)
#     file_upload = models.FileField(upload_to=None, max_length = 100)
#     file_path = models.CharField(max_length=150)
#     nip = models.OneToOneField(to=Nip, on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'uploadfile'
#         permissions= (
#             ('read-upload-file', 'can read file'),
#             ('delete-upload-file', 'can  delete file'),
#             ('edit-upload-file', 'can edit file'),
#             ('create-upload-file', 'can create file')
#         )