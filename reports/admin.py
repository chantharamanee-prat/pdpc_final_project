from django.contrib import admin
from .models import CompanyProfile
from .proxy_models import PDPAAuditReport
from django.contrib.auth.models import User
from django.template.response import TemplateResponse


# Register your models here.

admin.site.register(CompanyProfile)

@admin.register(PDPAAuditReport)
class PDPAAuditReportAdmin(admin.ModelAdmin):

    def changelist_view(self, request, extra_context = None):
        from django.db.models import Count
        from django.db.models import F
        from home.models import PdpaCategory

        # Aggregate data for the chart
        results = PDPAAuditReport.objects.values(
            category_name = F('question__sub_category__category__name'),
            question_text = F('question__question'),
            answer_name = F('answer__name'),
            category_sequence = F('question__sub_category__category__sequence')
        ).annotate(count=Count('id'))

        # Prepare data for Chart.js
        chart_data = {}
        for result in results:
            category = result['category_name']
            question = result['question_text']
            answer = result['answer_name']
            count = result['count']
            category_sequence = result['category_sequence']

            if category not in chart_data:
                chart_data[category] = {}
                chart_data[category]['sequence'] = category_sequence
                chart_data[category]['questions'] = {}

            if question not in chart_data[category]['questions']:
                chart_data[category]['questions'][question] = {}
            chart_data[category]['questions'][question][answer] = count


        # Sort chart_data by category sequence
        sorted_chart_data = dict(sorted(chart_data.items(), key=lambda item: item[1]['sequence'] if item[1]['sequence'] is not None else float('inf')))

        # Remove sequence from sorted_chart_data
        final_chart_data = {}
        for category, data in sorted_chart_data.items():
            final_chart_data[category] = data['questions']

        context = {
            'chart_data': final_chart_data
        }
        return TemplateResponse(request, 'admin/audit_reports.html', context)

