from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdpc_main, name='pdpc_main'),
    path('cat/<int:id>/question/', views.pdpc_question, name="pdpc_question"),
    path('cat/<int:id>/result/', views.pdpc_result, name="pdpc_result"),
    path('404.html', views.not_found, name="not_found")
]
