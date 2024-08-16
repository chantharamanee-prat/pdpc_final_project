from django.contrib import admin
from .models import MstPdpcCategory, MstPdpcQuestion, MstPdpcAnswer, TnxPdpcResult
# Register your models here.

class MstPdpcCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")

class MstPdpcQuestionAdmin(admin.ModelAdmin):
    list_display = ("category", "question", "sequence")

class MstPdpcAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer", "sequence", "score")

class TnxPdpcResultAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "answer")


admin.site.register(MstPdpcCategory, MstPdpcCategoryAdmin)
admin.site.register(MstPdpcQuestion, MstPdpcQuestionAdmin)
admin.site.register(MstPdpcAnswer, MstPdpcAnswerAdmin)
admin.site.register(TnxPdpcResult, TnxPdpcResultAdmin)