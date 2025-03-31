from django.db import models
from django.utils.translation import gettext_lazy as _
# Create your models here.
class CompanyProfile(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name        = _("Company Profile")
        verbose_name_plural = _("Company Profiles")

