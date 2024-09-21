from django.contrib import admin
from .models import MstPdpaCategory, MstPdpaQuestion, MstPdpaAnswer, TnxPdpaResult, TnxPdpaUser, MstPdpaSubCategory, TnxResultDocument
from .forms import CustomMstPdpaQuestionForm
from django.http import HttpResponse
import csv

from django.template.response import TemplateResponse

class TnxResultDocumentInline(admin.TabularInline):
    model = TnxResultDocument
    extra = 1  # Number of empty forms to display

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

    # inlines = [TnxResultDocumentInline]
    list_display = ["user"]
    actions = ['export_as_csv']

    change_list_template = 'admin/report_list.html'

    def changelist_view(self, request, extra_context=None):
        # Get the list of products and order them by category
        all_user = TnxPdpaUser.objects.all()
        print(all_user)
        # Group products by category
        # grouped_products = {}
        # for product in products:
        #     category = product.category
        #     if category not in grouped_products:
        #         grouped_products[category] = []
        #     grouped_products[category].append(product)

        context = {
            'all_user': all_user,
        }
        return TemplateResponse(request, 'admin/report_list.html', context)

class TnxPdpaUserAdmin(admin.ModelAdmin):
    list_display = ("username", "ssh_server", "ssh_port","ssh_user", "ssh_password")


admin.site.register(TnxPdpaUser, TnxPdpaUserAdmin)

admin.site.register(MstPdpaCategory, MstPdpaCategoryAdmin)
admin.site.register(MstPdpaSubCategory, MstPdpaSubCategoryAdmin)
admin.site.register(MstPdpaQuestion, MstPdpaQuestionAdmin)
admin.site.register(MstPdpaAnswer, MstPdpaAnswerAdmin)
admin.site.register(TnxPdpaResult, TnxPdpaResultAdmin)