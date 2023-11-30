from django.db import models

# Create your models here.

class Band (models.Model):
    name = models.CharField(max_length=100)

class Reviews(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField()