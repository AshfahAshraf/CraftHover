from django.db import models

# Create your models here.
from user.models import *


class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username