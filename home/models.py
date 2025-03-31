from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from reports.models import CompanyProfile
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
# Create your models here.

class UserProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(
        CompanyProfile,
        on_delete=models.CASCADE,
        null=True,  # Allow users to not be associated with a company initially. Consider using `blank=True` in the form.
        blank=True,
        related_name='users', # Optional:  Allows you to access users belonging to a company using company.users.all()
    )
    ssh_server = models.CharField(max_length=255, null=True, blank=True)
    ssh_port = models.IntegerField(null=True, blank=True)
    ssh_user = models.CharField(max_length=255, null=True, blank=True)
    ssh_password = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name        = _("PDPA User Info")
        verbose_name_plural = _("PDPA User Info")

class PdpaCategory(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    sequence = models.IntegerField(null=True, blank=True)


    class Meta:
        verbose_name        = _("PDPA Category")
        verbose_name_plural = _("PDPA Categories")

class PdpaSubCategory(models.Model):
    category = models.ForeignKey(PdpaCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "PDPA Subcategory"  
        verbose_name_plural = "PDPA Subcategories"  


class PdpaAnswer(models.Model):
    name =  models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    sequence = models.IntegerField(default=None)
    score = models.IntegerField(default=0, null=True, blank=True)
    result_text = models.TextField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "PDPA Answer" 
        verbose_name_plural = "PDPA Answers"


class PdpaQuestion(models.Model):
    sub_category = models.ForeignKey(PdpaSubCategory, on_delete=models.CASCADE)
    question = models.TextField()
    details = models.TextField()
    sequence = models.IntegerField(default=None)
    is_request_file = models.BooleanField(default=False, null=True, blank=True)

    answers = models.ManyToManyField(PdpaAnswer, related_name="questions")

    def __str__(self) -> str:
        return f"{self.question[:100]}"
    
    class Meta:
        verbose_name = "PDPA Question" 
        verbose_name_plural = "PDPA Questions"
    
    def get_category_name(self):
        return self.sub_category.category.name
    
    get_category_name.short_description = 'Category'

class TnxPdpaResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(PdpaQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(PdpaAnswer, on_delete=models.CASCADE)
    text_measurement = models.TextField(default=None, null=True, blank=True)
    script_result = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "PDPA Audit Result" 
        verbose_name_plural = "PDPA Audit Results"

    def get_category_name(self):
        return self.question.sub_category.category.name
    
    def get_sub_category_name(self):
        return self.question.sub_category.name
    
    get_category_name.short_description = 'Category'

    get_sub_category_name.short_description = "Sub Category"


class TnxResultDocument(models.Model):
    result = models.ForeignKey(TnxPdpaResult, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TnxAuditLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now)
    action = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.SET_NULL)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    changes = models.JSONField(null=True, blank=True) # Store changes as JSON
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_path = models.CharField(max_length=255, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "PDPA Audit Log" 
        verbose_name_plural = "PDPA Audit Logs"

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} - {self.content_object}"