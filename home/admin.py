# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.urls import path
from . import views
from django.apps import apps
from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from .forms import CustomPdpaQuestionForm
from .models import UserProfile, PdpaCategory, PdpaQuestion, PdpaAnswer, TnxPdpaResult, PdpaSubCategory, TnxAuditLog
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

class TnxPdpaResultAdmin(admin.ModelAdmin, ExportCsvMixin):

    # inlines = [TnxResultDocumentInline]
    list_display = ["user"]
    actions = ['export_as_csv']

    change_list_template = 'admin/report_list.html'

    def changelist_view(self, request, extra_context=None):

        all_user = User.objects.all()
        context = {
            'all_user': all_user
        }
        return TemplateResponse(request, 'admin/report_list.html', context)

# Register your models here.

@admin.register(PdpaCategory)
class PdpaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "sequence")
    fields = ("name", "sequence", "icon")

@admin.register(PdpaSubCategory)
class PdpaSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sequence")

@admin.register(PdpaQuestion)
class PdpaQuestionAdmin(admin.ModelAdmin):
    form = CustomPdpaQuestionForm
    list_display = ( "question",'get_category_name',"sub_category", "sequence")
    filter_horizontal = ('answers',)
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
@admin.register(PdpaAnswer)
class PdpaAnswerAdmin(admin.ModelAdmin):
    list_display = ("name","answer", "sequence", "score")

@admin.register(TnxPdpaResult)
class TnxPdpaResultAdmin(admin.ModelAdmin, ExportCsvMixin):

    list_display = ["user"]
    actions = ['export_as_csv']

    change_list_template = 'admin/report_list.html'

    def changelist_view(self, request, extra_context=None):

        all_user = User.objects.all()
        context = {
            'all_user': all_user
        }
        return TemplateResponse(request, 'admin/report_list.html', context)


admin.site.register(UserProfile)

admin.site.register(TnxAuditLog)