from django.db import models

# Create your models here.
class MstPdpcCategory(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)

    def __str__(self) -> str:
        return f"{self.name}"

class MstPdpcQuestion(models.Model):
    category = models.ForeignKey(MstPdpcCategory, on_delete=models.CASCADE)
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

class MstPdpcAnswer(models.Model):
    answer = models.CharField(max_length=50)
    sequence = models.IntegerField(default=None)
    score = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.answer}"


class TnxPdpcResult(models.Model):
    session = models.CharField(max_length=256)
    question = models.ForeignKey(MstPdpcQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(MstPdpcAnswer, on_delete=models.CASCADE)
    text_measurement = models.TextField(default=None, null=True, blank=True)

