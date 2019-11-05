# userauth/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

from realtimechatserver import helper


class User(AbstractUser):
    """Extend functionality of user"""
    
    hash_id = models.CharField(max_length=32, default=helper.create_hash, unique=True)
    phone_number = models.CharField(max_length=15, default='1111111111')
    channel_layer = models.CharField(max_length=80, default='ch')
    channel_name = models.CharField(max_length=80, default='ch')

