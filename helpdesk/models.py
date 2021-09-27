from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.authtoken.models import Token

STATUS_CHOICES = (
    ('Active', 'Active'),
    ('NotActive/Confirm', 'NotActive/Confirm'),
    ('NotActive/Reject', 'NotActive/Reject'),
    ('Review', 'Review'),
)

IMPORTANCE_CHOICES = (
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
)


class User(AbstractUser):
    last_active = models.DateTimeField(auto_now=True)


class WishList(models.Model):
    title = models.CharField(max_length=100, default='name11')
    text = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Application')
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, default='Active', max_length=100)
    importance = models.CharField(choices=IMPORTANCE_CHOICES, default='Low', max_length=100)


class Comment(models.Model):
    text = models.CharField(max_length=100)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Comment')
    created_at = models.DateTimeField(auto_now=True)
    application = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='Comment2')
    last_comment = models.BooleanField(default=False)


class TemporaryTokenModel(Token):
    last_active = models.DateTimeField(auto_now=True)
