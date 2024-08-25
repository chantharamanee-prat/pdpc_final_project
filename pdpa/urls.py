from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdpa_main, name='pdpa_main'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('cat/<int:id>/question/', views.pdpa_question, name="pdpa_question"),
    path('cat/<int:id>/result/', views.pdpa_result, name="pdpa_result"),
]

handler404 = "pdpa.views.handler404"