from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdpa_main, name='pdpa_main'),
    path('cat/<int:id>/question/', views.pdpa_question, name="pdpa_question"),
    path('cat/<int:id>/result/', views.pdpa_result, name="pdpa_result"),
    path('404.html', views.not_found, name="not_found")
]
