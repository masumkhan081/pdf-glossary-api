from django.urls import path

from . import views

app_name = "glossary"

urlpatterns = [
    path("health/", views.health, name="health"),
]
