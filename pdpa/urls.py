from django.urls import path
from . import views

urlpatterns = [
    path('', views.pdpa_main, name='pdpa_main'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('sign-in', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('sign-out-admin', views.sign_out_admin, name='sign_out_admin'),
    path('sub-cat/<int:id>/question/', views.pdpa_question, name="pdpa_question"),
    path('sub-cat/<int:id>/result/', views.pdpa_result, name="pdpa_result"),
    path('sub-cat/<int:id>/', views.fetch_sub_cat, name="fetch_sub_cat"),
    path('file/<str:filename>', views.download_file, name='downloaded_file'),
    path("404.html", views.not_found, name="not_found")
]

