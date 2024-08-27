from django.db import models
from django.contrib.auth.models import AbstractUser
import os
# Create your models here.
class MstPdpaCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"
    
class MstPdpaSubCategory(models.Model):
    category = models.ForeignKey(MstPdpaCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"


class MstPdpaAnswer(models.Model):
    name =  models.CharField(max_length=255)
    answer = models.CharField(max_length=255)
    sequence = models.IntegerField(default=None)
    score = models.IntegerField(default=0, null=True, blank=True)
    result_text = models.TextField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}"


class MstPdpaQuestion(models.Model):
    sub_category = models.ForeignKey(MstPdpaSubCategory, on_delete=models.CASCADE)
    question = models.TextField()
    details = models.TextField()
    sequence = models.IntegerField(default=None)

    file = models.FileField(upload_to='uploads/', blank=True, null=True)

    answers = models.ManyToManyField(MstPdpaAnswer, related_name="questions")

    def __str__(self) -> str:
        return f"{self.question[:100]}"
    
    def get_category_name(self):
        return self.sub_category.category.name
    
    get_category_name.short_description = 'Category'

    def save(self, *args, **kwargs):
        if self.pk:  # Check if the instance already exists
            old_instance = MstPdpaQuestion.objects.get(pk=self.pk)
            if old_instance.file and old_instance.file != self.file:
                if os.path.isfile(old_instance.file.path):
                    os.remove(old_instance.file.path)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class TnxPdpaResult(models.Model):
    session = models.CharField(max_length=256)
    question = models.ForeignKey(MstPdpaQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(MstPdpaAnswer, on_delete=models.CASCADE)
    text_measurement = models.TextField(default=None, null=True, blank=True)


class TnxPdpaUser(AbstractUser):
    server_url = models.CharField(max_length=255)
    ssh_user = models.CharField(max_length=255)
    ssh_password = models.CharField(max_length=255)
    