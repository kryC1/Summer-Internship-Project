from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    per_page = models.IntegerField(blank=True, null=True, default=10)

    def __str__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
       profile, created = Account.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)