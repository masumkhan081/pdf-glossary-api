from django.urls import path

from . import views

app_name = "glossary"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("analyse-text/", views.analyse_text_view, name="analyse_text"),
]
