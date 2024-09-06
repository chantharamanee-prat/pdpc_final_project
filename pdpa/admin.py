from django.contrib import admin
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult, TnxPdpaUser, MstPdpaSubCategory
from .forms import CustomMstPdpaQuestionForm

from django.http import HttpResponse
import csv

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"
    

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

class TnxPdpaResultAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("user", "question", "answer")
    actions = ['export_as_csv']

class TnxPdpaUserAdmin(admin.ModelAdmin):
    list_display = ("username", "ssh_server", "ssh_port","ssh_user", "ssh_password")


class MyAdminSite(admin.AdminSite):
    site_header = 'PDPA Administration'
    site_title = 'PDPA Admin'
    index_title = 'Welcome to the PDPA Admin Panel'

    def get_app_list(self, request):
        # Override this method to change the order of models
        app_list = super().get_app_list(request)
        for app in app_list:
            if app['app_label'] == 'pdpa':  # Replace 'your_app_name' with your actual app name
                app['models'] = sorted(app['models'], key=lambda x: ['MstPdpaAnswer', 'MstPdpaCategory', 'MstPdpaSubCategory', 'MstPdpaQuestion', 'TnxPdpaResult', 'TnxPdpaUser'].index(x['object_name']))
        return app_list
    
my_admin_site = MyAdminSite(name='myadmin')

my_admin_site.register(TnxPdpaUser, TnxPdpaUserAdmin)

my_admin_site.register(MstPdpaCategory, MstPdpaCategoryAdmin)
my_admin_site.register(MstPdpaSubCategory, MstPdpaSubCategoryAdmin)
my_admin_site.register(MstPdpaQuestion, MstPdpaQuestionAdmin)
my_admin_site.register(MstPdpaAnswer, MstPdpaAnswerAdmin)
my_admin_site.register(TnxPdpaResult, TnxPdpaResultAdmin)