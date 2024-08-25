from django.contrib import admin
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult, TnxPdpaUser
from django.contrib.auth.models import User

# Register your models here.

class MstPdpaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")

class MstPdpaQuestionAdmin(admin.ModelAdmin):
    list_display = ("category", "question", "sequence")

class MstPdpaAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer", "sequence", "score")

class TnxPdpaResultAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "answer")

class TnxPdpaUserAdmin(admin.ModelAdmin):
    list_display = ("username", "server_url", "ssh_user", "ssh_password")

admin.site.register(TnxPdpaUser, TnxPdpaUserAdmin)

admin.site.register(MstPdpaCategory, MstPdpaCategoryAdmin)
admin.site.register(MstPdpaQuestion, MstPdpaQuestionAdmin)
admin.site.register(MstPdpaAnswer, MstPdpaAnswerAdmin)
admin.site.register(TnxPdpaResult, TnxPdpaResultAdmin)