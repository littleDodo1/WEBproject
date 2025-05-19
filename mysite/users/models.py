import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string



# Create your models here.


class CustomUser(AbstractUser):
    email_verify = models.BooleanField(default=False)
    email_verify_token = models.CharField(max_length=64, blank=True)
    
    def generate_verify_token(self):
        self.email_verify_token = get_random_string(64)
        self.save()
        return self.email_verify_token


class Ratings(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)
    item_id = models.CharField(max_length=100)
    grade = models.PositiveSmallIntegerField()


class Reviews(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)
    item_id = models.CharField(max_length=100)
    review = models.TextField()
    review_date = models.DateField(default=datetime.date.today())
    watch_date = models.DateField(null=True)


class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)
    item_id = models.CharField(max_length=100)


class WishList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=10)
    item_id = models.CharField(max_length=100)