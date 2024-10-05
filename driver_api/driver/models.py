from django.db import models

class Driver(models.Model):
    driver_id = models.CharField(max_length=50, primary_key=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
