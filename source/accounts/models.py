from django.db import models
from django.contrib.auth.models import User


class Activation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
