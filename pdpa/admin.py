from django.contrib import admin
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult, TnxPdpaUser, MstPdpaSubCategory
from .forms import CustomMstPdpaQuestionForm
from csvexport.actions import csvexport

# Register your models here.

class MstPdpaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")

class MstPdpaSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sequence")

class MstPdpaQuestionAdmin(admin.ModelAdmin):
    form = CustomMstPdpaQuestionForm
    list_display = ( "question",'get_category_name',"sub_category", "sequence")
    filter_horizontal = ('answers',)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class MstPdpaAnswerAdmin(admin.ModelAdmin):
    list_display = ("name","answer", "sequence", "score")

class TnxPdpaResultAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "answer")
    actions = [csvexport]

class TnxPdpaUserAdmin(admin.ModelAdmin):
    list_display = ("username", "ssh_server", "ssh_port","ssh_user", "ssh_password")

admin.site.register(TnxPdpaUser, TnxPdpaUserAdmin)

admin.site.register(MstPdpaCategory, MstPdpaCategoryAdmin)
admin.site.register(MstPdpaSubCategory, MstPdpaSubCategoryAdmin)
admin.site.register(MstPdpaQuestion, MstPdpaQuestionAdmin)
admin.site.register(MstPdpaAnswer, MstPdpaAnswerAdmin)
admin.site.register(TnxPdpaResult, TnxPdpaResultAdmin)