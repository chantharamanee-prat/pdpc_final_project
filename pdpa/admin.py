from django.contrib import admin
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult
# Register your models here.

class MstPdpaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")

class MstPdpaQuestionAdmin(admin.ModelAdmin):
    list_display = ("category", "question", "sequence")

class MstPdpaAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer", "sequence", "score")

class TnxPdpaResultAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "answer")


admin.site.register(MstPdpaCategory, MstPdpaCategoryAdmin)
admin.site.register(MstPdpaQuestion, MstPdpaQuestionAdmin)
admin.site.register(MstPdpaAnswer, MstPdpaAnswerAdmin)
admin.site.register(TnxPdpaResult, TnxPdpaResultAdmin)