from django.db import models
from django.contrib.auth.models import AbstractUser
import os

class MstPdpaCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"
    class Meta:
        verbose_name = "PDPA Category"  # Singular name
        verbose_name_plural = "PDPA Categories"  # Plural name
    
class MstPdpaSubCategory(models.Model):
    category = models.ForeignKey(MstPdpaCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "PDPA Subcategory"  # Singular name
        verbose_name_plural = "PDPA Subcategories"  # Plural name


class MstPdpaAnswer(models.Model):
    name =  models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    sequence = models.IntegerField(default=None)
    score = models.IntegerField(default=0, null=True, blank=True)
    result_text = models.TextField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"
    
    class Meta:
        verbose_name = "PDPA Answer"  # Singular name
        verbose_name_plural = "PDPA Answers"  # Plural name




class MstPdpaQuestion(models.Model):
    sub_category = models.ForeignKey(MstPdpaSubCategory, on_delete=models.CASCADE)
    question = models.TextField()
    details = models.TextField()
    sequence = models.IntegerField(default=None)
    is_request_file = models.BooleanField(default=False, null=True, blank=True)

    answers = models.ManyToManyField(MstPdpaAnswer, related_name="questions")

    def __str__(self) -> str:
        return f"{self.question[:100]}"
    
    class Meta:
        verbose_name = "PDPA Question"  # Singular name
        verbose_name_plural = "PDPA Questions"  # Plural name
    
    def get_category_name(self):
        return self.sub_category.category.name
    
    get_category_name.short_description = 'Category'

class TnxPdpaUser(AbstractUser):
    ssh_server = models.CharField(max_length=255)
    ssh_port = models.IntegerField(default=22)
    ssh_user = models.CharField(max_length=255)
    ssh_password = models.CharField(max_length=255)

class TnxPdpaResult(models.Model):
    user = models.ForeignKey(TnxPdpaUser, on_delete=models.CASCADE)
    question = models.ForeignKey(MstPdpaQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(MstPdpaAnswer, on_delete=models.CASCADE)
    text_measurement = models.TextField(default=None, null=True, blank=True)
    script_result = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "Transaction PDPA Result"  # Singular name
        verbose_name_plural = "Transaction PDPA Results"  # Plural name

class TnxResultDocument(models.Model):
    result = models.ForeignKey(TnxPdpaResult, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

