from django.db import models

class Admin(models.Model):
    admin_id =models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
