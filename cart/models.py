from users.models import User
from django.db.models.signals import post_save
from django.db import models

class SesKey(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True)
    ses_key = models.CharField(max_length=5000, default='', blank=True)



def save_seskey(sender, **kwargs):
    if kwargs['created']:
        save_seskey = SesKey.objects.create(user=kwargs['instance'])      #may one family create 5 account but just one of them use, so we dont create session and assign ses_key here.

post_save.connect(save_seskey, sender=User)


