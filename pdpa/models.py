from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class MstPdpaCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"

class MstPdpaQuestion(models.Model):
    category = models.ForeignKey(MstPdpaCategory, on_delete=models.CASCADE)
    question = models.TextField()
    details = models.TextField()
    sequence = models.IntegerField(default=None)
    # result text for
    result_for_answer_1 = models.TextField(default=None, null=True, blank=True)
    result_for_answer_2 = models.TextField(default=None, null=True, blank=True)
    result_for_answer_3 = models.TextField(default=None, null=True, blank=True)

    # script for answer
    script_for_answer_1 = models.TextField(default=None, null=True, blank=True)
    script_for_answer_2 = models.TextField(default=None, null=True, blank=True)
    script_for_answer_3 = models.TextField(default=None, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.question[:100]}"

class MstPdpaAnswer(models.Model):
    answer = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)
    score = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.answer}"


class TnxPdpaResult(models.Model):
    session = models.CharField(max_length=256)
    question = models.ForeignKey(MstPdpaQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(MstPdpaAnswer, on_delete=models.CASCADE)
    text_measurement = models.TextField(default=None, null=True, blank=True)


class TnxPdpaUser(AbstractUser):
    server_url = models.CharField(max_length=255)
    ssh_user = models.CharField(max_length=255)
    ssh_password = models.CharField(max_length=255)
    