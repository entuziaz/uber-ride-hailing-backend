from django.db import models

class Passenger(models.Model):
    passenger_id = models.AutoField(max_length=50, primary_key=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
