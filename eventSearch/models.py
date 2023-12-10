from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Band(models.Model):
    name = models.CharField(max_length=100)
    image_url = models.URLField(max_length=200)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #Any extentions to the user model can be made here
                           
class Reviews(models.Model):
    band = models.ForeignKey(Band, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now_add=True)
