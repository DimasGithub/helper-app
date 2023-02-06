# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

class Nip(models.Model):
    id = models.BigAutoField(primary_key=True)
    nip = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.nip
    class Meta:
        db_table = 'nip'
        verbose_name = 'Nip'
        verbose_name_plural = 'Nips'
