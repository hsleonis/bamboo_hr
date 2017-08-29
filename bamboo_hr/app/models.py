from django.db import models

class UserProfile(models.Model):
    api_key = models.CharField(max_length=200, null=False, blank=False)
    sub_domain = models.CharField(max_length=100, null=False, blank=False)
    last_download_date = models.DateField()
    category_synced = models.BooleanField(default=False)