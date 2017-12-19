from django.db import models
from django.contrib.auth import get_user_model

UserModel = get_user_model()


class Activation(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
